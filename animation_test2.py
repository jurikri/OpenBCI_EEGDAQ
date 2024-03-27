# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 16:06:40 2024

@author: PC
"""

#%%
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
package_names = ['pyOpenBCI', 'matplotlib', 'numpy', 'xmltodict']
for package_name in package_names:
    install_package(package_name)

#%%

import numpy as np
import matplotlib.pyplot as plt
from pyOpenBCI import OpenBCICyton

plt.ion()

class MultiChannelEEGPlot:
    def __init__(self, channels=[0, 1, 2], num_samples=100, update_interval=10):
        self.channels = channels  # 플로팅할 채널 리스트
        self.num_samples = num_samples
        self.update_interval = update_interval
        self.data = {channel: np.zeros(self.num_samples) for channel in channels}
        self.fig, self.axs = plt.subplots(len(channels), 1, figsize=(10, 7))  # 1컬럼 x 3행 구성
        self.lines = {channel: ax.plot([], [], 'r-')[0] for channel, ax in zip(channels, self.axs)}
        for ax in self.axs:
            ax.set_xlim(0, self.num_samples - 1)
            ax.set_ylim(-8000, 8000)
        self.samples_collected = 0

    def update_plot(self):
        for channel in self.channels:
            self.lines[channel].set_data(np.arange(self.num_samples), self.data[channel])
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def callback(self, sample):
        for channel in self.channels:
            self.data[channel] = np.roll(self.data[channel], -1)
            self.data[channel][-1] = sample.channels_data[channel]
        self.samples_collected += 1
        if self.samples_collected >= self.update_interval:
            self.update_plot()
            self.samples_collected = 0

    def start(self):
        self.board = OpenBCICyton(port='COM4', daisy=False)
        self.board.start_stream(self.callback)

if __name__ == "__main__":
    eeg_plot = MultiChannelEEGPlot(channels=[0, 1, 2], num_samples=2500, update_interval=10)
    eeg_plot.start()
    while True:
        plt.pause(0.001)






