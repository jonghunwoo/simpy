import simpy
import numpy as np


## one to one communication
def processA(env, pipe_out):
    ## processA sending msg to processB
    for i in range(0, 10):
        p_name = "PA{:2d}".format(i)
        yield env.timeout(3)
        print("{:8.2f}: {} executed a1".format(env.now, p_name))
        yield env.timeout(5)
        print("{:8.2f}: {} executed a2".format(env.now, p_name))
        ## 상황에 따라서 메세지를 보냄
        if np.random.normal(0, 1) < 0.5:
            pipe_out.put("msg1")
        else:
            pipe_out.put("msg2")
        yield env.timeout(5)
        print("{:8.2f}: {} executed a3".format(env.now, p_name))
        print("{:8.2f}: {} completed".format(env.now, p_name))


def processB(env, pipe_in):
    for i in range(0, 10):
        p_name = "PB{:2d}".format(i)
        yield env.timeout(3)
        print("{:8.2f}: {} executed a1".format(env.now, p_name))
        print("{:8.2f}: {} is waiting for msg".format(env.now, p_name))
        ## 메세지를 받음.
        msg = yield pipe_in.get()
        ## 받은 메세지에 따라서 다른 행동을 취함
        if msg == 'msg1':
            print("{:8.2f}: {} get {}".format(env.now, p_name, msg))
            yield env.timeout(5)
            print("{:8.2f}: {} executed exc_a1".format(env.now, p_name))
        elif msg == 'msg2':
            print("{:8.2f}: {} get {}".format(env.now, p_name, msg))
            yield env.timeout(5)
            print("{:8.2f}: {} executed exc_a2".format(env.now, p_name))
        print("{:8.2f}: {} completed".format(env.now, p_name))


np.random.seed(42)
env = simpy.Environment()
pipe = simpy.Store(env)
env.process(processA(env, pipe_out=pipe))
env.process(processB(env, pipe_in=pipe))

env.run(until=50)