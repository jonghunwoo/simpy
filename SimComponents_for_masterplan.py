import simpy
from collections import deque, OrderedDict


class DataframePart(object):

    def __init__(self, time, block_data, id, src="a", dst="z", flow_id=0):
        self.time = time
        self.project = block_data[0] #블록이 속한 project
        self.location_code = block_data[1] #블록의 location code
        self.activity_data = block_data[2] #블록에 대한 activity 정보
        self.simulation_data = OrderedDict() #블록의 시뮬레이션 결과
        self.id = id
        self.src = src
        self.dst = dst
        self.flow_id = flow_id

    def __repr__(self):
        return "id: {}, src: {}, time: {}".format(self.id, self.src, self.time)


class DataframeSource(object):

    def __init__(self, env, id, IAT, block_data,  process_dict, initial_delay=0, finish=float("inf"), flow_id=0):
        self.id = id
        self.env = env
        self.IAT = IAT #블록간 inter_arrival_time
        self.block_data = block_data #블록의 project, location code, activity 정보
        self.process_dict =  process_dict #각 activity에 대응되는 Process 객체들을 저장한 딕셔너리
        self.initial_delay = initial_delay
        self.finish = finish
        self.parts_sent = 0
        self.action = env.process(self.run())
        self.flow_id = flow_id

    def run(self):
        yield self.env.timeout(self.initial_delay)
        while self.env.now < self.finish:
            try:
                # inter_arrival_time만큼 대기 후 블록 생성
                yield self.env.timeout(next(self.IAT))
                self.parts_sent += 1
                p = DataframePart(self.env.now, next(self.block_data), self.parts_sent, src=self.id,
                                  flow_id=self.flow_id)

                idx = list(p.activity_data.keys())[0] #블록의 첫 번째 acitivty의 activity_code
                #첫 번째 Process 내 블록의 수가 qlimit와 같을 경우, 대기를 위한 event 발생
                if self.process_dict[idx].inventory + self.process_dict[idx].busy >= self.process_dict[idx].qlimit:
                    stop = self.env.event()
                    self.process_dict[idx].wait_for_next_process.append(stop)
                    yield stop
                self.process_dict[idx].put(p)
            except StopIteration:
                break


class Sink(object):

    def __init__(self, env, name, rec_arrivals=True, absolute_arrivals=False, rec_waits=True, debug=True, selector=None):
        self.name = name
        self.store = simpy.Store(env)
        self.env = env
        self.rec_waits = rec_waits
        self.rec_arrivals = rec_arrivals
        self.absolute_arrivals = absolute_arrivals
        self.waits = []
        self.arrivals = []
        self.debug = debug
        self.parts_rec = 0
        self.selector = selector
        self.last_arrival = 0.0
        self.block_project_sim = {} # 모든 블록에 대한 시뮬레이션 결과를 저장하는 딕셔너리

    def put(self, part):
        if not self.selector or self.selector(part):
            now = self.env.now
            if self.rec_waits:
                self.waits.append(self.env.now - part.time)
            if self.rec_arrivals:
                if self.absolute_arrivals:
                    self.arrivals.append(now)
                else:
                    self.arrivals.append(now - self.last_arrival)
                self.last_arrival = now
            self.parts_rec += 1
            #각 블록의 시뮬레이션 결과를 통합
            # 시뮬레이션 결과 데이터를 저장하는 딕셔너리가 블록의 project를 key로 갖고 있지 않으면 이를 추가
            if not part.project in list(self.block_project_sim.keys()):
                self.block_project_sim[part.project] = {}
            # 블록의 location code를 key 값으로 블록의 시뮬레이션 결과를 저장하는 딕셔너리 추가
            self.block_project_sim[part.project][part.location_code] = part.simulation_data
            if self.debug:
                print(part)


