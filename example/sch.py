import sys,os
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from nsga2.problem import Problem
from nsga2.evolution import Evolution
from nsga2.individual import Individual
import matplotlib.pyplot as plt


def f1(x):
    return x ** 2
def f2(x):
    return (x - 2) ** 2

def f3(features):
    return sum(features)

def solve():
    problem = Problem(objectives=[f3], num_of_variables=1, variables_range=[(0,1)])
    evo = Evolution(problem,50,20)
    # evo = Evolution(problem)
    evol = evo.evolve()
    print(evol[0].objectives)
    # print(evol[0].features[:100])


if __name__=='__main__':
    solve()