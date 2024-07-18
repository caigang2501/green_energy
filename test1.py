import pandas as pd
from nsga2_gp.utils import feature2calcu
from nsga2_gp.population import Population
from nsga2_gp.individual import Individual
from example import constent
from example.constent import DEVICE_LIMIT as up
from example.constent import CONV_RATE as c
from example.constent import STORAGE_DEVICE as sd
import random

def calcu_feature(feature_calcu):
    individual = Individual()

    energy_start = [lmt/3 for lmt in up[9:]] # 电 热 冷 气
    plan = []
    individual.feature_run = []
    individual.feature_plan = []
    plan_season = {'summer':[],'excessive':[],'winter':[]}
    run_season = {'summer':[],'excessive':[],'winter':[]}

    for season in constent.SEASONS:
        stop = False
        season_load = constent.LOAD[season]
        energy_rest = energy_start.copy() 
        run = [[],[],[],[],[0,0]] # 输入功率
        run_out = [[],[],[]]
        time = 6
        for le,lh,lc,ft in zip(season_load[0],season_load[1],season_load[2],feature_calcu[season]):

            time = 1 if time+1>24 else time+1
            run[3] = energy_rest.copy()

            stb_cold,stb_heat = True,True
            # 5678: '地源热泵制冷','空气源热泵制冷','电制冷机','吸收式制冷机' 
            run[2] = [ft[5]*ft[9]*up[5],ft[6]*ft[10]*up[6],ft[7]*up[7],ft[8]*up[8]]
            run_out[2] = [ft[5]*ft[9]*up[5]*c[5][1],ft[6]*ft[10]*up[6]*c[6][1],ft[7]*up[7]*c[7],ft[8]*up[8]*c[8]]
            if sum(run_out[2])+energy_rest[2]*sd['cold'][1]>lc:
                if sum(run_out[2])-lc>0:
                    energy_rest[2] = energy_rest[2]*(1-sd['cold'][2]) + (sum(run_out[2])-lc)*sd['cold'][0]
                else:
                    energy_rest[2] = energy_rest[2]*(1-sd['cold'][2]) + (sum(run_out[2])-lc)/sd['cold'][1]
            else:
                stb_heat = False
            
            # 32456'燃气锅炉','热电产热','电锅炉','地源热泵产热','空气源热泵产热'
            run[1] = [ft[3]*up[3],ft[2]*up[2],ft[4]*up[4],ft[5]*(1-ft[-4])*up[5],ft[6]*(1-ft[-3])*up[6]]
            run_out[1] = [ft[3]*up[3]*c[3],ft[2]*up[2]*c[2][0],ft[4]*up[4]*c[4],ft[5]*(1-ft[-4])*up[5]*c[5][0],ft[6]*(1-ft[-3])*up[6]*c[6][0]]
            if sum(run_out[1])-run_out[2][3]+energy_rest[1]*sd['heat'][1]>lh:
                    if sum(run_out[1])-run[2][3]-lh>0:
                        energy_rest[1] = energy_rest[1]*(1-sd['heat'][2]) + (sum(run_out[1])-run[2][3]-lh)*sd['heat'][0]
                    else:
                        energy_rest[1] = energy_rest[1]*(1-sd['heat'][2]) + (sum(run_out[1])-run[2][3]-lh)/sd['heat'][1]
            else:
                stb_cold =  False    
            
            if not stb_cold or not stb_heat:
                df_wrong = pd.DataFrame(individual.feature_run)
                df_wrong.to_csv('example/result/test_wrong.csv',)
                print('wrong')
                return False
               
            # CH4

            gas_cost = run[1][0]+run[1][1]
            gas_chg = ft[11]*energy_start[0]*3-energy_rest[3] if energy_rest[3]<gas_cost/sd['gas'][1] else ft[11]*(energy_start[3]*3-energy_rest[3]+gas_cost/sd['gas'][1])-gas_cost/sd['gas'][1]

            # +储 -放
            if gas_chg>0:
                run[4][0] = gas_chg/sd['gas'][0]+gas_cost # '买燃气'
            else:
                run[4][0] = gas_chg*sd['gas'][1]+gas_cost
            energy_rest[3] = (energy_rest[3]+gas_chg)*(1-sd['gas'][2])

            # '风电','光伏','热电产电'
            elic_chg = ft[12]*energy_start[0]*3*0.8-(energy_rest[0]-energy_start[0]*3*0.2)
            energy_rest[0] = (energy_rest[0]+elic_chg)*(1-sd['elic'][2])
            elic_o = elic_chg/sd['elic'][0] if elic_chg>0 else elic_chg*sd['elic'][1]
            elic_cost = sum(run[2][:3])+sum(run[1][2:])+le-run_out[1][1]+elic_o
            run[0] = [ft[0]*up[0],ft[1]*up[1],run[1][1]]
            run_out[0] = [ft[0]*up[0],ft[1]*up[1],run[1][1]*c[1]]

            # rest_elic +卖 -买
            run[4][1] = sum(run_out[0])-elic_cost # '买卖电'

            # time,le,lh,lc,'风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵产热','空气源热泵产热','地源热泵制冷','空气源热泵制冷','电制冷机','吸收式制冷机','储电设备','储热设备','储冷设备','储气设备','买燃气','买卖电'
            individual.feature_run.append([time,le,lh,lc,*run[0],run[1][0],*run[1][2:],*run[2],*run[3],*run[4]])
            individual.feature_run[-1] = [round(p,1) for p in individual.feature_run[-1]]
            run_season[season].append([time,le,lh,lc,*run[0],run[1][0],*run[1][2:],*run[2],*run[3],*run[4]])

            # '风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵','空气源热泵','电制冷机','吸收式制冷机','储电设备','储热设备','储冷设备','储气设备'
            plan.append([*run[0],ft[3]*up[3],ft[4]*up[4],ft[5]*up[5],ft[6]*up[6],ft[7]*up[7],ft[8]*up[8],*run[3]])
            plan_season[season].append([*run[0],ft[3]*up[3],ft[4]*up[4],ft[5]*up[5],ft[6]*up[6],ft[7]*up[7],ft[8]*up[8],*run[3]])
        
    ch4_cost,elic_buy,elic_sell = 0,0,0
    for season in constent.SEASONS:    
        sum_plan = [sum(column) for column in zip(*plan_season[season])]  
        ch4_cost += (sum_plan[2]+sum_plan[3])*constent.SPECIAL_DAYS[season]
        elic_buy += sum([-row[-1] if row[-1]<0 else 0 for row in run_season[season]])*constent.SPECIAL_DAYS[season]
        elic_sell += sum([-row[-1] if row[-1]>0 else 0 for row in run_season[season]])*constent.SPECIAL_DAYS[season]
    
    individual.benefit['be'] = elic_buy
    individual.benefit['se'] = elic_sell
    individual.benefit['bg'] = ch4_cost
    individual.dis_co2 = constent.CH4_CO2*ch4_cost + constent.ELIC_CO2*elic_buy
    individual.feature_plan = [max(column) for column in zip(*plan)]
    # adjust(individual)

    individual.calcuted = True
    return individual

# for index, row in df.iterrows():
    # print(row.values)

df = pd.read_excel('example/result/ans.xlsx',sheet_name='feature0')
ft = [f for i,row in df.iterrows() for f in row.values]
individual = calcu_feature(feature2calcu(ft))
if not isinstance(individual,bool):
    with pd.ExcelWriter(f'example/result/test.xlsx') as writer:
        df_ansx = pd.DataFrame(individual.feature_run,columns=constent.FEATURE_RUN_COLUME)
        # df_ansx.to_csv(f'{save_path}ans_{i}.csv',index=False)
        df_ansx.to_excel(writer, sheet_name='run', index=False)

        df_ansx = pd.DataFrame([individual.feature_plan],columns=constent.FEATURE_PLAN_COLUME)
        df_ansx.to_excel(writer, sheet_name='规划', index=False)
        print('right')


