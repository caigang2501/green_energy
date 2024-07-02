from individual import Individual
import random,math
from copy import deepcopy
from example import constent 
from example.constent import DEVICE_LIMIT as up
from utils import adjust


class Problem:

    def __init__(self, objectives):
        self.num_of_objectives = len(objectives)
        self.objectives = objectives
        self.variables_range = (0,1)

    def generate_individual(self):
        individual = Individual()

        # 运行
        energy_start = [lmt/3 for lmt in up[9:]] # 电 热 冷 气
        energy_rest = energy_start.copy()
        plan = []

        for season in [constent.SUMMER_LOAD,constent.EXCESSIVE_LOAD,constent.WINTER_LOAD]:
            run = [[],[],[],[],[0,0]] # 输入功率
            ft = [round(random.random(),2) for _ in range(13)]
            for le,lh,lc in zip(season[0],season[1],season[2]):
                run[3] = energy_rest.copy()

                # 5678: '地源热泵制冷','空气源热泵制冷','电制冷机','吸收式制冷机' 
                while True:
                    run[2] = [ft[5]*ft[9]*up[5],ft[6]*ft[10]*up[6],ft[7]*up[7],ft[8]*up[8]]
                    if sum(run[2])+energy_rest[2]>lc:
                        energy_rest[2] += sum(run[2])-lc
                        break
                    else:
                        for i in range(6):
                            ft[i+5] = round(random.random(),2)


                # 32456'燃气锅炉','热电产热','电锅炉','地源热泵产热','空气源热泵产热'
                while True:
                    run[1] = [ft[3]*up[3],ft[2]*up[2],ft[4]*up[4],ft[5]*(1-ft[-4])*up[5],ft[6]*(1-ft[-3])*up[6]]
                    if sum(run[1])-run[2][3]+energy_rest[1]>lh:
                        energy_rest[1] += sum(run[1])-run[2][3]-lh
                        break
                    else:
                        for i in range(3):
                            ft[i+2] = round(random.random(),2)                        
                
                # CH4
                gas_cost = run[1][0]+run[1][1]
                gas_chg = ft[11]*energy_start[0]*3-energy_rest[3] if energy_rest[3]<gas_cost else ft[11]*(energy_start[3]*3-energy_rest[3]+gas_cost)-gas_cost
                
                run[4][0] = gas_chg+gas_cost # '买燃气'
                energy_rest[3] += run[4][1]-gas_cost

                # '风电','光伏','热电产电'
                elic_chg = ft[12]*energy_start[0]*3-energy_rest[0]
                energy_rest[0] += elic_chg
                elic_cost = sum(run[2][:3])+sum(run[1][2:])+le-run[1][1]+elic_chg
                run[0] = [ft[0]*up[0],ft[1]*up[1],run[1][1]]

                run[4][1] = -(sum(run[0])-elic_cost) # '买卖电'

                # ft:'风电','光伏','热电联产','燃气锅炉','电锅炉','地源热泵','空气源热泵','电制冷机','吸收式制冷机','地源热泵制冷比例','空气源热泵制冷比例','充放然气','充放电'
                individual.features.extend(ft.copy())

                #'风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵产热','空气源热泵产热','地源热泵制冷','空气源热泵制冷','电制冷机','吸收式制冷机','储电设备','储热设备','储冷设备','储气设备','买燃气','买卖电'
                individual.feature_run.append([*run[0],run[1][0],*run[1][2:],*run[2],*run[3]],*run[4])

                # '风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵','空气源热泵','电制冷机','吸收式制冷机','储电设备','储热设备','储冷设备','储气设备'
                plan.append([*run[0],ft[3]*up[3],ft[4]*up[4],ft[5]*up[5],ft[6]*up[6],ft[7]*up[7],ft[8]*up[8],*run[3]])
            
            individual.feature_plan = [max(column) for column in zip(*plan)]

            # adjust(individual)

        return individual


    def calculate_objectives(self, individual):
        individual.objectives = [f(individual) for f in self.objectives]
