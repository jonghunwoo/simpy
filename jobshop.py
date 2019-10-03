"""
Example use of SimComponents to simulate a certain jobshop model
Copyright 2019 Dr. Jonathan Woo
"""
import random
import functools
import simpy
from SimComponents_rev import Source, Sink, Process, Monitor, RandomBrancher

if __name__ == '__main__':

    # Set up arrival and packet size distributions
    # Using Python functools to create callable functions for random variates with fixed parameters
    # each call to these will produce a new random value
    random.seed(42)

    adist = functools.partial(random.randrange,3,7) # arrival distribution
    #sdist = functools.partial(random.expovariate, 0.1)  # successive sizes of packets
    sdist = functools.partial(random.randint,1,1)
    samp_dist = functools.partial(random.expovariate, 1)

    ct1 = 5
    ct2 = 5
    ct3 = 5
    var1 = 1
    var2 = 1
    var3 = 1

    proc_time1 = functools.partial(random.normalvariate,ct1,var1)
    proc_time2 = functools.partial(random.normalvariate,ct2,var2)
    proc_time3 = functools.partial(random.normalvariate,ct3,var3)

    RUN_TIME = 500

    # Create the SimPy environment
    env = simpy.Environment()

    # Create the packet generators and sink
    Sink = Sink(env, 'Sink', debug=False, rec_arrivals=True)
    Source = Source(env, "Source", adist, sdist)
    Process1 = Process(env, 'Process1', proc_time1, qlimit=3, limit_bytes=False)
    Process2 = Process(env, 'Process2', proc_time2, qlimit=3, limit_bytes=False)
    Process3 = Process(env, 'Process3', proc_time3, qlimit=3, limit_bytes=False)
    Process3_1 = Process(env, 'Process3_1', proc_time3, qlimit=3, limit_bytes=False)
    branch = RandomBrancher(env, [0.5, 0.5])

    # Using a PortMonitor to track queue sizes over time
    Monitor1 = Monitor(env, Process1, samp_dist)
    Monitor2 = Monitor(env, Process2, samp_dist)
    Monitor3 = Monitor(env, Process3, samp_dist)
    Monitor3_1 = Monitor(env, Process3_1, samp_dist)

    # Wire packet generators, switch ports, and sinks together
    Source.out = Process1
    Process1.out = Process2
    Process2.out = branch
    branch.outs[0] = Process3
    branch.outs[1] = Process3_1
    Process3.out = Sink
    Process3_1.out = Sink

    # Run it
    env.run(until=RUN_TIME)

    print('#'*80)
    print("Results of simulation")
    print('#'*80)
    print("Lead time of Last 10 Parts: " + ", ".join(["{:.3f}".format(x) for x in Sink.waits[-10:]]))

    print("Process1: Last 10 queue sizes: {}".format(Monitor1.sizes[-10:]))
    print("Process2: Last 10 queue sizes: {}".format(Monitor2.sizes[-10:]))
    print("Process3: Last 10 queue sizes: {}".format(Monitor3.sizes[-10:]))
    print("Process3_1: Last 10 queue sizes: {}".format(Monitor3_1.sizes[-10:]))

    print("Sink: Last 10 sink arrival times: " + ", ".join(["{:.3f}".format(x) for x in Sink.arrivals[-10:]])) # 모든 공정을 거친 packet이 최종 노드에 도착하는 시간 간격 - TH 계산 가능
    #print("Sink: average wait = {:.3f}".format(sum(Sink.waits)/len(Sink.waits))) # 모든 parts들의 리드타임의 평균

    print("sent {}".format(Source.parts_sent))
    print("received: {}, dropped {} of {}".format(Process1.parts_rec, Process1.parts_drop, Process1.name))
    print("received: {}, dropped {} of {}".format(Process2.parts_rec, Process2.parts_drop, Process2.name))
    print("received: {}, dropped {} of {}".format(Process3.parts_rec, Process3.parts_drop, Process3.name))
    print("received: {}, dropped {} of {}".format(Process3_1.parts_rec, Process3_1.parts_drop, Process3_1.name))

    #print("loss rate: {}".format(float(Process1.parts_drop)/Process1.parts_rec)) # SwitchPort들이 qlimit에 도달한 상태에서 packet이 도착하면 loss로 처리학고 있음 - 대기하도록 SimComponent 코드 수정 필요
    #print("loss rate: {}".format(float(Process2.parts_drop)/Process2.parts_rec))
    #print("loss rate: {}".format(float(Process3.parts_drop)/Process3.parts_rec))

    print("average system occupancy of Process1: {:.3f}".format(float(sum(Monitor1.sizes))/len(Monitor1.sizes)))
    print("average system occupancy of Process2: {:.3f}".format(float(sum(Monitor2.sizes))/len(Monitor2.sizes)))
    print("average system occupancy of Process3: {:.3f}".format(float(sum(Monitor3.sizes))/len(Monitor3.sizes)))
    print("average system occupancy of Process3_1: {:.3f}".format(float(sum(Monitor3_1.sizes)) / len(Monitor3_1.sizes)))

    print("utilization of Process1: {:2.2f}".format(Process1.working_time/RUN_TIME))
    print("utilization of Process2: {:2.2f}".format(Process2.working_time/RUN_TIME))
    print("utilization of Process3: {:2.2f}".format(Process3.working_time/RUN_TIME))
    print("utilization of Process3_1: {:2.2f}".format(Process3_1.working_time / RUN_TIME))

    # 각 packet의 시스템 체류 시간(리드타임)을 도수분포료(histogram)으로 플로팅
    #fig, axis = plt.subplots()
    #axis.hist(Sink.waits, bins=100, density=True)
    #axis.set_title("Histogram for waiting times")
    #axis.set_xlabel("time")
    #axis.set_ylabel("normalized frequency of occurrence")
    #fig.savefig("WaitHistogram.png")
    #plt.show()

    #fig, axis = plt.subplots()
    #axis.hist(Sink.arrivals, bins=100, density=True)
    #axis.set_title("Histogram for Sink Interarrival times")
    #axis.set_xlabel("time")
    #axis.set_ylabel("normalized frequency of occurrence")

    #fig.savefig("ArrivalHistogram.png")
    #plt.show()