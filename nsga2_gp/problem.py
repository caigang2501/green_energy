from individual import Individual
import random,math
from copy import deepcopy
from example import constent 


class Problem:

    def __init__(self, objectives):
        self.num_of_objectives = len(objectives)
        self.objectives = objectives

    def generate_individual(self):
        def gr():
            return round(random.random(),2)
        
        individual = Individual()

        # 规划
        dvc = [random.randint(0,mx) for mx in constent.DEVICE_LIMIT]
        individual.feature_plan = [[dvc[0],dvc[1],dvc[2]],[dvc[3],dvc[2],dvc[4],dvc[5],dvc[6]],[dvc[5],dvc[6],dvc[7],dvc[8]],dvc[9:]]

        # 运行
        energy_start = [lmt/2 for lmt in individual.feature_plan[-4:]] # 电 热 冷 气
        energy_rest = energy_start.copy()
        
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
                energy_chg = gr()*energy_start[0]-energy_rest
                energy_rest[0] += energy_chg
                elic_cost = sum(run[2][:3])+sum(run[1][2:])-run[1][1]+energy_chg
                upl = individual.feature_plan[0]
                run[0] = [gr()*upl[0],gr()*upl[1],run[1][1]]
                run[4][0] = -(sum(run[0])-elic_cost)

                individual.feature_run.append(deepcopy(run))
        
        individual.features.extend(dvc)
        for r in individual.feature_run:
            individual.features.extend([n for sr in r for n in sr]) 

        individual.range.extend([[0,upl] for upl in constent.DEVICE_LIMIT])
        for r in individual.feature_run:
            individual.range.extend([n for sr in r for n in sr]) 
        
        return individual


    def calculate_objectives(self, individual):
        individual.objectives = [f(individual) for f in self.objectives]
