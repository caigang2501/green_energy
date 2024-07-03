import sys,os,random
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import constent
from constent import DEVICE_LIMIT as up
from example.constent import CONV_RATE as c
from example.constent import STORAGE_DEVICE as sd
from nsga2_gp.problem import Problem
from nsga2_gp.evolution import Evolution
from nsga2_gp.individual import Individual
from nsga2_gp.utils import adjust,feature2calcu


save_path = 'example/result/'

def calcu_feature(individual:Individual):
    if not individual.child:
        return
    energy_start = [lmt/3 for lmt in up[9:]] # 电 热 冷 气
    plan = []
    feature_calcu = feature2calcu(individual.features)

    individual.feature_run = []
    individual.feature_plan = []

    for season in ['summer','excessive','winter']:
        season_load = constent.LOAD[season]
        energy_rest = energy_start.copy() # TODO 添加平衡调整后删除
        run = [[],[],[],[],[0,0]] # 输入功率
        run_out = [[],[],[]]
        time = 6
        for le,lh,lc,ft in zip(season_load[0],season_load[1],season_load[2],feature_calcu[season]):

            time = 1 if time>24 else time+1
            run[3] = energy_rest.copy()

            # 5678: '地源热泵制冷','空气源热泵制冷','电制冷机','吸收式制冷机' 
            while True:
                run[2] = [ft[5]*ft[9]*up[5],ft[6]*ft[10]*up[6],ft[7]*up[7],ft[8]*up[8]]
                run_out[2] = [ft[5]*ft[9]*up[5]*c[6],ft[6]*ft[10]*up[6]*c[7],ft[7]*up[7]*c[8],ft[8]*up[8]*c[9]]
                if sum(run_out[2])+energy_rest[2]*sd['cold'][1]>lc:
                    if sum(run_out[2])-lc>0:
                        energy_rest[2] = energy_rest[2]*(1-sd['cold'][2]) + (sum(run_out[2])-lc)*sd['cold'][0]
                    else:
                        energy_rest[2] = energy_rest[2]*(1-sd['cold'][2]) + (sum(run_out[2])-lc)/sd['cold'][1]
                    break
                else:
                    # TODO 后期改为调整
                    return 0

            # 32456'燃气锅炉','热电产热','电锅炉','地源热泵产热','空气源热泵产热'
            while True:
                run[1] = [ft[3]*up[3],ft[2]*up[2],ft[4]*up[4],ft[5]*(1-ft[-4])*up[5],ft[6]*(1-ft[-3])*up[6]]
                run_out[1] = [ft[3]*up[3]*c[2],ft[2]*up[2]*c[0],ft[4]*up[4]*c[3],ft[5]*(1-ft[-4])*up[5]*c[4],ft[6]*(1-ft[-3])*up[6]*c[5]]
                if sum(run_out[1])-run_out[2][3]+energy_rest[1]>lh:
                    energy_rest[1] += sum(run_out[1])-run_out[2][3]-lh
                    if sum(run_out[1])-lh>0:
                        energy_rest[1] = energy_rest[1]*(1-sd['heat'][2]) + (sum(run_out[2])-lc)*sd['heat'][0]
                    else:
                        energy_rest[1] = energy_rest[1]*(1-sd['heat'][2]) + (sum(run_out[2])-lc)/sd['heat'][1]
                    break
                else:
                    # TODO 后期改为调整
                    return 0                   
            
            # CH4
            gas_cost = run[1][0]+run[1][1]
            gas_chg = ft[11]*energy_start[0]*3-energy_rest[3] if energy_rest[3]<gas_cost/sd['gas'][1] else ft[11]*(energy_start[3]*3-energy_rest[3]+gas_cost/sd['gas'][1])-gas_cost/sd['gas'][1]
            
            # +储 -放
            if gas_chg>0:
                run[4][0] = gas_chg/sd['gas'][0]+gas_cost # '买燃气'
            else:
                run[4][0] = -gas_chg*sd['gas'][1]+gas_cost
            energy_rest[3] = (energy_rest[3]+gas_chg)*(1-sd['gas'][2])

            # '风电','光伏','热电产电'
            elic_chg = ft[12]*energy_start[0]*3*0.8-(energy_rest[0]-energy_start[0]*3*0.2)
            energy_rest[0] += (energy_rest[0]+elic_chg)*(1-sd['elic'][2])
            elic_o = elic_chg/sd['elic'][0] if elic_chg>0 else elic_chg*sd['elic'][1]
            elic_cost = sum(run_out[2][:3])+sum(run_out[1][2:])+le-run_out[1][1]+elic_o
            run[0] = [ft[0]*up[0],ft[1]*up[1],run[1][1]]
            run_out[0] = [ft[0]*up[0],ft[1]*up[1],run[1][1]*c[1]]

            # rest_elic +卖 -买
            run[4][1] = sum(run_out[0])-elic_cost # '买卖电'

            # time,le,lh,lc,'风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵产热','空气源热泵产热','地源热泵制冷','空气源热泵制冷','电制冷机','吸收式制冷机','储电设备','储热设备','储冷设备','储气设备','买燃气','买卖电'
            individual.feature_run.append([time,le,lh,lc,*run[0],run[1][0],*run[1][2:],*run[2],*run[3],*run[4]])

            # '风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵','空气源热泵','电制冷机','吸收式制冷机','储电设备','储热设备','储冷设备','储气设备'
            plan.append([*run[0],ft[3]*up[3],ft[4]*up[4],ft[5]*up[5],ft[6]*up[6],ft[7]*up[7],ft[8]*up[8],*run[3]])
    
    sum_plan = [sum(column) for column in zip(*plan)]  
    ch4_cost = sum_plan[2]+sum_plan[3]
    elic_buy = sum([-row[-1] if row[-1]<0 else 0 for row in individual.feature_run])
    individual.dis_co2 = constent.CH4_CO2*ch4_cost + constent.ELIC_CO2*elic_buy
    individual.feature_plan = [max(column) for column in zip(*plan)]
    # adjust(individual)


def f1(individual:Individual):
    calcu_feature(individual)
    # '风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵','空气源热泵','电制冷机','吸收式制冷机','储电设备','储热设备','储冷设备','储气设备'
    for buy,bs_elic in individual.feature_run[-2:]:
        pass
    return 

def f2(individual:Individual):
    return individual.dis_co2

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


