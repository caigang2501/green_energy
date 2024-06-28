import sys,os
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from example.data import table_p
from nsga2_gp_example.problem import Problem
from nsga2_gp_example.evolution import Evolution
from nsga2_gp_example.individual import Individual
from nsga2_gp_example.utils import adjust
import matplotlib.pyplot as plt
import pandas as pd

C_WT = 0.019
C_PV = 0.01
C_EB = 0.04
C_HS = 0.023

N_EB = 0.97
N_SH = 0.87

A_CO2 = 0.853
SELL_PRICE = 0.4

save_path = 'example/result/'

def calculate(individual:Individual):
    cost_money = 0
    i = 0
    ans = []
    heat_rest = 960
    for peb in individual.features:
        a,b,c,d,e,f,g = table_p[i]# '时刻','电负荷','热负荷','冷负荷','风电出力上限','光伏出力上限','外购电价'
        pwt,ppv,qch,qdis = e,f,0,0
        if peb*N_EB-c>0:
            qch = peb*N_EB-c
            heat_rest += qch*N_SH
        else:
            qdis = c - peb*N_EB
            heat_rest -= qdis/N_SH
        elic_exchange = pwt+ppv-(b+peb)

        if pwt+ppv-(b+peb)>0:
            cost_money -= (pwt+ppv-(b+peb))*SELL_PRICE
        else:
            cost_money += ((b+peb)-(pwt+ppv))*g
        cost_money += pwt*C_WT + ppv*C_PV + peb*C_EB + max(qch,qdis)*C_HS
        ans.append([a,pwt,ppv,peb,qch,qdis,heat_rest,elic_exchange])
        i += 1
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

def test():
    individual = Individual()
    individual.features = [0,0,0,0,0,67.57731959,35.03092784,27.55670103,33.87628866,92.37113402,119.1958763,101.1649485,111.7319588,115.0721649,187.3814433,73.71134021,96.8556701,144.2886598,264,400,400,400,400,400]
    result = calculate(individual)
    print(result)
    df_ansx = pd.DataFrame(individual.ans,columns=['time','pwt','ppv','peb','qch','qdis','hhst','pgt'])
    name = ' '.join([str(round(cost)) for cost in individual.objectives])
    df_ansx.to_csv(f'{save_path}{name}.csv',index=False)

if __name__=='__main__':
    solve()
    # test()






