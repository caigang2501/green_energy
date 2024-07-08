import sys,os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from example import constent
from example.constent import DEVICE_LIMIT as up
from example.constent import CONV_RATE as c
from example.constent import STORAGE_DEVICE as sd
from nsga2_gp.problem import Problem
from nsga2_gp.evolution import Evolution
from nsga2_gp.individual import Individual
from nsga2_gp.utils import calcu_feature,feature_hour


save_path = 'example/result/'


def f1(individual:Individual):
    calcu_feature(individual)
    # '风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵','空气源热泵','电制冷机','吸收式制冷机','储电设备','储热设备','储冷设备','储气设备'
    
    constract_cost,run_cost = 0,0
    for cpc,con in zip(individual.feature_plan,constent.CONSTRA_COST):
        constract_cost += cpc*con
    
    run_cost = individual.benefit['be']*0.5+individual.benefit['bg']*3+individual.benefit['se']*0.3

    for row in individual.feature_run:
        buy,bs_elic = row[-2:]
        pass
    return run_cost*500+constract_cost

def f2(individual:Individual):
    return individual.dis_co2

def test(individual:Individual):
    
    
    v = 0
    for i in range(3):
        v += individual.feature_run[(i+1)*24-1][-4]
    return v

def f(individual:Individual):
    return f1(individual)+f2(individual)

def solve(hashrate):
    problem = Problem(objectives=[test])
    evo = Evolution(problem,50,20)
    evol = evo.evolve()
    func = [i.objectives for i in evol]
    with pd.ExcelWriter(f'{save_path}ans.xlsx') as writer:
        for i,individual in enumerate(evol):
            df_ansx = pd.DataFrame(individual.feature_run,columns=constent.FEATURE_RUN_COLUME)
            # df_ansx.to_csv(f'{save_path}ans_{i}.csv',index=False)
            name = ' '.join([str(round(cost)) for cost in individual.objectives])
            df_ansx.to_excel(writer, sheet_name=name, index=False)

            df_ansx = pd.DataFrame(feature_hour(individual.features),columns=constent.FEATURE_COLUME)
            df_ansx.to_excel(writer, sheet_name=f'feature{i}', index=False)
        df_ansx = pd.DataFrame([individual.feature_plan],columns=constent.FEATURE_PLAN_COLUME)
        df_ansx.to_excel(writer, sheet_name='规划', index=False)
    function1 = [i[0] for i in func]
    if len(func)==1:
        print(constent.objectives[0],constent.objectives[-1])
        plt.figure()
        # plt.plot(constent.objectives, marker='o')
        plt.plot(constent.cat1, marker='o')
        plt.plot(constent.cat2, marker='o')
        plt.plot(constent.cat3, marker='o')
        plt.text(len(constent.cat1)-1, constent.cat1[-1], 'bg', ha='left')
        plt.text(len(constent.cat2)-1, constent.cat2[-1], 'be', ha='left')
        plt.text(len(constent.cat3)-1, constent.cat3[-1], 'se', ha='left')
        plt.title('Line Chart Example')
        plt.xlabel('Index')
        plt.ylabel('Value')
    else:
        function2 = [i[1] for i in func]
        plt.xlabel('cost_money', fontsize=15)
        plt.ylabel('DIS_CO2', fontsize=15)
        plt.scatter(function1, function2)
        plt.savefig(f'{save_path}ans.png')
    
    # individual = evol[0]
    # constract_cost,run_cost = 0,0
    # for cpc,con in zip(individual.feature_plan,constent.CONSTRA_COST):
    #     constract_cost += cpc*con
    
    # run_cost = individual.benefit['be']+individual.benefit['bg']-individual.benefit['se']

    # print(constract_cost,run_cost)
    plt.show()
    return evol[0].feature_run

if __name__=='__main__':
    hashrate = constent.SUMMER_LOAD
    solve(hashrate)
