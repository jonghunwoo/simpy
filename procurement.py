import os
import random
import urllib.request
import xlrd
import csv
import pandas as pd
import functools
import simpy
from SimComponents_rev3 import Source, DataframeSource, Sink, Process, Monitor

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

df1 = data[["NO_SPOOL", "DIA", "Length", "Weight", "MemberCount", "JointCount", "Material", "제작협력사", "도장협력사", "Actual_makingLT", "Predicted_makingLT", "Actual_paintingLT", "Predicted_paintingLT"]]

print(df1.head())

""" Simulation
    Dataframe with product data is passed to Source.
    Then, source create product with interval time of defined adist function.
    For this purpose, DataframeSource is defined based on original Source.
"""

random.seed(42)
adist = functools.partial(random.randrange,3,7) # Inter arrival time
samp_dist = functools.partial(random.expovariate, 1) # need to be checked
proc_time = functools.partial(random.normalvariate,5,1) # sample process working time

RUN_TIME = 500

env = simpy.Environment()

Source = DataframeSource(env, "Source", adist, df1)
Sink = Sink(env, 'Sink', debug=False, rec_arrivals=True)

Process1 = Process(env, 'Process1', proc_time, qlimit=1, limit_bytes=False)
Process2 = Process(env, 'Process2', proc_time, qlimit=1, limit_bytes=False)
Process3 = Process(env, 'Process3', proc_time, qlimit=1, limit_bytes=False)
Process4 = Process(env, 'Process4', proc_time, qlimit=1, limit_bytes=False)
Process5 = Process(env, 'Process5', proc_time, qlimit=1, limit_bytes=False)
Process6 = Process(env, 'Process6', proc_time, qlimit=1, limit_bytes=False)
Process7 = Process(env, 'Process7', proc_time, qlimit=1, limit_bytes=False)

"""