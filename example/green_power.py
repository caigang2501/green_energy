import sys,os
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from example import constent
from nsga2_gp.problem import Problem
from nsga2_gp.evolution import Evolution
from nsga2_gp.individual import Individual
from nsga2_gp.utils import feature_hour


save_path = 'example/result/'


def f1(individual:Individual):
    feature_run = [run for sp_day in constent.SPECIAL_9DAYS.keys() for run in individual.feature_run[sp_day]]

    constract_cost,run_cost = 0,0
    for cpc,con in zip(individual.feature_plan,constent.CONSTRA_COST):
        constract_cost += cpc*con
    
    run_cost = individual.benefit['be']+individual.benefit['bg']/constent.CH4_POWER*constent.CH4_PRICE+individual.benefit['se']

    for row in feature_run:
        buy,bs_elic = row[-2:]
        pass

    individual.economic = run_cost*constent.YEARS+constract_cost
    return individual.economic

def f2(individual:Individual):
    return individual.dis_co2

def f(individual:Individual):
    return f1(individual)+f2(individual)

def solve(load):

    constent.LOAD = constent.get_load(load)
    problem = Problem(objectives=[f])
    evo = Evolution(problem,4,20)
    evol = evo.evolve()
    with pd.ExcelWriter(f'{save_path}ans.xlsx') as writer:
        for i,individual in enumerate(evol):
            feature_run = [run for sp_day in constent.SPECIAL_9DAYS.keys() for run in individual.feature_run[sp_day]]
            df_ansx = pd.DataFrame(feature_run,columns=constent.FEATURE_RUN_COLUME)
            # df_ansx.to_csv(f'{save_path}ans_{i}.csv',index=False)
            name = ' '.join([str(round(cost)) for cost in individual.objectives])
            df_ansx.to_excel(writer, sheet_name=name, index=False)

            df_ansx = pd.DataFrame(feature_hour(individual.features),columns=constent.FEATURE_COLUME)
            df_ansx.to_excel(writer, sheet_name=f'feature{i}', index=False)
        df_ansx = pd.DataFrame([individual.feature_plan],columns=constent.FEATURE_PLAN_COLUME)
        df_ansx.to_excel(writer, sheet_name='规划', index=False)

    return evol

def main(load):
    evol = solve(load)
    func = [i.objectives for i in evol]
    function1 = [i[0] for i in func]
    if len(func)==1:
        print(constent.objectives[0],constent.objectives[-1])
        print(evol[0].dis_co2,evol[0].benefit)
        plt.figure()
        plt.plot(constent.objectives, marker='o',label='A')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        # plt.text(len(constent.cat3)-1, constent.cat3[-1], 'se', ha='left')
        plt.title('Iteration process')
        plt.xlabel('Iterations')
        plt.ylabel('Value')
    else:
        function2 = [i[1] for i in func]
        plt.xlabel('cost_money', fontsize=15)
        plt.ylabel('DIS_CO2', fontsize=15)
        plt.scatter(function1, function2)
    
    plt.savefig(f'{save_path}ans.png')
    plt.show()

if __name__=='__main__':
    load = {"workday": [30710.359865684313, 32424.963504136176, 26343.31836691784, 23402.050858972714, 31466.139246456245, 29404.1820705795, 32072.02460211823, 32745.146735856084, 31052.116954890793, 29286.697766835285, 33463.946078774075, 29636.647781847056, 39758.90971421667, 40463.81936424404, 24116.691469570425, 35138.40331794309, 2135.296922648603, 5151.845589285519, 6404.293285631984, 6217.690324626677, 5703.2162531203785, 8958.08853133498, 6629.073407347482, 4996.452096458904],
            "weekend": [30710.359865684313, 32424.963504136176, 26343.31836691784, 23402.050858972714, 31466.139246456245, 29404.1820705795, 32072.02460211823, 32745.146735856084, 31052.116954890793, 29286.697766835285, 33463.946078774075, 29636.647781847056, 39758.90971421667, 40463.81936424404, 24116.691469570425, 35138.40331794309, 2135.296922648603, 5151.845589285519, 6404.293285631984, 6217.690324626677, 5703.2162531203785, 8958.08853133498, 6629.073407347482, 4996.452096458904],
            "holiday": [30710.359865684313, 32424.963504136176, 26343.31836691784, 23402.050858972714, 31466.139246456245, 29404.1820705795, 32072.02460211823, 32745.146735856084, 31052.116954890793, 29286.697766835285, 33463.946078774075, 29636.647781847056, 39758.90971421667, 40463.81936424404, 24116.691469570425, 35138.40331794309, 2135.296922648603, 5151.845589285519, 6404.293285631984, 6217.690324626677, 5703.2162531203785, 8958.08853133498, 6629.073407347482, 4996.452096458904]}
    
    # load = {"workday": [0 for _ in range(24)],
    #         "weekend": [0 for _ in range(24)],
    #         "holiday": [0 for _ in range(24)]}
    
    main(load)
