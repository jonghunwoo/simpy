import os
import random
import urllib.request
import xlrd
import csv
import pandas as pd
import functools
import simpy
from SimComponents_rev import Source, Source_with_dataframe, Sink, Process, Monitor, RandomBrancher

""" Data loading
    request raw excel file from github of jonghunwoo
    then, change the format from excel to csv
    Data frame object of product data is generated from csv file
"""

# ./data 폴더에 해당 파일이 없으면 실행
if not os.path.isfile('./data/PBS_assy_sequence_gen_000.csv'):
    url = "https://raw.githubusercontent.com/jonghunwoo/public/master/PBS_assy_sequence.xlsx"
    filename = "./data/PBS_assy_sequence.xlsx"
    urllib.request.urlretrieve(url, filename)

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

""" Simulation
    Dataframe with product data is passed to Source.
    Then, source create product with interval time of defined adist function.
    For this purpose, Source_with_dataframe is defined based on original Source.
"""

random.seed(42)
adist = functools.partial(random.randrange,3,7)
samp_dist = functools.partial(random.expovariate, 1)
proc_time = functools.partial(random.normalvariate,5,1)

RUN_TIME = 10000

env = simpy.Environment()

Source = Source_with_dataframe(env, "Source", adist, df1)
Sink = Sink(env, 'Sink', debug=False, rec_arrivals=True)

Process1 = Process(env, 'Process1', proc_time, qlimit=1, limit_bytes=False)
Process2 = Process(env, 'Process2', proc_time, qlimit=1, limit_bytes=False)
Process3 = Process(env, 'Process3', proc_time, qlimit=1, limit_bytes=False)
Process4 = Process(env, 'Process4', proc_time, qlimit=1, limit_bytes=False)
Process5 = Process(env, 'Process5', proc_time, qlimit=1, limit_bytes=False)
Process6 = Process(env, 'Process6', proc_time, qlimit=1, limit_bytes=False)
Process7 = Process(env, 'Process7', proc_time, qlimit=1, limit_bytes=False)

# Using a PortMonitor to track each status over time
Monitor1 = Monitor(env, Process1, samp_dist)
Monitor2 = Monitor(env, Process2, samp_dist)
Monitor3 = Monitor(env, Process3, samp_dist)
Monitor4 = Monitor(env, Process4, samp_dist)
Monitor5 = Monitor(env, Process5, samp_dist)
Monitor6 = Monitor(env, Process6, samp_dist)
Monitor7 = Monitor(env, Process7, samp_dist)

# Connection
Source.out = Process1
Process1.out = Process2
Process2.out = Process3
Process3.out = Process4
Process4.out = Process5
Process5.out = Process6
Process6.out = Process7
Process7.out = Sink

# Run it
env.run(until=RUN_TIME)