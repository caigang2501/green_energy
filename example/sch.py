import sys,os
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from nsga2.problem import Problem
from nsga2.evolution import Evolution
import matplotlib.pyplot as plt


def f1(x):
    return x ** 2
def f2(x):
    return (x - 2) ** 2

def f3(x,y):
    return x**2+y**2
def f4(x,y):
    return (x-2)**2+(y+2)**2

def solve():
    problem = Problem(objectives=[f1, f2], num_of_variables=1, variables_range=[(0,3)])
    evo = Evolution(problem,100,10)
    # evo = Evolution(problem)
    evol = evo.evolve()
    func = [i.objectives for i in evol]

    function1 = [i[0] for i in func]
    function2 = [i[1] for i in func]
    plt.xlabel('Function 1', fontsize=15)
    plt.ylabel('Function 2', fontsize=15)
    plt.scatter(function1, function2)
    plt.show()

# def calculate():
    
    # function1 = [i[0] for i in func]
    # function2 = [i[1] for i in func]
    # plt.xlabel('Function 1', fontsize=15)
    # plt.ylabel('Function 2', fontsize=15)
    # plt.scatter(function1, function2)
    # plt.show()

if __name__=='__main__':
    solve()