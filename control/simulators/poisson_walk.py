from control.simulators.models import Models

import matplotlib.pyplot as plt
import numpy as np

import threading

class PoissonWalk(Models):
    def __init__(self, threshold, start, prob_up, prob_down, update_period_seconds=5, l1=1, l2=100):
        super().__init__(threshold)
        self.position = [start]
        self.prob_up = prob_up
        self.prob_down = prob_down
        self.l1 = l1
        self.l2 = l2

        self.update_period_seconds = update_period_seconds


    def __compute_next_position(self):
        U2 = np.random.rand()

        if U2 < self.prob_up / (self.prob_up + self.prob_down) and self.position[-1] < self.l2:
            self.position.append(self.position[-1] + 1)
        elif self.position[-1] > self.l1:
            self.position.append(self.position[-1] - 1)

    def get_current_position(self):
        return self.position[-1]

    def plot(self):
        plt.style.use(['bmh'])
        fig, ax = plt.subplots(1)
        fig.suptitle("Stochastic Model (Poisson)", fontsize=16)
        ax.set_xlabel('Time, second')
        ax.set_ylabel('Simulated Demand')

        x_axis = np.arange(0, len(self.position), 1)

        plt.plot(x_axis, self.position)

        plt.plot(self.position)

        f = plt.figure()

        f.savefig("foo.pdf")

        plt.show()

    def __str__(self):
        __name = 'poisson_walk'

        return "Model: {}\n" \
               "prob_up:{} prob_down:{}\n" \
               "L1:{} L2:{} Current position:{}".format(__name, self.prob_up,
                                                        self.prob_down,
                                                        self.l1,
                                                        self.l2,
                                                        self.get_current_position())



