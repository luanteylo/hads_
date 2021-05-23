import random
import math
import sys

import logging

class Poisson:
    '''
    lambda : the average number of events that happen in one second
    seed : to initialize the uniform number generator
    '''

    def __init__(self, plambda, k=1, seed=None):
        self.random = random

        if seed is not None:
            self.random.seed(a=seed)
        else:
            seed = random.randrange(sys.maxsize)
            rng = random.Random(seed)
            self.random = rng

        logging.info("Poison SEED: {} ".format(seed))

        ''' 
        The average number of failures expected  to
        happen each second in a   Poisson Process, which is also
        called event rate or rate parameter. 
        '''
        self.plambda = plambda
        self.k = k

    def random_uniform(self):
        return self.random.uniform(0.0, 1.0)

    def __events_arrival_probability(self):
        return (self.plambda ** self.k * math.exp(-self.plambda)) / math.factorial(self.k)

    def event_happened(self):
        return self.random_uniform() <= self.__events_arrival_probability()

    def sample(self):
        return math.exp(1.0 - self.random_uniform()) / self.plambda

    def expected_cost(self, n, c, lambd, gamma, epsilon, R):

        sum = 0.0
        for k in range(int((epsilon * R) / n)):
            sum += (math.exp(-(lambd * (k - 1)) / epsilon) * math.floor(k / epsilon) * (1 - gamma)) + (
                math.exp(-(lambd * (k - 1)) / epsilon) * (k / epsilon))

        return c * n * (math.exp(lambd / epsilon) - 1) * sum
