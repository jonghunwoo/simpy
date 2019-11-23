import os
import random
import urllib.request
import xlrd
import csv
import pandas as pd
import functools
import simpy
from SimComponents_rev5 import Source, DataframeSource, Sink, Process, Monitor

""" Data loading
    1. request raw excel file from github of jonghunwoo
    2. then, change the format from excel to csv
    3. Data frame object of product data is generated from csv file
"""

# ./data 폴더에 해당 파일이 없으면 실행
if not os.path.isfile('./data/spool_data_for_simulation.csv'):
    url = "https://raw.githubusercontent.com/jonghunwoo/public/master/spool_data_for_simulation.xlsx"
    filename = "./data/spool_data_for_simulation.xlsx"
    urllib.request.urlretrieve(url, filename)

    def csv_from_excel(excel_name, file_name, sheet_name):
        workbook = xlrd.open_workbook(excel_name)
        worksheet = workbook.sheet_by_name(sheet_name)
        csv_file = open(file_name, 'w')
        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

        for row_num in range(worksheet.nrows):
            writer.writerow(worksheet.row_values(row_num))

        csv_file.close()

    csv_from_excel('./data/spool_data_for_simulation.xlsx', './data/spool_data_for_simulation.csv', 'Sheet1')

# csv 파일 pandas 객체 생성
data = pd.read_csv('./data/spool_data_for_simulation.csv')

df = data[["NO_SPOOL", "DIA", "Length", "Weight", "MemberCount", "JointCount", "Material", "제작협력사", "도장협력사", "Actual_makingLT", "Predicted_makingLT", "Actual_paintingLT", "Predicted_paintingLT"]]

df.rename(columns={'NO_SPOOL': 'part_no', "제작협력사": 'Proc1', '도장협력사': 'Proc2', 'Actual_makingLT': 'CT1', 'Predicted_makingLT': 'CT2', 'Actual_paintingLT': 'CT3', 'Predicted_paintingLT': 'CT4'}, inplace=True)

""" Simulation
    Dataframe with product data is passed to Source.
    Then, source create product with interval time of defined adist function.
    For this purpose, DataframeSource is defined based on original Source.
"""

random.seed(42)
adist = functools.partial(random.randrange,3,7) # Inter-arrival time
samp_dist = functools.partial(random.expovariate, 1) # need to be checked
proc_time = functools.partial(random.normalvariate,5,1) # sample process working time

RUN_TIME = 500

env = simpy.Environment()

Source = DataframeSource(env, "Source", adist, df, 7)
Sink = Sink(env, 'Sink', debug=False, rec_arrivals=True)

Proc1_1 = Process(env, "(주)성광테크", proc_time, 10, 7, qlimit=10000, limit_bytes=False)
Proc1_2 = Process(env, "건일산업(주)", proc_time, 10, 7, qlimit=10000, limit_bytes=False)
Proc1_3 = Process(env, "부흥", proc_time, 10, 7, qlimit=10000, limit_bytes=False)
Proc1_4 = Process(env, "삼성중공업(주)거제", proc_time, 10, 7, qlimit=10000, limit_bytes=False)
Proc1_5 = Process(env, "성일", proc_time, 10, 7, qlimit=10000, limit_bytes=False)
Proc1_6 = Process(env, "성일SIM함안공장", proc_time, 10, 7, qlimit=10000, limit_bytes=False)
Proc1_7 = Process(env, "해승케이피", proc_time, 10, 7, qlimit=10000, limit_bytes=False)

Proc2_1 = Process(env, "(주)성광테크", proc_time, 10, 1, qlimit=10000, limit_bytes=False)
Proc2_2 = Process(env, "건일산업(주)", proc_time, 10, 1, qlimit=10000, limit_bytes=False)
Proc2_3 = Process(env, "삼녹", proc_time, 10, 1, qlimit=10000, limit_bytes=False)
Proc2_4 = Process(env, "성도", proc_time, 10, 1, qlimit=10000, limit_bytes=False)
Proc2_5 = Process(env, "성일SIM함안공장", proc_time, 10, 1, qlimit=10000, limit_bytes=False)
Proc2_6 = Process(env, "하이에", proc_time, 10, 1, qlimit=10000, limit_bytes=False)
Proc2_7 = Process(env, "해승케이피", proc_time, 10, 1, qlimit=10000, limit_bytes=False)

Source.outs[0] = Proc1_1
Source.outs[1] = Proc1_2
Source.outs[2] = Proc1_3
Source.outs[3] = Proc1_4
Source.outs[4] = Proc1_5
Source.outs[5] = Proc1_6
Source.outs[6] = Proc1_7

Proc1_1.outs[0] = Proc2_1
Proc1_1.outs[1] = Proc2_2
Proc1_1.outs[2] = Proc2_3
Proc1_1.outs[3] = Proc2_4
Proc1_1.outs[4] = Proc2_5
Proc1_1.outs[5] = Proc2_6
Proc1_1.outs[6] = Proc2_7

Proc1_2.outs[0] = Proc2_1
Proc1_2.outs[1] = Proc2_2
Proc1_2.outs[2] = Proc2_3
Proc1_2.outs[3] = Proc2_4
Proc1_2.outs[4] = Proc2_5
Proc1_2.outs[5] = Proc2_6
Proc1_2.outs[6] = Proc2_7

Proc1_3.outs[0] = Proc2_1
Proc1_3.outs[1] = Proc2_2
Proc1_3.outs[2] = Proc2_3
Proc1_3.outs[3] = Proc2_4
Proc1_3.outs[4] = Proc2_5
Proc1_3.outs[5] = Proc2_6
Proc1_3.outs[6] = Proc2_7

Proc1_4.outs[0] = Proc2_1
Proc1_4.outs[1] = Proc2_2
Proc1_4.outs[2] = Proc2_3
Proc1_4.outs[3] = Proc2_4
Proc1_4.outs[4] = Proc2_5
Proc1_4.outs[5] = Proc2_6
Proc1_4.outs[6] = Proc2_7

Proc1_5.outs[0] = Proc2_1
Proc1_5.outs[1] = Proc2_2
Proc1_5.outs[2] = Proc2_3
Proc1_5.outs[3] = Proc2_4
Proc1_5.outs[4] = Proc2_5
Proc1_5.outs[5] = Proc2_6
Proc1_5.outs[6] = Proc2_7

Proc1_6.outs[0] = Proc2_1
Proc1_6.outs[1] = Proc2_2
Proc1_6.outs[2] = Proc2_3
Proc1_6.outs[3] = Proc2_4
Proc1_6.outs[4] = Proc2_5
Proc1_6.outs[5] = Proc2_6
Proc1_6.outs[6] = Proc2_7

Proc1_7.outs[0] = Proc2_1
Proc1_7.outs[1] = Proc2_2
Proc1_7.outs[2] = Proc2_3
Proc1_7.outs[3] = Proc2_4
Proc1_7.outs[4] = Proc2_5
Proc1_7.outs[5] = Proc2_6
Proc1_7.outs[6] = Proc2_7

