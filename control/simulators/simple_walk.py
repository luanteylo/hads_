from control.simulators.models import Models

import numpy
import matplotlib.pyplot as plt


class SimpleWalk(Models):

    def __init__(self, threshold, start, prob_down, prob_up, l1=1, l2=100):

        super().__init__(threshold)
        self.prob_down = prob_down
        self.prob_up = prob_up
        self.position = [start]

        self.l1 = l1
        self.l2 = l2

    def get_current_position(self):
        return self.position[-1]

    def compute_next_position(self):
        U2 = numpy.random.rand()

        if U2 < self.prob_up and self.position[-1] < self.l2:
            self.position.append(self.position[-1] + 1)
        elif self.position[-1] > self.l1:
            self.position.append(self.position[-1] - 1)

    def plot(self):

        plt.style.use(['bmh'])
        fig, ax = plt.subplots(1)
        fig.suptitle("Simple Random Walk", fontsize=16)
        ax.set_xlabel('Time, t')
        ax.set_ylabel('Simulated Demand')

        x_axis = numpy.arange(0, len(self.position), 1)

        plt.plot(x_axis, self.position)

        plt.plot(self.position)
        plt.show()
