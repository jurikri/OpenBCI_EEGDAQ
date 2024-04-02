# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 15:00:10 2024

@author: PC
"""

import os
import glob
import pickle
import matplotlib.pyplot as plt
import sys;
import numpy as np
sys.path.append(r'C:\mscode\test\backend')
import VNS_PPG_def
# 지정된 경로에 있는 모든 .pkl 파일들을 리스트업
data_directory = "C:\\mscode\\test\\data"
pkl_files = glob.glob(os.path.join(data_directory, "*.pkl"))

# 로드된 데이터를 저장할 리스트
loaded_data = []

# 각 .pkl 파일을 순차적으로 로드
for file_path in pkl_files:
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
        loaded_data.append(data)
    print(f"Loaded data from {file_path}")

# 로드된 데이터 사용 예
# 여기서는 로드된 각 데이터 세트의 길이를 출력합니다.
for i, data in enumerate(loaded_data):
    print(f"Dataset {i+1}: {len(data)} entries")
    

#%%

i = 0
SR = 250

for i in range(len(loaded_data)):

    # plt.plot(loaded_data[i][2])
    
    # len(loaded_data[i][0])
    # len(loaded_data[i][2])
    
    ppg_data = np.array(loaded_data[i][2])
    
    print(i, len(ppg_data)/SR)
    
    SDNN, RMSSD, pNN50, BPM, peaks = VNS_PPG_def.msmain(SR=SR, \
                        ppg_data=ppg_data)
    
    print(i)
    print(f"{'SDNN':<5}: {SDNN:.2f}")
    print(f"{'RMSSD':<5}: {RMSSD:.2f}")
    print(f"{'pNN50':<5}: {pNN50:.2f}")
    print(f"{'BPM':<5}: {BPM:.2f}")


