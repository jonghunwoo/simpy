import simpy
import numpy as np

#very basic case - clock
"""
def clock(env, name, tick):
    while True:
        print("{:.2f} sec: {} clock ticks".format(env.now, name))
        yield env.timeout(tick)


env = simpy.Environment()

fast_clock = clock(env, 'fast', 0.5)
slow_clock = clock(env, 'slow', 1)
very_fast_clock = clock(env, 'very fast', 0.1)

env.process(fast_clock)
env.process(slow_clock)
env.process(very_fast_clock)

env.run(until = 5)

"""

#basic case - car
"""
def car1(env):
    while True:
        print('Start parking at %5.1f' % env.now)
        parking_duration = 5
        #parking_duration = np.random.normal(5, 1)
        yield env.timeout(parking_duration)
        print('Stop  parking at %5.1f' % env.now)

        print('Start driving at %5.1f' % env.now)
        driving_duration = 2
        #trip_duration = np.random.normal(2, 1)
        yield env.timeout(driving_duration)
        print('Stop  driving at %5.1f' % env.now)

def car2(env):
    while True:
        print('Start parking at %5.1f' % env.now)
        parking_duration = 3
        # parking_duration = np.random.normal(5, 1)
        yield env.timeout(parking_duration)
        print('Stop  parking at %5.1f' % env.now)

        print('Start driving at %5.1f' % env.now)
        driving_duration = 10
        # trip_duration = np.random.normal(2, 1)
        yield env.timeout(driving_duration)
        print('Stop  driving at %5.1f' % env.now)

env = simpy.Environment()
env.process(car1(env))
env.process(car2(env))

env.run(until=100)
"""

#basic case - business process simulation
"""
def business_process(env, activity_lst):
    #while True:
    for i in range(5):
        for act in activity_lst:
            ## activity의 수행 시간은 triangulat dist를 따르며,
            print('start {} at {:6.2f}'.format(act, env.now))
            activity_time = np.random.triangular(left=3, right=10, mode=7)
            yield env.timeout(activity_time)
            print('end   {} at {:6.2f}'.format(act, env.now))

            ## activity를 transfer하는데 일정 시간이 소요된다고 가정함.
            activity_transfer_time = np.random.triangular(left=1, right=3, mode=2)
            yield env.timeout(activity_transfer_time)
        print("#" * 30)
        print("process end")
        ## 만약 여기 return 을 넣으면 여기서 generator가 그대로 종료됨
        ## 만약 n 번 수행하고 싶다면, while True 를 for 문으로 변경하고, 몇 번 종료 후 끝내는 형태로 해도 괜찮을듯.
        #return 'over'


## environment setting
env = simpy.Environment()

bp1 = business_process(env, activity_lst=["activity_{}".format(i) for i in range(1, 6)])
env.process(bp1)

env.run(until=200)
"""

#basic case - resource
"""
def Student(env, num, library, arrive_time):
    ## student마다 도착하는 시간이 다르게 표현
    yield env.timeout(arrive_time)
    ## 아래와 같은 형태로 쓰면 자동으로 get, release가 된다.
    ## 단, 다른 형태로 쓸 경우에는 req = library.request(), library.release(req) 로 해주어야 함

    ## with library.request() as req:
    ##   yield req

    ## 여기서 해당 resource에 대한 사용권을 얻고
    ## req = library.request()
    ## 사용이 종료되면, 다음을 통해 resource의 사용권을 풀어줌
    ## library.release(req)

    ## with 내의 구문이 종료되면 자동으로 resource release
    with library.request() as req:
        ## resource를 사용할 수 있을때까지 기다림, 즉시 사용가능하다면 이 부분은 거의 바로 넘어감
        yield req
        ## 일정 시간 만큼 공부함
        study_time = np.random.triangular(left=5, right=10, mode=8)
        yield env.timeout(study_time)
        ## with as 구문으로 resource를 사용할 경우에는, 끝에 굳이 release를 추가하지 않아도 자동으로 release해줌


env = simpy.Environment()
## capacity가 2인 리소스를 선언
library = simpy.Resource(env, capacity=2)

for i in range(0, 5):
    arrive_time = np.random.triangular(left=1, right=8, mode=3)
    stu = Student(env, i, library, arrive_time)
    env.process(stu)

## 50초까지 표현했지만, 남아있는 process가 없을 경우에는 그냥 종료됨.
env.run(until=50)
"""

#basic case - resource, the better code
#"""

def Student(env, num, library, arrive_time):
    ## 학생은 랜덤 시간 이후 도착
    yield env.timeout(arrive_time)
    print("student {} arrived library at {:6.2f}".format(num, env.now))
    waiting_time = env.now

    ## 아래와 같은 형태로 쓰면 자동으로 get, release가 된다.
    ## 단, 다른 형태로 쓸 경우에는 req = library.request(), library.release(req) 로 해주어야 함.
    with library.request() as req:
        yield req  ## resource를 사용이 가능하면 이 부분이 수행됨
        waiting_time = env.now - waiting_time
        ## waiting_time이 0이 아닌 경우는 기다린 경우
        if waiting_time != 0:
            print("student {} is waiting  during {:6.2f}".format(num, waiting_time))
        ## 얼마나 공부할지를 계산
        study_time = np.random.triangular(left=5, right=10, mode=8)
        print("student {} start to  study at {:6.2f}".format(num, env.now))
        ## 학생이 공부를 시작했고 => 현재 도서관이 꽉 차 있을 경우 꽉 차있다는 것을 표현
        if library.capacity == library.count:
            print("#### library full at  {:6.2f} ####".format(env.now))
        yield env.timeout(study_time)
        print("student {} end   to  study at {:6.2f}".format(num, env.now))
        print("#### library seat available at {:6.2f} ####".format(env.now))


env = simpy.Environment()
library = simpy.Resource(env, capacity=2)

for i in range(0, 5):
    arrive_time = np.random.triangular(left=1, right=8, mode=3)
    stu = Student(env, i, library, arrive_time)
    env.process(stu)

env.run(until=50)