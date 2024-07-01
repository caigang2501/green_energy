import matplotlib.pyplot as plt
import random


def plot_distribution(getrandom,*args,num_samples=10000):
    samples = [getrandom(*args) for _ in range(num_samples)]
    # samples = [i for i in samples if i<70]
    print(samples[0])
    print(min(samples),max(samples))
    plt.hist(samples, bins=30, density=True, alpha=0.7, color='b')
    plt.title('Random Number Distribution')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()

def getrandom(n):
    return sum([(2*random.random()-1)*(2*random.random()-1) for _ in range(n)])

def __get_delta():
    u = random.random()
    if u < 0.5:
        return (2 * u) ** (1 / (5 + 1)) - 1 # self.mutation_param = 5
    return 1 - (2 * (1 - u)) ** (1 / (5 + 1))



if __name__=='__main__':
    plot_distribution(random.uniform,3,6)






