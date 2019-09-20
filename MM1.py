"""
Example use of SimComponents to simulate a packet queue with M/M/1 characteristics.
Copyright 2014 Dr. Greg M. Bernstein
Released under the MIT license
"""
import random
import functools
import simpy
import numpy as np
import matplotlib.pyplot as plt
from SimComponents import Source, Sink, Process, Monitor
#from keras.models import load_model

if __name__ == '__main__':

    # Set up arrival and packet size distributions
    # Using Python functools to create callable functions for random variates with fixed parameters
    # each call to these will produce a new random value

    adist = functools.partial(random.randrange,1,10) # arrival distribution
    # sdist = functools.partial(random.expovariate, 0.1)  # successive sizes of packets
    sdist = functools.partial(random.randint,1,1)
    samp_dist = functools.partial(random.expovariate, 1)
    ct_1 = 3
    ct_2 = 3
    ct_3 = 3
    var_1 = 1
    var_2 = 1
    var_3 = 1

    RUN_TIME = 100

    # Create the SimPy environment
    env = simpy.Environment()

    # load learning model
    # model = load_model('making_DL_model.h5')
    # predicted = model.predict(X2_test)

    # Create the packet generators and sink
    Sink = Sink(env, 'Sink', debug=False, rec_arrivals=True)
    Source = Source(env, "Source", adist, sdist)
    Process1 = Process(env, 'Process1', random.normalvariate(ct_1, var_1), qlimit=10000, limit_bytes = False)
    Process2 = Process(env, 'Process2', random.normalvariate(ct_2, var_2), qlimit=10000, limit_bytes = False)
    Process3 = Process(env, 'Process3', random.normalvariate(ct_3, var_3), qlimit=10000, limit_bytes = False)

    # Using a PortMonitor to track queue sizes over time
    Monitor1 = Monitor(env, Process1, samp_dist)
    Monitor2 = Monitor(env, Process2, samp_dist)
    Monitor3 = Monitor(env, Process3, samp_dist)

    # Wire packet generators, switch ports, and sinks together
    Source.out = Process1
    Process1.out = Process2
    Process2.out = Process3
    Process3.out = Sink

    # Run it
    env.run(until=RUN_TIME)

    print('#'*80)
    print("Results of simulation")
    print('#'*80)
    print("Lead time of Last 10 Parts: " + ", ".join(["{:.3f}".format(x) for x in Sink.waits[-10:]]))

    print("Process1: Last 10 queue sizes: {}".format(Monitor1.sizes[-10:]))
    print("Process2: Last 10 queue sizes: {}".format(Monitor2.sizes[-10:]))
    print("Process3: Last 10 queue sizes: {}".format(Monitor3.sizes[-10:]))

    print("Sink: Last 10 sink arrival times: " + ", ".join(["{:.3f}".format(x) for x in Sink.arrivals[-10:]])) # 모든 공정을 거친 packet이 최종 노드에 도착하는 시간 간격 - TH 계산 가능
    print("Sink: average wait = {:.3f}".format(sum(Sink.waits)/len(Sink.waits))) # 모든 packet들의 리드타임의 평

    print("received: {}, dropped {}, sent {}".format(Process1.parts_rec, Process1.parts_drop, Source.parts_sent))

    print("loss rate: {}".format(float(Process1.parts_drop)/Process1.parts_rec)) # SwitchPort들이 qlimit에 도달한 상태에서 packet이 도착하면 loss로 처리학고 있음 - 대기하도록 SimComponent 코드 수정 필요
    print("loss rate: {}".format(float(Process2.parts_drop)/Process2.parts_rec))
    print("loss rate: {}".format(float(Process3.parts_drop)/Process3.parts_rec))

    print("average system occupancy of Process1: {:.3f}".format(float(sum(Monitor1.sizes))/len(Monitor1.sizes)))
    print("average system occupancy of Process2: {:.3f}".format(float(sum(Monitor2.sizes))/len(Monitor2.sizes)))
    print("average system occupancy of Process3: {:.3f}".format(float(sum(Monitor3.sizes))/len(Monitor3.sizes)))

    print("utilization of Process1: {:2.2f}".format(Process1.working_time/RUN_TIME))
    print("utilization of Process2: {:2.2f}".format(Process2.working_time/RUN_TIME))
    print("utilization of Process3: {:2.2f}".format(Process3.working_time/RUN_TIME))

    # 각 packet의 시스템 체류 시간(리드타임)을 도수분포료(histogram)으로 플로팅
    fig, axis = plt.subplots()
    axis.hist(Sink.waits, bins=100, density=True)
    axis.set_title("Histogram for waiting times")
    axis.set_xlabel("time")
    axis.set_ylabel("normalized frequency of occurrence")
    #fig.savefig("WaitHistogram.png")
    #plt.show()

    fig, axis = plt.subplots()
    axis.hist(Sink.arrivals, bins=100, density=True)
    axis.set_title("Histogram for Sink Interarrival times")
    axis.set_xlabel("time")
    axis.set_ylabel("normalized frequency of occurrence")

    #fig.savefig("ArrivalHistogram.png")
    #plt.show()