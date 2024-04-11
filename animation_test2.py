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
    package_names = ['pyOpenBCI', 'matplotlib', 'numpy', 'xmltodict', 'pyserial', 'requests']
    for package_name in package_names:
        install_package(package_name)

#%%
if False:
    import numpy as np
    import matplotlib.pyplot as plt
    from pyOpenBCI import OpenBCICyton
    import pickle
    from datetime import datetime
    import sys
    
    plt.ion()
    
    class MultiChannelEEGPlot:
        def __init__(self, channels=[0, 1, 2], num_samples=100, update_interval=10):
            self.channels = channels  # 플로팅할 채널 리스트
            self.num_samples = num_samples
            self.update_interval = update_interval
            self.data = {channel: np.zeros(self.num_samples) for channel in channels}  # 플로팅 데이터
            self.full_data = {channel: [] for channel in channels}  # 1분 동안의 모든 데이터를 저장할 리스트
            self.fig, self.axs = plt.subplots(len(channels), 1, figsize=(10, 7))
            self.callback_count = 0  # callback 함수 호출 횟수를 저장할 속성 추가
    
    
            # lines 속성 초기화
            self.lines = {}
            for channel, ax in zip(channels, self.axs):
                # 각 채널에 대한 라인 객체를 생성하고 lines 딕셔너리에 추가
                line, = ax.plot([], [], 'r-')  # 콤마는 unpacking을 의미, Line2D 객체 하나만 반환
                self.lines[channel] = line
    
                ax.set_xlim(0, self.num_samples - 1)
                ax.set_ylim(-8000, 8000)
    
            self.samples_collected = 0  # 여기에서 속성 초기화
            self.start_time = None # 기록 시작 시간
            self.first_data_received = False  # 첫 데이터 수신 여부 플래그
            self.duration = 60  # 데이터 기록 지속 시간(초 단위)
    
        def callback(self, sample):
            self.callback_count += 1  # callback 함수가 호출될 때마다 카운트 증가
            
            if not self.first_data_received:
                self.start_time = datetime.now()  # 첫 데이터 수신 시점을 시작 시간으로 설정
                self.first_data_received = True  # 첫 데이터 수신 플래그 업데이트
               
            for channel in self.channels:
                self.data[channel] = np.roll(self.data[channel], -1)
                self.data[channel][-1] = sample.channels_data[channel]
                self.full_data[channel].append(sample.channels_data[channel])  # 모든 데이터 누적
                
            print(self.callback_count)
                
            self.samples_collected += 1
            if self.samples_collected >= self.update_interval:
                self.update_plot()
                self.samples_collected = 0
                
        def save_data(self):
            # 현재 시간 정보를 포함한 파일 이름 생성
            filename = datetime.now().strftime("C:\\mscode\\test\\data\\%Y-%m-%d_%H-%M-%S.pkl")
            with open(filename, 'wb') as file:
                # 누적된 모든 데이터를 pickle 형식으로 저장
                pickle.dump(self.full_data, file)
            print(f"Data saved to {filename}")
            sys.exit("Data collection and saving complete. Exiting program.")
    
        def start(self):
            self.board = OpenBCICyton(port='COM3', daisy=False)
            self.board.start_stream(self.callback)
            
        # MultiChannelEEGPlot 클래스 초기화 메소드(__init__)에 추가
        # update_plot 메소드 수정
        def update_plot(self):
            for channel in self.channels:
                self.lines[channel].set_data(np.arange(self.num_samples), self.data[channel])
            # 남은 시간 계산
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
            remaining_time = max(self.duration - elapsed_time, 0)
            # 남은 시간 표시 (첫 번째 그래프의 타이틀로 사용)
            if self.axs.size > 0:
                self.axs[0].set_title(f"Remaining Time: {remaining_time:.2f} seconds")
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            # 지정된 시간이 끝났을 경우 데이터 저장
            if remaining_time <= 0:
                self.save_data()
    
    if True:
        if __name__ == "__main__":
            eeg_plot = MultiChannelEEGPlot(channels=[0, 1, 2], num_samples=2500, update_interval=10)
            eeg_plot.start()
            while True:
                plt.pause(0.001)


#%%

