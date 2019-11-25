import os
import random
import urllib.request
import xlrd
import csv
import pandas as pd
import functools
import simpy
from SimComponents_for_supply_chain import DataframeSource, Sink, Process, Monitor
import matplotlib.pyplot as plt

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

df = data[["NO_SPOOL", "DIA", "Length", "Weight", "MemberCount", "JointCount", "Material", "제작협력사", "도장협력사", "Plan_makingLT", "Actual_makingLT", "Predicted_makingLT", "Plan_paintingLT", "Actual_paintingLT", "Predicted_paintingLT"]]

df.rename(columns={'NO_SPOOL': 'part_no', "제작협력사": 'proc1', '도장협력사': 'proc2', 'Plan_makingLT': 'ct1', 'Actual_makingLT': 'ct3', 'Predicted_makingLT': 'ct5', 'Plan_paintingLT': 'ct2', 'Actual_paintingLT': 'ct4', 'Predicted_paintingLT': 'ct6'}, inplace=True)

""" Simulation
    Dataframe with product data is passed to Source.
    Then, source create product with interval time of defined adist function.
    For this purpose, DataframeSource is defined based on original Source.
"""

random.seed(42)
adist = functools.partial(random.randrange,1,10) # Inter-arrival time
samp_dist = functools.partial(random.expovariate, 1) # need to be checked
proc_time = functools.partial(random.normalvariate,5,1) # sample process working time

RUN_TIME = 45000
#RUN_TIME = 5000

env = simpy.Environment()

Source = DataframeSource(env, "Source", adist, df, 7)
Sink = Sink(env, 'Sink', debug=False, rec_arrivals=True)

Proc1_1 = Process(env, "proc1", "(주)성광테크", proc_time, 5, 7, qlimit=10, limit_bytes=False)
Proc1_2 = Process(env, "proc1", "건일산업(주)", proc_time, 5, 7, qlimit=10, limit_bytes=False)
Proc1_3 = Process(env, "proc1", "부흥", proc_time, 5, 7, qlimit=10000, limit_bytes=False)
Proc1_4 = Process(env, "proc1", "삼성중공업(주)거제", proc_time, 10, 7, qlimit=10, limit_bytes=False)
Proc1_5 = Process(env, "proc1", "성일", proc_time, 5, 7, qlimit=10000, limit_bytes=False)
Proc1_6 = Process(env, "proc1", "성일SIM함안공장", proc_time, 5, 7, qlimit=10, limit_bytes=False)
Proc1_7 = Process(env, "proc1", "해승케이피피", proc_time, 5, 7, qlimit=10, limit_bytes=False)

Proc2_1 = Process(env, "proc2", "(주)성광테크", proc_time, 5, 1, qlimit=10, limit_bytes=False)
Proc2_2 = Process(env, "proc2", "건일산업(주)", proc_time, 5, 1, qlimit=10, limit_bytes=False)
Proc2_3 = Process(env, "proc2", "삼녹", proc_time, 5, 1, qlimit=10, limit_bytes=False)
Proc2_4 = Process(env, "proc2", "성도", proc_time, 5, 1, qlimit=10, limit_bytes=False)
Proc2_5 = Process(env, "proc2", "성일SIM함안공장", proc_time, 5, 1, qlimit=10, limit_bytes=False)
Proc2_6 = Process(env, "proc2", "하이에어", proc_time, 5, 1, qlimit=10, limit_bytes=False)
Proc2_7 = Process(env, "proc2", "해승케이피피", proc_time, 5, 1, qlimit=10, limit_bytes=False)

Monitor1_1 = Monitor(env, Proc1_1, samp_dist)
Monitor1_2 = Monitor(env, Proc1_2, samp_dist)
Monitor1_3 = Monitor(env, Proc1_3, samp_dist)
Monitor1_4 = Monitor(env, Proc1_4, samp_dist)
Monitor1_5 = Monitor(env, Proc1_5, samp_dist)
Monitor1_6 = Monitor(env, Proc1_6, samp_dist)
Monitor1_7 = Monitor(env, Proc1_7, samp_dist)

Monitor2_1 = Monitor(env, Proc2_1, samp_dist)
Monitor2_2 = Monitor(env, Proc2_2, samp_dist)
Monitor2_3 = Monitor(env, Proc2_3, samp_dist)
Monitor2_4 = Monitor(env, Proc2_4, samp_dist)
Monitor2_5 = Monitor(env, Proc2_5, samp_dist)
Monitor2_6 = Monitor(env, Proc2_6, samp_dist)
Monitor2_7 = Monitor(env, Proc2_7, samp_dist)

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

