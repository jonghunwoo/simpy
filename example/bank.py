"""
Bank renege example

Covers:

- Resources: Resource
- Condition events

Scenario:
  A counter with a random service time and customers who renege

  Based on the program bank08.py from TheBank tutorial of SimPy 2

  https://pythonhosted.org/SimPy/Tutorials/TheBank.html

"""
import random

import simpy

RANDOM_SEED = 42 # 난수 지정 번호 - 변경에 따라 결과가 달라짐
NO_CUSTOMERS = 10  # 총 고객 수
INTERVAL_CUSTOMERS = 10.0  # 도착간 시간 간격 (inter-arrival time)
MIN_PATIENCE = 1  # Minimum customer patience
MAX_PATIENCE = 3  # Maximum customer patience
time_in_bank = 25
num_counter = 2

def source(env, number, interval, counter):

    # Random하게 고객(customer) 생성(generation)
    for i in range(number):

        # customer 함수(고객 이름, 리소스, 업무시간)를 프로세스에 탑재
        # customer 함수(name, resource, working time)를 프로세스에 탑재
        env.process(customer(env, 'Customer%02d' % i, counter, time_in_bank))

        #도착간 시간간격 시간 진행
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)

def customer(env, name, counter, time_in_bank):
    # source에서 customer 함수 호출과 함께 작동
    # 도착한 시간을 arrive에 기록
    arrive = env.now
    print('%7.4f %s: Here I am' % (arrive, name))

    # 본 함수를 호출한 source에서 전달받은 counter resource에 대한 requirement 구문
    with counter.request() as req:

        # customer가 기다릴 수 있는 한계 시간 생성
        patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)

        # counter가 가용해질때까지 기다리거나(req) 또는 인내심의 한계를 넘어 기다림 포기(env.timeout(patience))
        results = yield req | env.timeout(patience)

        # 기다린 시간을 wait에 기록
        wait = env.now - arrive

        # yield의 리턴값으로 받은 results에 req가 있는지 없는지에 따라 동작 결정
        # req in results가 true이면 time_in_bank 시간만큼 은행 업무 수행
        # 그렇지 않으면(else) 포기하고 돌아간 것으로 가정하고 메세지만 print
        if req in results:
            # We got to the counter
            print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))

            tib = random.expovariate(1.0 / time_in_bank)
            yield env.timeout(tib)
            print('%7.4f %s: Finished' % (env.now, name))

        else:
            # We reneged
            print('%7.4f %s: RENEGED after %6.3f' % (env.now, name, wait))


# Setup and start the simulation
print('Bank renege')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Start processes and run
counter = simpy.Resource(env, capacity=num_counter)
env.process(source(env, NO_CUSTOMERS, INTERVAL_CUSTOMERS, counter))

for i in range(3):
    random.seed(RANDOM_SEED)
    env = simpy.Environment()

    counter = simpy.Resource(env, capacity=num_counter)
    env.process(source(env, NO_CUSTOMERS, INTERVAL_CUSTOMERS, counter))

    env.run(200)
    time_in_bank -= 1


