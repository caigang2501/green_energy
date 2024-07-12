import random,math
import pandas as pd
from nsga2_gp.individual import Individual
from copy import deepcopy
from example import constent 
from example.constent import DEVICE_LIMIT as up
from example.constent import CONV_RATE as c
from example.constent import STORAGE_DEVICE as sd
from nsga2_gp.utils import adjust


class Problem:

    def __init__(self, objectives):
        self.num_of_objectives = len(objectives)
        self.objectives = objectives
        self.variables_range = (0,1)

    def generate_empty_individual(self):
            individual = Individual()
            individual.calcuted = False
            individual.features = [round(random.random(),2) for _ in range(936)]
            return individual
    

    def generate_individual(self):
        sp = random.random()
        sp1 = random.random()

        def gr(i):
            if i==0:
                return round(random.random(),5)*0.002
            elif i==1:
                return round(random.random(),5)
            else:
                return self.variables_range[1]*0.9+round(random.random()*0.1,5)
        
        def get_part(sc,k,change=False):
            pda = 2 #总part比上总容量
            choc = sorted(random.choices(list(range(100)),k=k))
            choc.insert(0,0),choc.append(100)
            part = [(choc[i+1]-choc[i])*0.01 for i in range(k+1)]
            if len(part)==4:
                power = [f*p for f,p in zip(part,up[5:9])]
                print(sum(power))
            if change:
                part = [(p+random.normalvariate(0,0.05))/pda for idx,p in enumerate(part)]
            else:
                part = [p/pda for idx,p in enumerate(part)]
            part = [0 if p<0 else p for p in part]
            if len(part)==4:
                power = [f*p*c for f,p,c in zip(part,up[5:9],sc)]
                print(part[0],up[5],sc[0])
                print(sum(power))
            return part
        
        def get_plan():
            # if sp<0.1:
            if constent.SP_INDIVIDUAL>0:
                
                ft = []
                spp = random.choice([1])
                if spp==1:
                    for i in range(6):
                        if i in [0,1]:
                            ft.append(gr(2))
                        elif i in [4,5]:
                            ft.append(gr(0)*3)
                        elif i in [2,3]:
                            if lh==0 and lc==0: 
                                if i==2:
                                    ft.append([gr(0),gr(0),gr(1),gr(1)])
                                else:
                                    ft.append([gr(1)*0.5,gr(0),gr(0),gr(0),gr(0)])
                            elif lh!=0 and lc==0: # 热负荷
                                if i==2: # 冷
                                    ft.append([gr(0),gr(0),gr(1),gr(1)])
                                else: # 热
                                    ft.append(get_part([c[2][0],c[3],c[4],[5][0],c[6][0]],4))
                            elif lh==0 and lc!=0: # 冷负荷
                                if i==2: # 冷
                                    part = get_part([c[5][1],c[6][1],c[7],c[8]],3)
                                    ft.append(part)
                                else: # 热
                                    part = get_part([c[2][0],c[3],c[4],[5][0],c[6][0]],4,change=False)
                                    part = [p*ft[2][3] for p in part]
                                    # ft[2][0],ft[2][1] = min(ft[2][0]+part[3],1),min(ft[2][0]+part[4],1)
                                    if ft[2][0]==0 or ft[2][1]==0:
                                        ft[2].extend([0,0])
                                    else:
                                        ft[2].extend([(ft[2][0]-part[3])/ft[2][0],(ft[2][0]-part[4])/ft[2][1]])
                                    ft.append(part[:3])
                            else:
                                ft.append(gr(1))
                elif spp==2:
                    pass
                ft = [ft[0],ft[1],*ft[3],*ft[2],ft[4],ft[5]]
            else:
                ft = [round(random.random(),5) for _ in range(13)]
            ft = [round(f,5) for f in ft]
            return ft
        individual = Individual()

        energy_start = [lmt/3 for lmt in up[9:]] # 电 热 冷 气
        energy_rest = energy_start.copy()
        plan = []
        plan_season = {'summer':[],'excessive':[],'winter':[]}
        run_season = {'summer':[],'excessive':[],'winter':[]}


        for season in constent.SEASONS:
            season_load = constent.LOAD[season]
            energy_rest = energy_start.copy() 
            run = [[],[],[],[],[0,0]] # 输入功率
            run_out = [[],[],[]] # 输出功率
            time = 6
            for le,lh,lc in zip(season_load[0],season_load[1],season_load[2]):
                # ft:'风电','光伏','热电联产','燃气锅炉','电锅炉','地源热泵','空气源热泵','电制冷机','吸收式制冷机','地源热泵制冷比例','空气源热泵制冷比例','充放然气','充放电'           
                time = 1 if time+1>24 else time+1
                run[3] = energy_rest.copy()

                stb_cold,stb_heat = False,False
                # 5678: '地源热泵制冷','空气源热泵制冷','电制冷机','吸收式制冷机' 
                while True:
                    ft = get_plan() 

                    run[2] = [ft[5]*ft[9]*up[5],ft[6]*ft[10]*up[6],ft[7]*up[7],ft[8]*up[8]]
                    run_out[2] = [ft[5]*ft[9]*up[5]*c[5][1],ft[6]*ft[10]*up[6]*c[6][1],ft[7]*up[7]*c[7],ft[8]*up[8]*c[8]]
                    if sum(run_out[2])+energy_rest[2]*sd['cold'][1]>lc:
                        if sum(run_out[2])-lc>0:
                            energy_rest[2] = energy_rest[2]*(1-sd['cold'][2]) + (sum(run_out[2])-lc)*sd['cold'][0]
                        else:
                            energy_rest[2] = energy_rest[2]*(1-sd['cold'][2]) + (sum(run_out[2])-lc)/sd['cold'][1]
                        stb_cold = True

                    # 32456'燃气锅炉','热电产热','电锅炉','地源热泵产热','空气源热泵产热'
                    run[1] = [ft[3]*up[3],ft[2]*up[2],ft[4]*up[4],ft[5]*(1-ft[-4])*up[5],ft[6]*(1-ft[-3])*up[6]]
                    run_out[1] = [ft[3]*up[3]*c[3],ft[2]*up[2]*c[2][0],ft[4]*up[4]*c[4],ft[5]*(1-ft[-4])*up[5]*c[5][0],ft[6]*(1-ft[-3])*up[6]*c[6][0]]
                    if sum(run_out[1])-run_out[2][3]+energy_rest[1]*sd['heat'][1]>lh:
                        if sum(run_out[1])-run[2][3]-lh>0:
                            energy_rest[1] = energy_rest[1]*(1-sd['heat'][2]) + (sum(run_out[1])-run[2][3]-lh)*sd['heat'][0]
                        else:
                            energy_rest[1] = energy_rest[1]*(1-sd['heat'][2]) + (sum(run_out[1])-run[2][3]-lh)/sd['heat'][1]
                        stb_heat = True 
                    
                    if stb_cold and stb_heat:
                        break
                    else:
                        # print(season,time)
                        stb_cold,stb_heat = False,False

                # CH4
                gas_cost = run[1][0]+run[1][1]
                gas_chg = ft[11]*energy_start[0]*3-energy_rest[3] if energy_rest[3]<gas_cost/sd['gas'][1] else ft[11]*(energy_start[3]*3-energy_rest[3]+gas_cost/sd['gas'][1])-gas_cost/sd['gas'][1]
                
                # '买燃气'
                if gas_chg>0:
                    run[4][0] = gas_chg/sd['gas'][0]+gas_cost 
                else:
                    run[4][0] = gas_chg*sd['gas'][1]+gas_cost
                    
                # +储 -放
                energy_rest[3] = (energy_rest[3]+gas_chg)*(1-sd['gas'][2])

                # '风电','光伏','热电产电'
                # elic_chg = ft[12]*energy_start[0]*3-energy_rest[0]
                elic_chg = ft[12]*energy_start[0]*3*0.8-(energy_rest[0]-energy_start[0]*3*0.2)
                energy_rest[0] = (energy_rest[0]+elic_chg)*(1-sd['elic'][2])
                elic_o = elic_chg/sd['elic'][0] if elic_chg>0 else elic_chg*sd['elic'][1]
                elic_cost = sum(run[2][:3])+sum(run[1][2:])+le-run_out[1][1]+elic_o
                run[0] = [ft[0]*up[0],ft[1]*up[1],run[1][1]]
                run_out[0] = [ft[0]*up[0],ft[1]*up[1],run[1][1]*c[2][1]]

                # rest_elic +卖 -买
                run[4][1] = sum(run_out[0])-elic_cost # '买卖电'

                individual.features.extend(ft.copy())

                # time,le,lh,lc,'风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵产热','空气源热泵产热','地源热泵制冷','空气源热泵制冷','电制冷机','吸收式制冷机','储电设备','储热设备','储冷设备','储气设备','买燃气','买卖电'
                individual.feature_run.append([time,le,lh,lc,*run[0],run[1][0],*run[1][2:],*run[2],*run[3],*run[4]])
                individual.feature_run[-1] = [round(p,1) for p in individual.feature_run[-1]]
                run_season[season].append([time,le,lh,lc,*run[0],run[1][0],*run[1][2:],*run[2],*run[3],*run[4]])

                # '风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵','空气源热泵','电制冷机','吸收式制冷机','储电设备','储热设备','储冷设备','储气设备'
                plan.append([*run[0],ft[3]*up[3],ft[4]*up[4],ft[5]*up[5],ft[6]*up[6],ft[7]*up[7],ft[8]*up[8],*run[3]])
                plan_season[season].append([*run[0],ft[3]*up[3],ft[4]*up[4],ft[5]*up[5],ft[6]*up[6],ft[7]*up[7],ft[8]*up[8],*run[3]])
                
                # df_ansx = pd.DataFrame(individual.feature_run,columns=constent.FEATURE_RUN_COLUME)
                # df_ansx.to_csv('test.csv')
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

        constent.SP_INDIVIDUAL -= 1
        return individual

    def calculate_objectives(self, individual):
        individual.objectives = [f(individual) for f in self.objectives]