# FPS 확인코드
if False:
    from pyOpenBCI import OpenBCICyton
    import time
    import threading
    
    class SimpleEEGCounter:
        def __init__(self):
            self.callback_count = 0  # callback 함수 호출 횟수를 저장할 속성
            self.running = True  # 스트림이 실행 중인지 상태를 표시하는 플래그
    
        def callback(self, sample):
            self.callback_count += 1  # callback 함수가 호출될 때마다 카운트 증가
    
        def print_fps(self):
            while self.running:
                # 현재 카운트를 저장하고 리셋
                current_count = self.callback_count
                self.callback_count = 0
                print(f"FPS: {current_count}")
                time.sleep(1)  # 1초 대기
    
        def start(self, duration=60):
            # FPS 출력을 위한 스레드 시작
            fps_thread = threading.Thread(target=self.print_fps)
            fps_thread.start()
    
            # OpenBCICyton 객체 초기화 및 데이터 스트림 시작
            self.board = OpenBCICyton(port='COM4', daisy=False)
            self.board.start_stream(self.callback)
    
            # 지정된 시간(초) 동안 실행
            time.sleep(duration)
    
            # 스트림 중지 및 스레드 종료
            self.running = False
            self.board.stop_stream()
            fps_thread.join()  # FPS 스레드가 종료될 때까지 대기
    
            print("Data collection complete.")
    
    if __name__ == "__main__":
        eeg_counter = SimpleEEGCounter()
        eeg_counter.start()  # 기본적으로 60초 동안 실행

#%%

import numpy as np
import matplotlib.pyplot as plt
from pyOpenBCI import OpenBCICyton
import pickle
from datetime import datetime
import sys
import multiprocessing
import time
import queue

plt.ion()

class MultiChannelEEGPlot:
    def __init__(self, queue, channels=[0, 1, 2], num_samples=2500, update_interval=25):
        self.queue = queue
        self.channels = channels
        self.num_samples = num_samples
        self.update_interval = update_interval
        self.data = {channel: np.zeros(self.num_samples) for channel in channels}
        self.fig, self.axs = plt.subplots(len(channels), 1, figsize=(10, 7))
        self.lines = {channel: ax.plot([], [], 'r-')[0] for channel, ax in zip(channels, self.axs)}
        self.start_time = time.time()  # 그래프 업데이트 시작 시간 기록
        self.queue = queue
        self.is_running = True  # 여기에서 is_running 속성을 정의
        
        self.update_counter = 0  # 이 카운터로 업데이트 간격을 조절

        for ax in self.axs:
            ax.set_xlim(0, self.num_samples - 1)
            ax.set_ylim(-8000, 8000)

    def update_plot(self):
        while self.is_running:
            try:
                data = self.queue.get_nowait()  # 큐에서 데이터 가져오기
                # 데이터를 내부 버퍼에 추가하는 코드
                for channel in self.channels:
                    self.data[channel] = np.roll(self.data[channel], -1)
                    self.data[channel][-1] = data[channel]

                self.update_counter += 1
                
                if self.update_counter >= self.update_interval:
                    for channel in self.channels:
                        self.lines[channel].set_data(np.arange(self.num_samples), self.data[channel])
                    # 남은 시간 계산 및 표시 코드...
                    self.fig.canvas.draw()
                    self.fig.canvas.flush_events()
                    self.update_counter = 0  # 카운터 리셋

            except queue.Empty:
                time.sleep(0.01)  # 큐가 비어 있으면 잠시 대기
                continue
            
    def stop(self):
        self.is_running = False

def data_collection(queue):
    callback_count = 0  # callback 함수 호출 횟수를 저장할 변수
    full_data = []  # 모든 데이터를 누적할 리스트
    start_time = None  # 첫 callback 호출 시간

    def callback(sample):
        nonlocal callback_count, start_time
        if start_time is None:
            start_time = time.time()  # 첫 callback 시간 기록

        callback_count += 1

        # FPS 계산 및 출력
        current_time = time.time()
        if current_time - start_time >= 1.0:
            print(f"FPS: {callback_count}")
            callback_count = 0
            start_time = current_time

        # 샘플 데이터를 리스트로 변환하여 누적
        data = [sample.channels_data[channel] for channel in range(8)]
        full_data.append(data)  # 누적 데이터에 추가
        queue.put(data)  # GUI 업데이트를 위해 큐에 데이터 추가

    board = OpenBCICyton(port='COM4', daisy=False)
    board.start_stream(callback)

    # 60초 동안 데이터 수집 실행
    time.sleep(60)
    board.stop_stream()  # 스트림 중지

    # 데이터 저장
    filename = datetime.now().strftime("C:\\mscode\\test\\data\\%Y-%m-%d_%H-%M-%S.pkl")
    with open(filename, 'wb') as file:
        pickle.dump(full_data, file)
    print(f"Data saved to {filename}")

    print("Data collection finished. Exiting program.")
    sys.exit()  # 프로그램 종료


if __name__ == "__main__":
    data_queue = multiprocessing.Queue()
    data_process = multiprocessing.Process(target=data_collection, args=(data_queue,))

    data_process.start()

    plot = MultiChannelEEGPlot(data_queue)
    try:
        plot.update_plot()
    finally:
        plot.stop()
        data_process.join()


# if __name__ == "__main__":
#     data_queue = multiprocessing.Queue()
#     data_process = multiprocessing.Process(target=data_collection, args=(data_queue,))
#     data_process.start()
#     data_process.join()  # 데이터 수집 프로세스가 완료될 때까지 기다림

























































