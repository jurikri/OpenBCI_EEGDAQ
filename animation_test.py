# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 10:11:51 2024

@author: PC
"""

#%%

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pyOpenBCI import OpenBCICyton

class OpenBCIPlotter:
    def __init__(self, port='COM4', num_samples=100):
        self.board = OpenBCICyton(port=port)
        self.num_samples = num_samples
        self.data_buffer = np.zeros(num_samples)  # 데이터 버퍼 초기화

    def callback(self, sample):
        # 3번째 채널의 값을 버퍼에 추가합니다.
        self.data_buffer = np.roll(self.data_buffer, -1)
        self.data_buffer[-1] = sample.channels_data[2]

    def update(self, frame):
        self.line.set_ydata(self.data_buffer)
        print(self.data_buffer)
        return (self.line,)  # 이 부분이 변경되었습니다.

    def start(self):
        # Matplotlib 플롯 설정
        fig, ax = plt.subplots()
        ax.set_ylim(-500, 500)  # y축 범위 설정
        
        # line 객체를 클래스의 속성으로 관리
        self.line, = ax.plot(np.arange(self.num_samples), self.data_buffer)
        
        # 애니메이션 설정
        ani = FuncAnimation(fig, self.update, init_func=lambda: self.line, blit=True, interval=40)

        # OpenBCI 데이터 스트리밍 시작
        self.board.start_stream(self.callback)

        plt.show()  # 플롯 보여주기

def main():
    plotter = OpenBCIPlotter(port="COM4", num_samples=100)  # COM 포트에 따라 변경
    plotter.start()

if __name__ == "__main__":
    main()










