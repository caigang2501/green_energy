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
    for season in [constent.SUMMER_LOAD,constent.EXCESSIVE_LOAD,constent.WINTER_LOAD]:
        run = [[],[],[],[],[]] # 输入功率
        for le,lh,lc in zip(season[0],season[1],season[2]):
            run[3] = energy_rest.copy()

            # '地源热泵制冷','空气源热泵制冷','电制冷机','吸收式制冷机'
            while True:
                upl = individual.feature_plan[2]
                run[2] = [gr()*upl[0],gr()*upl[1],gr()*upl[2],gr()*upl[3]]
                if sum(run[2])+energy_rest[2]>lc:
                    run[1][3] -= run[2][0]
                    run[1][4] -= run[2][1]
                    energy_rest[2] += sum(run[2])-lc
                    break

            # '燃气锅炉','热电产热','电锅炉','地源热泵产热','空气源热泵产热'
            while True:
                upl = individual.feature_plan[1]
                run[1] = [gr()*upl[0],gr()*upl[1],gr()*upl[2],gr()*upl[3],gr()*upl[4]]
                
                if sum(run[1])-run[2][3]+energy_rest[1]>lh:
                    energy_rest[1] += sum(run[1])-run[2][3]-lh
                    break
            
            # CH4
            gas_cost = run[1][0]+run[1][1]
            bdl = 0 if energy_rest[3]>gas_cost else gas_cost-energy_rest[3]
            run[4][1] = random.uniform(bdl,individual.feature_plan[-1]-energy_rest[3]+gas_cost)
            energy_rest[3] += run[4][1]-gas_cost

            # '风电','光伏','热电产电'
            energy_chg = gr()*energy_start[0]*4-energy_rest
            energy_rest[0] += energy_chg
            elic_cost = sum(run[2][:3])+sum(run[1][2:])+le-run[1][1]+energy_chg
            upl = individual.feature_plan[0]
            run[0] = [gr()*upl[0],gr()*upl[1],run[1][1]]
            run[4][0] = -(sum(run[0])-elic_cost)

            individual.feature_run.append(deepcopy(run))

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


