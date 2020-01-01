import time
import pandas as pd
import numpy as np

# data 가져오기
input_data = pd.read_excel('./data/MCM_ACTIVITY.xls')

# 전체 data 개수
data_num = len(input_data)

'''
2018년 이후의 작업 중 가장 빠른 날짜 찾기(initial_date)
'''
pd.to_datetime(input_data['PLANSTARTDATE'], unit='s')  # 작업의 편의성을 위해 datetime 형식으로 변경
STARTDATE = []  # 2018년 이후의 날짜만 저장할 list

for i in range(data_num):
    if input_data['PLANSTARTDATE'][i].year >= 2018:
        STARTDATE.append(input_data['PLANSTARTDATE'][i])

initial_date = np.min(STARTDATE)  # 2018-12-10

'''
데이터 저장 & 가공

data 저장 형식:
{ 호선 번호
    : { block code(location code) 
            : { activity code : [ 시작일 (initial date와의 시간 간격) , duration ] }
'''
# 변수
raw_data = {}  # 전처리 전 데이터, 부하 계산 시 사용
preproc_data = {}  # 전처리 후 데이터, Simcomponents 실행 시 사용
activity = []  # 모든 activity code를 저장할 list
PROJECT = []  # 호선 번호 저장 할 list

# 데이터 받아오기
for i in range(data_num):
    temp = input_data.loc[i]  # 한 행씩 읽어주기
    proj_name = temp.PROJECTNO  # 호선 번호
    proj_block = temp.LOCATIONCODE  # block code
    activity_code = temp.ACTIVITYCODE[5:]  # activity code

    # 2005년도 자료 + ACTIVITYCODE가 '#'으로 시작하는 데이터는 버림
    if (temp.PLANSTARTDATE.year >= 2018) and (proj_block != 'OOO'):
        # 호선 번호를 key값으로 갖는 dictionary 만들어주기 -> value는 block code를 키값으로 갖는 딕셔너리
        if proj_name not in PROJECT:
            PROJECT.append(proj_name)
            raw_data[proj_name] = {}
            preproc_data[proj_name] = {}
        if proj_block not in raw_data[proj_name].keys():
            # block code를 키값으로 갖는 dictionary 만들어주기 -> value는 각 activity code, 시작, duration을 기록한 list
            # location code : {ACTIVITYCODE : start date, duration}
            raw_data[proj_name][proj_block] = {}
            preproc_data[proj_name][proj_block] = {}

        # 시작 날짜 = 0으로 하여 일 기준으로 시간 차이 계산해 줌
        interval_t = temp.PLANSTARTDATE - initial_date   # + datetime.timedelta(days=1)

        if activity_code not in activity:
            activity.append(activity_code)

        # [시작 시간 간격, 총 공정 시간]
        raw_data[proj_name][proj_block][activity_code] = [interval_t.days, temp.PLANDURATION]
        preproc_data[proj_name][proj_block][activity_code] = [interval_t.days, temp.PLANDURATION]


# 날짜 순서대로 정렬
for name in PROJECT:
    for location_code in raw_data[name].keys():
        # 시작 날짜 기준으로 정렬해 줌
        sorted_raw = sorted(raw_data[name][location_code].items(), key=lambda x: x[1][0])
        sorted_preproc = sorted(preproc_data[name][location_code].items(), key=lambda x: x[1][0])
        raw_data[name][location_code] = sorted_raw
        preproc_data[name][location_code] = sorted_preproc


# 블럭 별 첫 공정 시작 시간 순서로 정렬
for name in PROJECT:
    block_list_raw = list(raw_data[name].items())
    block_sorted_raw = sorted(block_list_raw, key=lambda x: x[1][0][1][0])
    raw_data[name] = block_sorted_raw

    block_list_preproc = list(preproc_data[name].items())
    block_sorted_preproc = sorted(block_list_preproc, key=lambda x: x[1][0][1][0])
    preproc_data[name] = block_sorted_preproc


# block간 시작 시간 간격 (첫 공정 시작 시간 비교) / 처음 = 0 / i번째 : i - (i-1)
IAT = {}
for name in PROJECT:
    IAT[name] = []
    for i in range(len(raw_data[name])):
        if i == 0:
            IAT[name].append(0)
        else:
            interval_AT = raw_data[name][i][1][0][1][0] - raw_data[name][i-1][1][0][1][0]
            IAT[name].append(interval_AT)
    dict_block = dict(preproc_data[name])
    preproc_data[name] = dict_block


