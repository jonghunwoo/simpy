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