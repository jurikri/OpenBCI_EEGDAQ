# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 10:32:17 2024

@author: PC
"""

import numpy as np
import matplotlib.pyplot as plt


eeg_data = np.load(r'C:\\mscode\test\eeg_data.npy')
print(eeg_data.shape)

plt.plot(eeg_data[0,:])
plt.plot(eeg_data[1,:])
plt.plot(eeg_data[2,:])



