Proc2_1.outs[0] = Sink
Proc2_2.outs[0] = Sink
Proc2_3.outs[0] = Sink
Proc2_4.outs[0] = Sink
Proc2_5.outs[0] = Sink
Proc2_6.outs[0] = Sink
Proc2_7.outs[0] = Sink

env.run(until=RUN_TIME)

print("Total Lead Time : ", Sink.last_arrival)

# 공정별 가동
working_time_1 = []
working_time_1.append(Proc1_1.working_time/Proc1_1.subprocess_num)
print(" working time of Process1_1: {:2.2f}".format(working_time_1[-1]))
working_time_1.append(Proc1_2.working_time/Proc1_2.subprocess_num)
print(" working time of Process1_2: {:2.2f}".format(working_time_1[-1]))
working_time_1.append(Proc1_3.working_time/Proc1_3.subprocess_num)
print(" working time of Process1_3: {:2.2f}".format(working_time_1[-1]))
working_time_1.append(Proc1_4.working_time/Proc1_4.subprocess_num)
print(" working time of Process1_4: {:2.2f}".format(working_time_1[-1]))
working_time_1.append(Proc1_5.working_time/Proc1_5.subprocess_num)
print(" working time of Process1_5: {:2.2f}".format(working_time_1[-1]))
working_time_1.append(Proc1_6.working_time/Proc1_6.subprocess_num)
print(" working time of Process1_6: {:2.2f}".format(working_time_1[-1]))
working_time_1.append(Proc1_7.working_time/Proc1_7.subprocess_num)
print(" working time of Process1_7: {:2.2f}".format(working_time_1[-1]))

working_time_2 = []
working_time_2.append(Proc2_1.working_time/Proc2_1.subprocess_num)
print(" working time of Process2_1: {:2.2f}".format(working_time_2[-1]))
working_time_2.append(Proc2_2.working_time/Proc2_2.subprocess_num)
print(" working time of Process2_2: {:2.2f}".format(working_time_2[-1]))
working_time_2.append(Proc2_3.working_time/Proc2_3.subprocess_num)
print(" working time of Process2_3: {:2.2f}".format(working_time_2[-1]))
working_time_2.append(Proc2_4.working_time/Proc2_4.subprocess_num)
print(" working time of Process2_4: {:2.2f}".format(working_time_2[-1]))
working_time_2.append(Proc2_5.working_time/Proc2_5.subprocess_num)
print(" working time of Process2_5: {:2.2f}".format(working_time_2[-1]))
working_time_2.append(Proc2_6.working_time/Proc2_6.subprocess_num)
print(" working time of Process2_6: {:2.2f}".format(working_time_2[-1]))
working_time_2.append(Proc2_7.working_time/Proc2_7.subprocess_num)
print(" working time of Process2_7: {:2.2f}".format(working_time_2[-1]))

print("average system occupancy of Proc1_1: {:.3f}".format(float(sum(Monitor1_1.sizes))/len(Monitor1_1.sizes)))
print("average system occupancy of Proc1_2: {:.3f}".format(float(sum(Monitor1_2.sizes))/len(Monitor1_2.sizes)))
print("average system occupancy of Proc1_3: {:.3f}".format(float(sum(Monitor1_3.sizes))/len(Monitor1_3.sizes)))
print("average system occupancy of Proc1_4: {:.3f}".format(float(sum(Monitor1_4.sizes))/len(Monitor1_4.sizes)))
print("average system occupancy of Proc1_5: {:.3f}".format(float(sum(Monitor1_5.sizes))/len(Monitor1_5.sizes)))
print("average system occupancy of Proc1_6: {:.3f}".format(float(sum(Monitor1_6.sizes))/len(Monitor1_6.sizes)))
print("average system occupancy of Proc1_7: {:.3f}".format(float(sum(Monitor1_7.sizes))/len(Monitor1_7.sizes)))

print("average system occupancy of Proc2_1: {:.3f}".format(float(sum(Monitor2_1.sizes))/len(Monitor2_1.sizes)))
print("average system occupancy of Proc2_2: {:.3f}".format(float(sum(Monitor2_2.sizes))/len(Monitor2_2.sizes)))
print("average system occupancy of Proc2_3: {:.3f}".format(float(sum(Monitor2_3.sizes))/len(Monitor2_3.sizes)))
print("average system occupancy of Proc2_4: {:.3f}".format(float(sum(Monitor2_4.sizes))/len(Monitor2_4.sizes)))
print("average system occupancy of Proc2_5: {:.3f}".format(float(sum(Monitor2_5.sizes))/len(Monitor2_5.sizes)))
print("average system occupancy of Proc2_6: {:.3f}".format(float(sum(Monitor2_6.sizes))/len(Monitor2_6.sizes)))
print("average system occupancy of Proc2_7: {:.3f}".format(float(sum(Monitor2_7.sizes))/len(Monitor2_7.sizes)))