class Process(object):

    def __init__(self, env, name, subprocess_num, process_dict, qlimit=None, limit_bytes=True, debug=False):
        self.name = name
        self.store = simpy.Store(env)
        self.env = env
        self.subprocess_num = subprocess_num
        self.wait_for_next_process = deque([]) #이전 Process에서 발생시킨 대기 event들을 저장
        self.wait_for_subprocess = self.env.event() #subprocess가 모두 가동 중일 경우, 대기를 위한 event
        self.parts_rec = 0
        self.parts_drop = 0
        self.qlimit = qlimit
        self.process_dict = process_dict #각 activity에 대응되는 Process 객체들을 저장한 딕셔너리
        self.limit_bytes = limit_bytes
        self.debug = debug
        self.inventory = 0
        self.busy = 0
        self.working_time = 0
        self.working_time_list = []
        self.action = env.process(self.run())

    def run(self):
        while True:
            # 현재 작업 중인 블록의 수가 subprocess_num보다 적으면 subprocess 생성
            # 현재 작업 중인 블록의 수가 subprocess_num과 같아지면 대기 event 발생
            if self.busy < self.subprocess_num:
                msg = (yield self.store.get())
                self.inventory -= 1
                self.busy += 1
                self.env.process(self.subrun(msg))
            else:
                yield self.wait_for_subprocess

    def subrun(self, msg):
        proc_time = msg.activity_data[self.name][1] # 블록의 현재 Process에서의 작업시간을 저장
        start = self.env.now # 블록의 작업 시작 시간
        msg.simulation_data[self.name] = [start] # 시뮬레이션 결과에 블록의 작업 시작 시간 저장
        yield self.env.timeout(proc_time) # 블록의 작업 시간만큼 event 발생
        finish = self.env.now # 블록의 작업 종료 시간
        msg.simulation_data[self.name].append(finish - start) # 시뮬레이션 결과에 블록의 작업 시간 저장

        idx = list(msg.activity_data.keys()).index(self.name) # 블록의 activity들 중 현재 Process가 해당되는 순서 저장
        if idx != len(msg.activity_data) - 1: # 현재 Process가 마지막 activity가 아니면 다음 Process에 블록 put
            next_process = list(msg.activity_data.keys())[idx + 1] # 블록의 다음 Process의 activity_code 저장
            # 계획된 다음 Process의 시작 시간과 현재 Process에서 작업 종료 시간의 차로 lag 계산
            # lag만큼 대기하는 event 발생
            lag = msg.activity_data[next_process][0] - finish
            if lag > 0:
                yield self.env.timeout(lag)
            # 다음 Process 내 블록의 수가 qlimit와 같을 경우, 대기를 위한 event 발생
            if self.process_dict[next_process].inventory + self.process_dict[next_process].busy >= self.process_dict[next_process].qlimit:
                stop = self.env.event()
                self.process_dict[next_process].wait_for_next_process.append(stop)
                yield stop
            self.process_dict[next_process].put(msg)
        else: # 현재 Process가 마지막 activity이면 블록을 Sink로 put
            self.process_dict['Sink'].put(msg)

        # subprocess가 모두 가동 중일 때 대기하도록 발생한 event를 종료시킴
        self.busy -= 1
        self.wait_for_subprocess.succeed()
        self.wait_for_subprocess = self.env.event()

        if self.debug:
            print(msg)

        # 현재 Process 내 블록의 수가 qlimit보다 작아지면 이전 Process에서 발생시킨 대기 event 종료시킴
        if self.inventory + self.busy < self.qlimit and len(self.wait_for_next_process) > 0:
            temp = self.wait_for_next_process.popleft()
            temp.succeed()

    def put(self, part):
        self.inventory += 1
        self.parts_rec += 1
        if self.qlimit is None:
            return self.store.put(part)
        elif len(self.store.items) >= self.qlimit:
            self.parts_drop += 1
        else:
            return self.store.put(part)


class Monitor(object):

    def __init__(self, env, port, dist):
        self.port = port
        self.env = env
        self.dist = dist
        self.sizes = []
        self.action = env.process(self.run())

    def run(self):
        while True:
            yield self.env.timeout(self.dist())
            total = self.port.inventory + self.port.busy
            self.sizes.append(total)