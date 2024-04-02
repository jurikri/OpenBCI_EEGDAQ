# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 14:38:53 2024

@author: PC
"""

import subprocess
import os

# 경로 변경 (프로젝트 폴더로 이동)
os.chdir('C:/mscode/test')

# 변경된 모든 파일 스테이지에 추가
subprocess.run(['git', 'add', '.'], check=True)

# 변경사항 커밋
commit_message = "Update files"
subprocess.run(['git', 'commit', '-m', commit_message], check=True)

# 변경사항 원격 저장소에 푸시
subprocess.run(['git', 'push'], check=True)

#%%
import subprocess
import os

# 경로 변경 (프로젝트 폴더로 이동)
os.chdir('C:/mscode/test')

# 최신 변경사항 다운로드 및 업데이트
try:
    result = subprocess.run(['git', 'pull'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("업데이트 성공:\n", result.stdout.decode())
except subprocess.CalledProcessError as e:
    print("업데이트 실패:\n", e.stderr.decode())

