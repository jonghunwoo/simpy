import simpy
import numpy as np

env = simpy.Environment() # shared_event 전역변수 설정을 위해 가장 앞에 Environment 설

## 전역 이벤트 변수 선언
shared_event = env.event()

def global_process(env, shared_event): # shared_evnet를 관리하는 프로세스
    ## 1초에 한번씩 global event가 발생할 것인지 파악함
    while True:
        yield env.timeout(1)
        print('from global process at', env.now)
        if np.random.randint(0, 50) == 1:
            ## 이벤트가 성공했음을 표시함
            shared_event.succeed()
            break   # 원 프로세스와 관리 프로세스 모두 중단되어야 함 (어느 한쪽에서 break 하지 않으면 무한루프 또는 sharing 붕괴로 에러)

def simple_process(env, shared_event):
    while True:
        ## 다른 프로세스에서 shared_event.succeed()가 실행되면
        ## env.timeout(10.0)이 아직 끝나지 않았더라도, 이 부분이 종료되고 다음으로 넘어감
        print('from simple process at ', env.now, 'befor yield')
        result = yield env.timeout(10.0) | shared_event
        print('from simple process at ', env.now, 'after yield')
        if shared_event in result:
            print("shared event occurs at {}".format(env.now))
            break # 원 프로세스와 관리 프로세스 모두 중단되어야 함 (어느 한쪽에서 break 하지 않으면 무한루프 또는 sharing 붕괴로 에러)# 원 프로세스와 관리 프로세스 모두 중단되어야 함 (어느 한쪽에서 break 하지 않으면 무한루프 또는 sharing 붕괴로 에러)
        print("shared event didn't occurs during {}".format(env.now))
        print('#' * 100)

np.random.seed(31)

shared_event = env.event()

env.process(simple_process(env, shared_event))
env.process(global_process(env, shared_event))

env.run(until=100)