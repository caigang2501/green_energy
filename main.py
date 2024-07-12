import sys,os
import pandas as pd

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
    
    run_cost = individual.benefit['be']*0.5+individual.benefit['bg']/constent.CH4_POWER*constent.CH4_PRICE+individual.benefit['se']*0.3

    for row in individual.feature_run:
        buy,bs_elic = row[-2:]
        pass
    return run_cost*500+constract_cost

def f2(individual:Individual):
    return individual.dis_co2

def f(individual:Individual):
    return f1(individual)+f2(individual)

def solve(hashrate):
    problem = Problem(objectives=[f])
    evo = Evolution(problem,50,20)
    evol = evo.evolve()
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

    spd_val,return_val = {},{'规划':individual.feature_plan}
    for dvc in constent.FEATURE_RUN_COLUME[4:]:
        spd_val[dvc] = constent.SUMMER_LOAD[0]
    for sp_day in constent.SPECIAL_DAYS1:
        return_val[sp_day] = spd_val

    
    return return_val

if __name__=='__main__':
    solve()

