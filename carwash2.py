import simpy
import numpy as np

## 세차머신
class CarWashMachine(object):
    ## 리소스는 아래처럼 클래스로 만들어서 처리해주는 것이 바람직할 것으로 생각됨
    def __init__(self, env, capacity):
        self.env = env
        self.machine = simpy.Resource(self.env, capacity = capacity)
        self.users = [] ## 현재 사용중인 프로세스
        self.queue = [] ## 현재 대기열에 있는 프로세스
    def wash(self, car_name):
        ## 아래처럼 resource 에서 이뤄지는 부분은 여기에서 작성하는 편이 더 좋을 수도 있음.
        print("{:6.2f} users: {}, queue: {}".format(env.now, self.users, self.queue))
        waiting_time = self.env.now
        with self.machine.request() as req:
            ## 바로 resource available 할 때
            if self.machine.count < self.machine.capacity:
                self.users.append(car_name)
                yield req
            ## resource available 하지 않을 때
            else:
                self.queue.append(car_name)
                yield req
                self.queue.remove(car_name)
                self.users.append(car_name)
            waiting_time = self.env.now - waiting_time
            if waiting_time!=0:
                print("{:6.2f} {} waited {:6.2f}".format(self.env.now, car_name, waiting_time))
            print("{:6.2f} {} wash start".format(self.env.now, car_name))
            wash_time = np.random.exponential(30)
            yield self.env.timeout(wash_time)
            print("{:6.2f} {} wash over".format(self.env.now, car_name))
        self.users.remove(car_name)

## 도착했음을 출력하고, 리소스에 사용요청을 보내고, 사용을 끝내면 메세지츨 출력하고 종료하는 제너레이터
def car(env, name, car_wash_machine):
    ## 도착하고, resource에 넘겨지고 그 다음을 죽 진행함.
    print("{:6.2f} {} arrived".format(env.now, name))
    yield env.process(car_wash_machine.wash(name))
    print("{:6.2f} {} leaved".format(env.now, name))

## 랜덤으로 car를 생성해내는 제너레이터
def source(env, car_n, car_wash_machine):
    for i in range(0, car_n):
        arrival_time = np.random.exponential(3)
        yield env.timeout(arrival_time)
        new_car = car(env, "Car{:2d}".format(i), car_wash_machine)
        env.process(new_car)

np.random.seed(42)
env = simpy.Environment()
cwm1 = CarWashMachine(env, capacity=2)

s = source(env, 10, cwm1)
env.process(s)

env.run(until=100)