# 겹치거나 포함되는 부분 처리 (SimComponents 위함)
for name in PROJECT:
    for location_code in preproc_data[name].keys():
        for i in range(0, len(preproc_data[name][location_code])-1):
            # 선행 공정의 끝나는 시간
            date1 = preproc_data[name][location_code][i][1][0] + preproc_data[name][location_code][i][1][1] - 1
            # 후행 공정의 시작 시간
            date2 = preproc_data[name][location_code][i+1][1][0]
            # 후행 공정의 끝나는 시간
            date3 = preproc_data[name][location_code][i+1][1][0] + preproc_data[name][location_code][i+1][1][1] - 1

            if date1 > date2:  # 선행공정이 후행공정보다 늦게 끝날 때
                if date1 < date3:  # 선행 공정이랑 후행 공정이랑 겹칠 때
                    preproc_data[name][location_code][i+1][1][0] = date1
                else:  # 포함될 때
                    preproc_data[name][location_code][i+1][1][0] = date1
                    preproc_data[name][location_code][i+1][1][1] = 1
                    preproc_data[name][location_code][i+1][1].append("##")  # 완전히 포함되는 것에 표시

for name in PROJECT:
    for location_code in preproc_data[name].keys():
        temp_list = []
        for i in range(0, len(preproc_data[name][location_code])):
            if len(preproc_data[name][location_code][i][1]) < 3:
                temp_list.append(preproc_data[name][location_code][i])
        preproc_data[name][location_code] = dict(temp_list)

########################################################################################################################
import simpy
import random
from collections import OrderedDict
from SimComponents_for_masterplan import DataframeSource, Sink, Process
import matplotlib.pyplot as plt


# IAT data와 block data를 하나씩 차례대로 생성하는 generator 객체
def gen_schedule(inter_arrival_time_data):
    project_list = list(inter_arrival_time_data.keys())
    print(project_list)
    for project in project_list:
        for inter_arrival_time in inter_arrival_time_data[project]:
            yield inter_arrival_time


def gen_block_data(block_data):
    project_list = list(block_data.keys())
    for project in project_list:
        block_list = list(block_data[project].keys())
        for location_code in block_list:
            activity = OrderedDict(block_data[project][location_code])
            yield [project, location_code, activity]

print(IAT)

IAT_gen = gen_schedule(IAT)
preproc_data_gen = gen_block_data(preproc_data)


#시뮬레이션 시작
random.seed(42)

RUN_TIME = 45000

env = simpy.Environment()

process_dict = {}
Source = DataframeSource(env, "Source", IAT_gen, preproc_data_gen, process_dict)
Sink = Sink(env, 'Sink', debug=False, rec_arrivals=True)

process = []
for i in range(len(activity)):
    process.append(Process(env, activity[i], 10, process_dict, 10))

for i in range(len(activity)):
    process_dict[activity[i]] = process[i]

process_dict['Sink'] = Sink

# Run it
start = time.time()  # 시작 시간 저장
# Run it
env.run(until=RUN_TIME)
print("simulation time :", time.time() - start)

print('#'*80)
print("Results of simulation")
print('#'*80)

#계획 데이터 예시
print(preproc_data['U611']['A11C'])
#시뮬레이션 결과 생성된 데이터 예시
print(Sink.block_project_sim['U611']['A11C'])


#### WIP 계산

process_time = Sink.last_arrival
WIP = [0 for i in range(process_time)]

# for name in block_name:
for location_code in Sink.block_project_sim['U611'].keys():
    p = dict(Sink.block_project_sim['U611'][location_code])
    q = list(p.items())
    Sink.block_project_sim['U611'][location_code] = q
    for i in range(0, len(Sink.block_project_sim['U611'][location_code])-1):
        ###선행공정 끝나는 시간
        date1 = Sink.block_project_sim['U611'][location_code][i][1][0] + Sink.block_project_sim['U611'][location_code][i][1][1] -1
        ###후행공정 시작하는 시간
        date2 = Sink.block_project_sim['U611'][location_code][i+1][1][0]
        lag = date2-date1
        if lag > 3:
            for j in range(date1, date2):
                WIP[j] += 1

plt.plot(WIP)
plt.xlabel('time')
plt.ylabel('WIP')
plt.title('WIP')
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