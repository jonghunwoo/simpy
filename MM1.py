"""
Example use of SimComponents to simulate a packet queue with M/M/1 characteristics.
Copyright 2014 Dr. Greg M. Bernstein
Released under the MIT license
"""
import random
import functools
import simpy
import matplotlib.pyplot as plt
from SimComponents import PacketGenerator, PacketSink, SwitchPort, PortMonitor

if __name__ == '__main__':

    # Set up arrival and packet size distributions
    # Using Python functools to create callable functions for random variates with fixed parameters
    # each call to these will produce a new random value

    adist = functools.partial(random.randrange, 1,10) # arrival distribution
    #sdist = functools.partial(random.expovariate, 0.1)  # successive sizes of packets
    sdist = functools.partial(random.randint, 1,1)
    samp_dist = functools.partial(random.expovariate, 1)
    port_rate1 = 3
    port_rate2 = 3

    # Create the SimPy environment
    env = simpy.Environment()

    # Create the packet generators and sink
    ps = PacketSink(env, 'Sink', debug=False, rec_arrivals=True)
    pg = PacketGenerator(env, "Source", adist, sdist)
    switch_port1 = SwitchPort(env, 'Port1', port_rate1, qlimit=7, limit_bytes = False)
    switch_port2 = SwitchPort(env, 'Port2', port_rate2, qlimit=5, limit_bytes = False)

    # Using a PortMonitor to track queue sizes over time
    pm1 = PortMonitor(env, switch_port1, samp_dist)
    pm2 = PortMonitor(env, switch_port2, samp_dist)

    # Wire packet generators, switch ports, and sinks together
    pg.out = switch_port1
    switch_port1.out = switch_port2
    switch_port2.out = ps

    # Run it
    env.run(until=100)

    print('#'*80)
    print("Results of simulation")
    print('#'*80)
    print("Lead time of Last 10 packets: "  + ", ".join(["{:.3f}".format(x) for x in ps.waits[-10:]]))
    print("Switch_port1: Last 10 queue sizes: {}".format(pm1.sizes[-10:]))
    print("Switch_port2: Last 10 queue sizes: {}".format(pm2.sizes[-10:]))
    print("PortSink: Last 10 sink arrival times: " + ", ".join(["{:.3f}".format(x) for x in ps.arrivals[-10:]])) # 모든 공정을 거친 packet이 최종 노드에 도착하는 시간 간격 - TH 계산 가능
    print("PortSink: average wait = {:.3f}".format(sum(ps.waits)/len(ps.waits))) # 모든 packet들의 리드타임의 평
    print("received: {}, dropped {}, sent {}".format(switch_port1.packets_rec, switch_port1.packets_drop, pg.packets_sent))
    print("loss rate: {}".format(float(switch_port1.packets_drop)/switch_port1.packets_rec)) # SwitchPort들이 qlimit에 도달한 상태에서 packet이 도착하면 loss로 처리학고 있음 - 대기하도록 SimComponent 코드 수정 필요
    print("average system occupancy of port1: {:.3f}".format(float(sum(pm1.sizes))/len(pm1.sizes)))
    print("average system occupancy of port2: {:.3f}".format(float(sum(pm2.sizes)) / len(pm2.sizes)))

    # 각 packet의 시스템 체류 시간(리드타임)을 도수분포료(histogram)으로 플로팅
    fig, axis = plt.subplots()
    axis.hist(ps.waits, bins=100, density=True)
    axis.set_title("Histogram for waiting times")
    axis.set_xlabel("time")
    axis.set_ylabel("normalized frequency of occurrence")
    fig.savefig("WaitHistogram.png")
    plt.show()

    fig, axis = plt.subplots()
    axis.hist(ps.arrivals, bins=100, density=True)
    axis.set_title("Histogram for Sink Interarrival times")
    axis.set_xlabel("time")
    axis.set_ylabel("normalized frequency of occurrence")

    fig.savefig("ArrivalHistogram.png")
    plt.show()