#Sink.show_chart()

# 공정별 대기시간의 합
names = ["(주)성광테크", "건일산업(주)", "부흥", "삼성중공업(주)거제", "성일", "성일SIM함안공장", "해승케이피피", "삼녹", "성도", "하이에어"]
waiting_time = {}
for name in names:
    t = 0
    for i in range(len(Sink.waiting_list)):
        if len(Sink.waiting_list[i]) == 2:
            if name + ' ' + "waiting start" == list(Sink.waiting_list[i].keys())[0]:
                t += Sink.waiting_list[i][name + " waiting finish"] - Sink.waiting_list[i][name + " waiting start"]
                #print("2 ", Sink.waiting_list[i][name + " waiting finish"], " - ", Sink.waiting_list[i][name + " waiting start"])

        elif len(Sink.waiting_list[i]) == 4:
            #print(list(Sink.waiting_list[i].keys())[0])
            #print(list(Sink.waiting_list[i].keys())[1])
            #print(list(Sink.waiting_list[i].keys())[2])
            #print(list(Sink.waiting_list[i].keys())[3])
            if name + ' ' + "waiting start" == list(Sink.waiting_list[i].keys())[0]:
                t += Sink.waiting_list[i][name + " waiting finish"] - Sink.waiting_list[i][name + " waiting start"]
                #print("4 ", Sink.waiting_list[i][name + " waiting finish"], " - ", Sink.waiting_list[i][name + " waiting start"])
            if name + ' ' + "waiting start" == list(Sink.waiting_list[i].keys())[2]:
                t += Sink.waiting_list[i][name + " waiting finish"] - Sink.waiting_list[i][name + " waiting start"]
                #print("4 ", Sink.waiting_list[i][name + " waiting finish"], " - ", Sink.waiting_list[i][name + " waiting start"])
        else:
            print(Sink.waiting_list[i])

    waiting_time[name] = t

print("total waiting time of (주)성광테크 : ",waiting_time["(주)성광테크"])
print("total waiting time of 건일사업(주) : ",waiting_time["건일산업(주)"])
print("total waiting time of 부흥 : ",waiting_time["부흥"])
print("total waiting time of 삼성중공업(주)거제 : ",waiting_time["삼성중공업(주)거제"])
print("total waiting time of 성일 : ",waiting_time["성일"])
print("total waiting time of 성일SIM함안공장 : ",waiting_time["성일SIM함안공장"])
print("total waiting time of 해승케이피피 : ",waiting_time["해승케이피피"])
print("total waiting time of 삼녹 : ",waiting_time["삼녹"])
print("total waiting time of 성도 : ",waiting_time["성도"])
print("total waiting time of 하이에어 : ",waiting_time["하이에어"])

fig, axis = plt.subplots()
proc1_name = ["proc1_1", "proc1_2", "proc1_3", "proc1_4", "proc1_5", "proc1_6", "proc1_7"]
axis.bar(proc1_name, working_time_1)
axis.set_title("average working time of proc1")
axis.set_xlabel("Making process")
axis.set_ylabel("total working time")
plt.show()

fig, axis = plt.subplots()
proc2_name = ["proc2_1", "proc2_2", "proc2_3", "proc2_4", "proc2_5", "proc2_6", "proc2_7"]
axis.bar(proc2_name, working_time_2)
axis.set_title("average working time of proc2")
axis.set_xlabel("Painting process")
axis.set_ylabel("total working time")
plt.show()

fig, axis = plt.subplots()
axis.plot(Monitor1_2.times, Monitor1_2.sizes)
axis.set_title("WIP")
axis.set_xlabel("time")
axis.set_ylabel("WIP")
axis.set_xlim([0, Sink.last_arrival])
plt.show()

fig, axis = plt.subplots()
axis.hist(Sink.waits, bins=100, density=True)
axis.set_title("Histogram for waiting times")
axis.set_xlabel("time")
axis.set_ylabel("normalized frequency of occurrence")
plt.show()

fig, axis = plt.subplots()
axis.hist(Sink.arrivals, bins=100, density=True)
axis.set_title("Histogram for Sink Interarrival times")
axis.set_xlabel("time")
axis.set_ylabel("normalized frequency of occurrence")
plt.show()
