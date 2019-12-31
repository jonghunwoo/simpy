import simpy
import numpy as np


def movie_goer(env, movie, num_tickets, theater):
    ## 영화보러 온 사람 프로세스
    ## 카운터에 리소스를 요청하고 기다리는 중에
    ## sold_out이라는 전역 이벤트가 발생하면 renege,
    ## 그렇찌 않을때는 다른 프로세스를 따름.
    with theater['counter'].request() as req:
        ## sold_out은 env.event(), 만약 다른 프로세스에서 succeed를 처리하면 아래에서 먼저 실행됨
        sold_out = theater['sold_out'][movie]
        result = yield req | sold_out
        if sold_out in result:
            ## 티켓이 다 팔렸음.
            theater['num_renegers'][movie] += 1
            ## 프로세스 종료
            env.exit()
        elif req in result:
            if num_tickets > theater['available'][movie]:
                ## 티켓이 있는데 부족할 경우에는 그냥 감
                print("{:7.1f}: we don't have enough tickets".format(env.now))
                yield env.timeout(0.5)
                env.exit()
            else:
                theater['available'][movie] -= num_tickets
                if theater['available'][movie] < 1:
                    ## 아래 보면 이벤트를 succeed로 변경함.
                    ## 따라서 만약 다른 프로세스에서 yield req | theater['sold_out'][movie] 등으로 참고하고 있을 경우
                    ## 아래 부분이 수행되는 즉시, yield 구문을 빠져오게 됨.
                    theater['sold_out'][movie].succeed()
                    theater['when_sold_out'][movie] = env.now
                    theater['available'][movie] = 0
                    print('{} is sold out'.format(movie))
                yield env.timeout(1)


def customer_arrivals(env, theater):
    ## exponential time마다 사람이 도착함
    ## 영화, 사람 수 등을 랜덤하게 고르고, 티켓이 남아있을 경우 이를 프로세스로 env에 넘겨줌
    while True:
        yield env.timeout(np.random.exponential(2))
        movie = np.random.choice(theater['movies'])
        num_tickets = np.random.randint(1, 6)
        ## 티켓이 남아지 않으면 새로운 사람이 프로세스로 넘어가지 않는다.
        if theater['available'][movie] != 0:
            print("{:7.1f}: {} customer arrived to see {}".format(env.now, num_tickets, movie))
            env.process(movie_goer(env, movie, num_tickets, theater))


np.random.seed(42)
env = simpy.Environment()

print("Movie renege")
## 이전에는 모두 class, process등으로 처리했는데 여기서는 딕셔너리로 데이터를 관리함.
## 딕셔너리에 Resource, event 등이 포함되어 있음.
## 경우에 따라 클래스로 만들지 않고, 아래처럼 딕셔너리로 관리하는 것이 편할 수도 있음.
movies = ['Die hard 2', "Kill bill", 'Resevoir Dogs']
theater = {
    'counter': simpy.Resource(env, capacity=1),
    'movies': movies,
    'available': {movie: 20 for movie in movies},
    'sold_out': {movie: env.event() for movie in movies},
    'when_sold_out': {movie: None for movie in movies},
    'num_renegers': {movie: 0 for movie in movies}
}

env.process(customer_arrivals(env, theater))
env.run(until=100)