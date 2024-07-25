
import time,test
from example import constent
import matplotlib.pyplot as plt

def f(x):
    r = 0.05
    return r*(1+r)**x/((1+r)**x-1)

def plot_fun():

    x = list(range(1,20))
    y = [f(n) for n in x]
    plt.figure()
    plt.plot(x,y, marker='o',label='A')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.text(len(constent.cat3)-1, constent.cat3[-1], 'se', ha='left')
    plt.title('Iteration process')
    plt.xlabel('Iterations')
    plt.ylabel('Value')
    plt.show()

a= 1==2
print(a)

