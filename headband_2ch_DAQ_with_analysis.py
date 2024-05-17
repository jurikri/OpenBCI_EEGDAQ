# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 16:06:40 2024

@author: PC
"""

#%%
if False:
    import subprocess
    import pkg_resources
    
    def install_package(package_name):
        # 패키지가 이미 설치되어 있는지 확인
        installed_packages = {pkg.key for pkg in pkg_resources.working_set}
        if package_name not in installed_packages:
            # 패키지가 설치되어 있지 않을 경우 설치
            subprocess.check_call(["python", "-m", "pip", "install", package_name])
            print(f"{package_name} has been installed.")
        else:
            # 패키지가 이미 설치되어 있음
            print(f"{package_name} is already installed.")
    
    # 패키지 이름 설정
    package_names = ['pyOpenBCI', 'matplotlib', 'numpy', 'xmltodict', 'pyserial', 'requests', 'pynput', 'pyqtgraph', 'pyqt5']
    for package_name in package_names:
        install_package(package_name)

#%%

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from pyOpenBCI import OpenBCICyton
import multiprocessing
import time
import os
from datetime import datetime
import pickle
import queue

class CustomCalculationPlot:
    def __init__(self, queue, num_samples=50, update_interval=25):
        self.queue = queue
        self.num_samples = num_samples
        self.update_interval = update_interval
        self.data = np.zeros(self.num_samples)

        self.app = QtWidgets.QApplication([])
        self.win = pg.GraphicsLayoutWidget(show=True, title="Custom Calculation Plot")
        self.win.resize(1000, 600)
        self.win.setWindowTitle('Custom Calculation Plot')

        self.plot = self.win.addPlot(title="Custom Calculation")
        self.curve = self.plot.plot()

        self.timer = QtCore.QTimer()  # 타이머 초기화
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(int(1000 / self.update_interval))  # 업데이트 간격 설정

    def update_plot(self):
        try:
            custom_calculation = self.queue.get_nowait()
            # custom_calculation이 1x50 형태로 가정
            self.data = custom_calculation
            self.curve.setData(self.data)
        except queue.Empty:
            pass

    def start(self):
        QtWidgets.QApplication.instance().exec_()


def data_collection(queue):
    callback_count = 0
    full_data = []
    start_time = None
    save_interval = 5
    last_save_time = time.time()

    def callback(sample):
        nonlocal callback_count, start_time, last_save_time
        if start_time is None:
            start_time = time.time()

        callback_count += 1

        current_time = time.time()
        if current_time - start_time >= 1.0:
            print(f"FPS: {callback_count}")
            callback_count = 0
            start_time = current_time

        data = [sample.channels_data[channel] for channel in range(8)] + [current_time]
        full_data.append(data)
        queue.put(data)
        
        if False:
            if current_time - last_save_time >= save_interval:
                filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.pkl")
                filename = os.path.join(current_path, 'data', filename)
                with open(filename, 'wb') as file:
                    pickle.dump(full_data, file)
                    print(f"Data saved to {filename}")
                    full_data.clear()
                last_save_time = current_time

    board = OpenBCICyton(port='COM4', daisy=False)
    board.start_stream(callback)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        board.stop_stream()
        print("Data collection finished. Exiting program.")


import numpy as np
# 가중치 불러오기 함수
def load_weights(filepath):
    weights = np.load(filepath)
    return weights
# 가중치 불러오기
weights = load_weights(r'C:\mscode\test\seoul_challenge' + '\\my_model.npz')

def manual_prediction(input_data, weights):
    # 첫 번째 레이어 수동 계산 (WeightedAverageLayer)
    custom_weights = weights['layer_0_weight_0']  # (50,)
    out1 = input_data * custom_weights
    
    dense_weights_1 = weights['layer_1_weight_0']  # shape: (50, 16)
    dense_biases_1 = weights['layer_1_weight_1']  # shape: (16,)
    out1 = out1[np.newaxis, :]  # (1, 50)
    manual_result = np.dot(out1, dense_weights_1) + dense_biases_1  # (1, 16)

    # 두 번째 Dense 레이어 수동 계산 (Dense Layer 2)
    dense_weights_2 = weights['layer_2_weight_0']  # shape: (16, 2)
    dense_biases_2 = weights['layer_2_weight_1']  # shape: (2,)
    manual_result = np.dot(manual_result, dense_weights_2) + dense_biases_2  # (batch_size, 2)
    manual_result = np.exp(manual_result) / np.sum(np.exp(manual_result), axis=1, keepdims=True)  # Softmax 적용

    return manual_result

def data_slicing(queue, plot_queue, weights=weights):
    from scipy.fft import fft, fftfreq
    slice_interval = 1  # 슬라이싱 간격 (초)
    sample_rate = 250  # 샘플레이트, 예를 들어 250Hz
    window_size = 1200  # 분석할 데이터 포인트 수, 예: 1200
    DATA_LENGTH = window_size
    data_buffer = []
    
    baseline = None
    baseline_interval = 60  # Baseline을 계산할 간격 (초)
    last_baseline_update = time.time()
    ftmp_list = []
    
    baselin_ftmp = []

    while True:
        time.sleep(slice_interval)
        try:
            while not queue.empty():
                data_buffer.append(queue.get_nowait())

            if len(data_buffer) >= window_size:
                # 최신 1200개의 데이터 포인트를 사용하여 분석
                latest_data = data_buffer[-window_size:]
                X = np.array(latest_data)
                
                print('X.shape', X.shape)
                
                beta1, beta2 = 1, 1
                eeg_data = (X[:, 0] / np.mean(X[:, 0]) * beta1) \
                    + (X[:, 1] / np.mean(X[:, 1]) * beta2)
                
                eeg_fft = fft(eeg_data)
                frequencies = fftfreq(DATA_LENGTH, 1/DATA_LENGTH)
                
                magnitude_spectrum = np.abs(eeg_fft)
                power_spectrum = magnitude_spectrum ** 2
         
                mask = frequencies > 0  # Remove negative frequencies if needed
                mask &= frequencies <= 50  # Limit to 50 Hz
                
                filtered_frequencies = frequencies[mask]
                filtered_power_spectrum = power_spectrum[mask]
                ftmp = filtered_power_spectrum / np.mean(filtered_power_spectrum)
                
                
                if baseline is None: 
                    baselin_ftmp.append(ftmp)
                    print(len(baselin_ftmp))
                
                if len(baselin_ftmp) > 10:
                    baseline = np.mean(np.array(baselin_ftmp)[5:], axis=0)
                    print('baseline calculated')
                    
                if not(baseline is None):
                    
                    # Baseline 이후 ftmp 데이터 처리
                    custom_calculation = 10 * np.log10(ftmp / baseline)
                    plot_queue.put(custom_calculation)  # Plot에 전달하기 위해 평균값을 사용
                    
                    input_data = np.reshape(custom_calculation, (50))
                    
                    manual_result = manual_prediction(input_data, weights)[0][1]
                    print("Manual prediction result:", manual_result)
                
                # print(custom_calculation.shape)
                
                # 필요에 따라 데이터 버퍼를 슬라이싱하여 메모리 관리
                data_buffer = data_buffer[-window_size:]
        except:
            continue

if __name__ == "__main__":
    current_path = os.getcwd()
    data_queue = multiprocessing.Queue()
    plot_queue = multiprocessing.Queue()  # 플롯을 위한 큐 추가
    data_process = multiprocessing.Process(target=data_collection, args=(data_queue,))
    slicing_process = multiprocessing.Process(target=data_slicing, args=(data_queue, plot_queue))

    data_process.start()
    slicing_process.start()

    plot = CustomCalculationPlot(plot_queue)
    plot.start()

    data_process.join()
    slicing_process.terminate()




