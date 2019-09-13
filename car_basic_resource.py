import simpy

def car(env, name, bcs, driving_time, charge_duration):
    #Simulate driving to the BCS
    print('Car %s is created at %s with driving time %s' % (name, env.now, driving_time))
    yield env.timeout(driving_time)

    #Request one of its charging spots
    print('%s arriving at %s' % (name, env.now))
    with bcs.request() as req:
        yield req

        #Charging the battery
        print('%s starting to charge at %s' % (name, env.now))
        yield env.timeout(charge_duration)
        print('%s leaving the bca at %s' % (name, env.now))


env = simpy.Environment()
bcs = simpy.Resource(env, capacity = 2)

for i in range(4):
    env.process(car(env, 'Car %d' % i, bcs, i*2, 5))

env.run()
