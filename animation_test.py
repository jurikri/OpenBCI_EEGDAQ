# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 10:11:51 2024

@author: PC
"""

if False:
    from pyOpenBCI import OpenBCICyton
    
    def callback(sample):
        print(sample.channels_data)
    
    board = OpenBCICyton(port='COM4')
    board.start_stream(callback)
    board.write_command('b')
    
    #%%
    
    import matplotlib.pyplot as plt
    from pyOpenBCI import OpenBCICyton
    import time
    
    # OpenBCI 보드 초기화
    # board = OpenBCICyton(port='COM4')
    
    # 플롯 설정
    plt.ion()  # 대화형 모드 활성화
    figure, ax = plt.subplots()
    line, = ax.plot([], [])  # 초기 라인 객체 생성
    ax.set_xlim(0, 100)  # x축 범위 설정
    ax.set_ylim(-1000, 1000)  # y축 범위 설정 (3번째 채널의 예상 값 범위에 맞춤)
    
    x_data = []
    y_data = []
    
    # 콜백 함수 정의
    def callback(sample):
        y = sample.channels_data[2]  # 3번째 채널 값
        y_data.append(y)
        x_data.append(len(y_data))  # 간단한 x 값 (샘플 번호)
    
        # x_data와 y_data가 너무 길어지면 처음부터 다시 시작
        if len(x_data) > 100:
            x_data.pop(0)
            y_data.pop(0)
        
        line.set_data(x_data, y_data)
        ax.draw_artist(ax.patch)
        ax.draw_artist(line)
        figure.canvas.flush_events()
        time.sleep(0.1)
    
    # 스트리밍 시작
    board.start_stream(callback)
    
    # 참고: 이 코드는 스크립트가 실행 중인 동안 계속 데이터를 플로팅합니다.
    # 스트림을 중단하려면 프로그램을 명시적으로 중지해야 합니다.
    #%%
    
# def msmain2():
#     import numpy as np
#     import matplotlib.pyplot as plt
#     from matplotlib.animation import FuncAnimation
#     from pyOpenBCI import OpenBCICyton
    
#     # OpenBCI 보드 초기화
#     board = OpenBCICyton(port='COM4')
    
#     # 플롯을 위한 데이터 버퍼 초기화
#     data_buffer = np.zeros(50)  # 예: 최근 50개의 샘플 저장
    
#     # 콜백 함수: 새로운 샘플이 도착할 때마다 호출됩니다.
#     def callback(sample):
#         global data_buffer
#         # 3번째 채널의 값을 버퍼에 추가합니다. 채널 인덱스는 0부터 시작하므로 2를 사용합니다.
#         data_buffer = np.roll(data_buffer, -1)
#         data_buffer[-1] = sample.channels_data[2]
    
#     # Matplotlib 플롯 설정
#     fig, ax = plt.subplots()
#     x = np.arange(len(data_buffer))
#     line, = ax.plot(x, data_buffer)
#     ax.set_ylim(-500, 500)  # y축 범위 설정
    
#     # 업데이트 함수: 각 프레임에서 호출되어 플롯을 업데이트합니다.
#     def update(frame):
#         line.set_ydata(data_buffer)
#         return line,
    
    
#     ani = FuncAnimation(fig, update, blit=True, interval=100) # 애니메이션 설정
#     board.start_stream(callback) # OpenBCI 데이터 스트리밍 시작
#     plt.show() # 플롯 보여주기


# if __name__ == "__main__":
#     # msmain()
#     msmain2()

# #%%
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation
# from pyOpenBCI import OpenBCICyton

# class OpenBCIPlotter:
#     def __init__(self, port='COM4', num_samples=100):
#         self.board = OpenBCICyton(port=port)
#         self.num_samples = num_samples

#     def callback(self, sample):
#         # 3번째 채널의 값을 버퍼에 추가합니다.
#         self.data_buffer = np.roll(self.data_buffer, -1)
#         self.data_buffer[-1] = sample.channels_data[2]
#         print(sample.channels_data[2])

#     def update(self, frame):
#         line.set_ydata(self.data_buffer)
#         return line,

#     def start(self):
#         # Matplotlib 플롯 설정
#         fig, ax = plt.subplots()
#         x = np.arange(len(self.data_buffer))
#         print(x, self.data_buffer)
#         global line
#         line, = ax.plot(x, self.data_buffer)
#         ax.set_ylim(-500, 500)  # y축 범위 설정
        
#         ani = FuncAnimation(fig, self.update, init_func=init, blit=True, save_count=100)

#         self.board.start_stream(self.callback) # OpenBCI 데이터 스트리밍 시작 
#         plt.show() # 플롯 보여주기

# def msmain2():
#     plotter = OpenBCIPlotter()
#     plotter.start()

# if __name__ == "__main__":
#     msmain2()


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

    # def update(self, frame):
    #     self.line.set_ydata(self.data_buffer)
    #     return self.line,
    
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










