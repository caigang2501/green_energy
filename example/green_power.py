import sys,os
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import constent
from nsga2_gp.problem import Problem
from nsga2_gp.evolution import Evolution
from nsga2_gp.individual import Individual
from nsga2_gp.utils import adjust
import matplotlib.pyplot as plt
import pandas as pd

save_path = 'example/result/'

def calculate(individual:Individual):
    cost_money = 0
    i = 0
    ans = []
    for peb in individual.features:
        pass
    individual.ans = ans
    return cost_money

def f1(individual:Individual):
    calculate(individual)
    adjust(individual)
    return calculate(individual)

def f2(individual:Individual):
    elic_buy = sum([-row[-1] if row[-1]<0 else 0 for row in individual.ans])
    return elic_buy*A_CO2

def solve():
    problem = Problem(objectives=[f1,f2])
    evo = Evolution(problem,10000,15)
    evol = evo.evolve()
    with pd.ExcelWriter(f'{save_path}ans.xlsx') as writer:
        for i,individual in enumerate(evol):
            df_ansx = pd.DataFrame(individual.ans,columns=['time','pwt','ppv','peb','qch','qdis','hhst','pgt'])
            # df_ansx.to_csv(f'{save_path}ans_{i}.csv',index=False)
            name = ' '.join([str(round(cost)) for cost in individual.objectives])
            df_ansx.to_excel(writer, sheet_name=name, index=False)
    func = [i.objectives for i in evol]

    function1 = [i[0] for i in func]
    function2 = [i[1] for i in func]
    plt.xlabel('cost_money', fontsize=15)
    plt.ylabel('DIS_CO2', fontsize=15)
    plt.scatter(function1, function2)
    plt.savefig(f'{save_path}ans.png')
    plt.show()


