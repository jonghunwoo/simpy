import os
import random
import urllib.request
import xlrd
import csv
import pandas as pd
import functools
import simpy
from SimComponents_rev import Source, Sink, Process, Monitor, RandomBrancher

################
# Data loading #
################

# ./data 폴더에 해당 파일이 없으면 실행
if not os.path.isfile('./data/PBS_assy_sequence_gen_000.csv'):
    #urlretrieve를 이용하여 파일에 직접 저장하는 코드
    url = "https://raw.githubusercontent.com/jonghunwoo/public/master/PBS_assy_sequence.xlsx"
    filename = "./data/PBS_assy_sequence.xlsx"
    urllib.request.urlretrieve(url, filename)

    # Excel 파일을 csv로 변환하는 함수 정의
    def csv_from_excel(excel_name, file_name, sheet_name):
        workbook = xlrd.open_workbook(excel_name)
        worksheet = workbook.sheet_by_name(sheet_name)
        csv_file = open(file_name, 'w')
        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        for row_num in range(worksheet.nrows):
            writer.writerow(worksheet.row_values(row_num))

        csv_file.close()

    csv_from_excel('./data/PBS_assy_sequence.xlsx', './data/PBS_assy_sequence_gen_000.csv', 'gen_000')
    csv_from_excel('./data/PBS_assy_sequence.xlsx', './data/PBS_assy_sequence_gen_003.csv', 'gen_003')
    csv_from_excel('./data/PBS_assy_sequence.xlsx', './data/PBS_assy_sequence_gen_fin.csv', 'gen_fin')


# csv 파일 pandas 객체 생성
data1 = pd.read_csv('./data/PBS_assy_sequence_gen_000.csv')
data2 = pd.read_csv('./data/PBS_assy_sequence_gen_003.csv')
data3 = pd.read_csv('./data/PBS_assy_sequence_gen_fin.csv')

df1 = data1[["product", "plate_weld","saw_front","turn_over", "saw_back", "longi_weld", "unit_assy", "sub_assy"]]
df2 = data2[["product", "plate_weld","saw_front","turn_over", "saw_back", "longi_weld", "unit_assy", "sub_assy"]]
df3 = data3[["product", "plate_weld","saw_front","turn_over", "saw_back", "longi_weld", "unit_assy", "sub_assy"]]

##############
# Simulation #
##############

random.seed(42)
adist = functools.partial(random.randrange,3,7)
samp_dist = functools.partial(random.expovariate, 1)

RUN_TIME = 10000

# Create the SimPy environment
env = simpy.Environment()

Source = Source(env, "Source", adist, df1)
Sink = Sink(env, 'Sink', debug=False, rec_arrivals=True)

Process1 = Process(env, 'Process1', qlimit=5, limit_bytes=False)
Process2 = Process(env, 'Process2', qlimit=5, limit_bytes=False)
Process3 = Process(env, 'Process3', qlimit=5, limit_bytes=False)
Process4 = Process(env, 'Process4', qlimit=5, limit_bytes=False)
Process5 = Process(env, 'Process5', qlimit=5, limit_bytes=False)