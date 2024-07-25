import random,copy
import requests
import pandas as pd
from nsga2_gp.population import Population
from nsga2_gp.individual import Individual
from example import constent
from example.constent import DEVICE_LIMIT as up
from example.constent import CONV_RATE as c
from example.constent import STORAGE_DEVICE as sd




def to_excel(evol,name):
    with pd.ExcelWriter(f'example/result/{name}.xlsx') as writer:
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

def download_by_requests(path,download_path):
    result = requests.get(path)
    with open(download_path, 'wb') as f:
        f.write(result.content)

def calcu_feature(individual:Individual):
    energy_start = [lmt/3 for lmt in up[9:]] # 电 热 冷 气
    plan = []
    feature_calcu = feature2calcu(individual.features)
    
    individual.feature_plan = []
    plan_season = copy.deepcopy(constent.EMPTY_SEASON)
    rc = constent.RATED_CAPACITY
    

    for season in constent.SPECIAL_9DAYS.keys():
        ss,day = season.split('_')
        season_load = constent.st.load[season]
        energy_rest = energy_start.copy() 
        run = [[],[],[],[],[0,0]] # 输入功率
        run_out = [[],[],[]]
        time = 6
        for le,lh,lc,ft,pw,pv in zip(season_load[0],season_load[1],season_load[2],feature_calcu[season],constent.PW[ss],constent.PV[ss]):
            # ft = [f if i in [] else f for i,f in enumerate(ft)]
            time = 1 if time+1>24 else time+1
            run[3] = energy_rest.copy()
            
            # 5678: '地源热泵制冷','空气源热泵制冷','电制冷机','吸收式制冷机' 
            run[2] = [ft[5]*ft[9]*rc/c[5][1],ft[6]*ft[10]*rc/c[6][1],ft[7]*rc/c[7],ft[8]*rc/c[8]]
            run_out[2] = [ft[5]*ft[9]*rc,ft[6]*ft[10]*rc,ft[7]*rc,ft[8]*rc]
            if sum(run_out[2])+energy_rest[2]*sd['cold'][1]>lc:
                if sum(run_out[2])-lc>0:
                    energy_rest[2] = energy_rest[2]*(1-sd['cold'][2]) + (sum(run_out[2])-lc)*sd['cold'][0]
                else:
                    energy_rest[2] = energy_rest[2]*(1-sd['cold'][2]) + (sum(run_out[2])-lc)/sd['cold'][1]
            else:
                # print('cold',sum(run_out[2])-lc,season,time)
                return False
                
            # 32456'燃气锅炉','热电产热','电锅炉','地源热泵产热','空气源热泵产热'
            run[1] = [ft[3]*rc/c[3],ft[2]*rc/c[2][0],ft[4]*rc/c[4],ft[5]*(1-ft[-4])*rc/c[5][0],ft[6]*(1-ft[-3])*rc/c[6][0]]
            run_out[1] = [ft[3]*rc,ft[2]*rc,ft[4]*rc,ft[5]*(1-ft[-4])*rc,ft[6]*(1-ft[-3])*rc]
            if sum(run_out[1])-run_out[2][3]+energy_rest[1]*sd['heat'][1]>lh:
                    if sum(run_out[1])-run[2][3]-lh>0:
                        energy_rest[1] = energy_rest[1]*(1-sd['heat'][2]) + (sum(run_out[1])-run[2][3]-lh)*sd['heat'][0]
                    else:
                        energy_rest[1] = energy_rest[1]*(1-sd['heat'][2]) + (sum(run_out[1])-run[2][3]-lh)/sd['heat'][1]
            else:
                # print('heat',sum(run_out[1])-run[2][3]-lh,season,time)
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
            run[0] = [ft[0]*up[0]*pw,ft[1]*up[1]*pv,run[1][1]]
            run_p = [ft[0]*up[0],ft[1]*up[1],run[1][1]]
            run_out[0] = [ft[0]*up[0],ft[1]*up[1],run[1][1]*c[2][1]]

            # rest_elic +卖 -买
            run[4][1] = sum(run_out[0])-elic_cost # '买卖电'

            # time,le,lh,lc,'风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵产热','空气源热泵产热','地源热泵制冷','空气源热泵制冷','电制冷机','吸收式制冷机','储电设备','储热设备','储冷设备','储气设备','买燃气','买卖电'
            individual.feature_run[season].append([season,time,le,lh,lc,*run[0],run[1][0],*run[1][2:],*run[2],*run[3],*run[4]])
            # '风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵','空气源热泵','电制冷机','吸收式制冷机','储电设备','储热设备','储冷设备','储气设备'
            plan.append([*run_p,run[1][0],run[1][2],run[1][3]+run[2][0],run[1][4]+run[2][1],run[2][2],run[2][3],*run[3]])
            plan_season[season].append([*run[0],*run_p,run[1][0],run[1][2],run[1][3]+run[2][0],run[1][4]+run[2][1],run[2][2],run[2][3],*run[3]])
        
    ch4_cost,elic_buy,elic_sell = 0,0,0
    for season in constent.SPECIAL_9DAYS.keys():    
        sum_plan = [sum(column) for column in zip(*plan_season[season])]  
        ch4_cost += (sum_plan[2]+sum_plan[3])*constent.SPECIAL_9DAYS[season]
        elic_buy += sum([-row[-1]*p if row[-1]<0 else 0 for row,p in zip(individual.feature_run[season],constent.ELEC_SELL_PRICE)])*constent.SPECIAL_9DAYS[season]
        elic_sell += sum([-row[-1]*p if row[-1]>0 else 0 for row,p in zip(individual.feature_run[season],constent.ELEC_SELL_PRICE)])*constent.SPECIAL_9DAYS[season]
         
    individual.benefit['be'] = elic_buy/10000
    individual.benefit['se'] = elic_sell/10000
    individual.benefit['bg'] = ch4_cost
    individual.dis_co2 = constent.CH4_CO2*ch4_cost + constent.ELIC_CO2*elic_buy
    individual.feature_plan = [max(column) for column in zip(*plan)]

    stg = list(zip(*plan))[-4:]
    chg = [max([s[i+1]-s[i] for i in range(23)]) for s in stg]
    dis_chg = [max([s[i]-s[i+1] for i in range(23)]) for s in stg]
    individual.feature_plan.extend(chg+dis_chg)
    # adjust(individual)

    return True


def sutable_individual(individual:Individual):
    result = []
    energy_start = [lmt/3 for lmt in up[9:]] # 电 热 冷 气
    plan = []
    feature_calcu = feature2calcu(individual.features)
    
    individual.feature_plan = []
    plan_season = copy.deepcopy(constent.EMPTY_SEASON)
    rc = constent.RATED_CAPACITY
    

    for season in constent.SPECIAL_9DAYS.keys():
        ss,day = season.split('_')
        season_load = constent.st.load[season]
        energy_rest = energy_start.copy() 
        run = [[],[],[],[],[0,0]] # 输入功率
        run_out = [[],[],[]]
        time = 6
        i = 0
        for le,lh,lc,ft,pw,pv in zip(season_load[0],season_load[1],season_load[2],feature_calcu[season],constent.PW[ss],constent.PV[ss]):

            time = 1 if time+1>24 else time+1
            run[3] = energy_rest.copy()
            
            # 5678: '地源热泵制冷','空气源热泵制冷','电制冷机','吸收式制冷机' 
            run[2] = [ft[5]*ft[9]*rc/c[5][1],ft[6]*ft[10]*rc/c[6][1],ft[7]*rc/c[7],ft[8]*rc/c[8]]
            run_out[2] = [ft[5]*ft[9]*rc,ft[6]*ft[10]*rc,ft[7]*rc,ft[8]*rc]
            if sum(run_out[2])+energy_rest[2]*sd['cold'][1]>lc:
                if sum(run_out[2])-lc>0:
                    energy_rest[2] = energy_rest[2]*(1-sd['cold'][2]) + (sum(run_out[2])-lc)*sd['cold'][0]
                else:
                    energy_rest[2] = energy_rest[2]*(1-sd['cold'][2]) + (sum(run_out[2])-lc)/sd['cold'][1]
            else:
                print('cold',sum(run_out[2])-lc,season,time)
                return False
                
            # 32456'燃气锅炉','热电产热','电锅炉','地源热泵产热','空气源热泵产热'
            run[1] = [ft[3]*rc/c[3],ft[2]*rc/c[2][0],ft[4]*rc/c[4],ft[5]*(1-ft[-4])*rc/c[5][0],ft[6]*(1-ft[-3])*rc/c[6][0]]
            run_out[1] = [ft[3]*rc,ft[2]*rc,ft[4]*rc,ft[5]*(1-ft[-4])*rc,ft[6]*(1-ft[-3])*rc]
            if sum(run_out[1])-run_out[2][3]+energy_rest[1]*sd['heat'][1]>lh:
                    # if season=='summer_workday' and time==8:
                    #     print('test')
                    #     print(energy_rest[1]*(1-sd['heat'][2]) + (sum(run_out[1])-run[2][3]-lh)*sd['heat'][0])
                    #     print(energy_rest[1]*(1-sd['heat'][2]) + (sum(run_out[1])-run[2][3]-lh)/sd['heat'][1])
                    if sum(run_out[1])-run[2][3]-lh>0:
                        energy_rest[1] = energy_rest[1]*(1-sd['heat'][2]) + (sum(run_out[1])-run[2][3]-lh)*sd['heat'][0]
                    else:
                        energy_rest[1] = energy_rest[1]*(1-sd['heat'][2]) + (sum(run_out[1])-run[2][3]-lh)/sd['heat'][1]
            else:
                print('heat',sum(run_out[1])-run[2][3]-lh,season,time)
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
            run[0] = [ft[0]*up[0]*pw,ft[1]*up[1]*pv,run[1][1]]
            run_p = [ft[0]*up[0],ft[1]*up[1],run[1][1]]
            run_out[0] = [ft[0]*up[0],ft[1]*up[1],run[1][1]*c[2][1]]

            # rest_elic +卖 -买
            run[4][1] = sum(run_out[0])-elic_cost # '买卖电'

            # time,le,lh,lc,'风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵产热','空气源热泵产热','地源热泵制冷','空气源热泵制冷','电制冷机','吸收式制冷机','储电设备','储热设备','储冷设备','储气设备','买燃气','买卖电'
            e = individual.feature_run[season][i]==[season,time,le,lh,lc,*run[0],run[1][0],*run[1][2:],*run[2],*run[3],*run[4]]
            if not e:
                result.append([season,time])
                print(individual.feature_run[season][i])
                print([season,time,le,lh,lc,*run[0],run[1][0],*run[1][2:],*run[2],*run[3],*run[4]])
                pass
            # '风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵','空气源热泵','电制冷机','吸收式制冷机','储电设备','储热设备','储冷设备','储气设备'
            plan.append([*run_p,run[1][0],run[1][2],run[1][3]+run[2][0],run[1][4]+run[2][1],run[2][2],run[2][3],*run[3]])
            plan_season[season].append([*run[0],*run_p,run[1][0],run[1][2],run[1][3]+run[2][0],run[1][4]+run[2][1],run[2][2],run[2][3],*run[3]])
        
            i += 1

    return True


def adjust(individual:Individual):
    eng_start = individual.feature_run[0][11:15]
    for s in range(3):
        elic_rest,heat_rest,cold_rest,gas_rest = individual.feature_run[24*(s+1)-1][11:15]

        # 气
        if gas_rest<eng_start[3]:
            individual.feature_run[-2] += eng_start[3]-gas_rest

        i = -1
        # while eng_rest<start[engi]:
        #     if delt_heat+heat_rest_p<960:
        #         heat_rest_p += delt_heat
        #         individual.features[i] = QEB_MAX
        #         i -= 1
        #     else:
        #         a = 0.05
        #         while heat_rest_p+delt_heat*a<960:
        #             a += 0.05
        #         heat_rest_p += delt_heat*a
        #         individual.features[i] += (QEB_MAX-individual.features[i])*a
            # individual.ans[i][3] = individual.features[i]
    return individual

def feature2calcu(feature):
    feature_calcu = copy.deepcopy(constent.EMPTY_SEASON)
    for i,season in enumerate(constent.SPECIAL_9DAYS.keys()):
        for j in range(24):
            index = i*13*24+13*j
            feature_calcu[season].append(feature[index:index+13])
    return feature_calcu

def feature_hour(feature):
    feature_cat = []
    for i,season in enumerate(constent.SPECIAL_9DAYS.keys()):
        for j in range(24):
            index = i*13*24+13*j
            feature_cat.append(feature[index:index+13])
    return feature_cat


class NSGA2Utils:

    # num_of_tour_particips： 用于选取父类的子集个数
    def __init__(self, problem,num_of_individuals=50,
                 num_of_tour_particips=2, tournament_prob=0.9, crossover_param=2, mutation_param=5):

        self.problem = problem
        self.num_of_individuals = num_of_individuals
        self.num_of_tour_particips = num_of_tour_particips
        self.tournament_prob = tournament_prob
        self.crossover_param = crossover_param
        self.mutation_param = mutation_param

    def create_initial_population(self):
        population = Population()
        for _ in range(self.num_of_individuals):
            individual = self.problem.generate_individual()
            # if not sutable_individual(individual):
            #     print('unsutable_individual')
            self.problem.calculate_objectives(individual)
            population.append(individual)
        return population

    def fast_nondominated_sort(self, population):
        population.fronts = [[]]
        for individual in population:
            individual.domination_count = 0
            individual.dominated_solutions = []
            for other_individual in population:
                if individual.dominates(other_individual):
                    individual.dominated_solutions.append(other_individual)
                elif other_individual.dominates(individual):
                    individual.domination_count += 1
            if individual.domination_count == 0:
                individual.rank = 0
                population.fronts[0].append(individual)
        i = 0
        while len(population.fronts[i]) > 0:
            temp = []
            for individual in population.fronts[i]:
                for other_individual in individual.dominated_solutions:
                    other_individual.domination_count -= 1
                    if other_individual.domination_count == 0:
                        other_individual.rank = i + 1
                        temp.append(other_individual)
            i = i + 1
            population.fronts.append(temp)

    def calculate_crowding_distance(self, front):
        if len(front) > 0:
            solutions_num = len(front)
            for individual in front:
                individual.crowding_distance = 0

            for m in range(len(front[0].objectives)):
                front.sort(key=lambda individual: individual.objectives[m])
                front[0].crowding_distance = 10 ** 9
                front[solutions_num - 1].crowding_distance = 10 ** 9
                m_values = [individual.objectives[m] for individual in front]
                scale = max(m_values) - min(m_values)
                if scale == 0: scale = 1
                for i in range(1, solutions_num - 1):
                    front[i].crowding_distance += (front[i + 1].objectives[m] - front[i - 1].objectives[m]) / scale

    def crowding_operator(self, individual, other_individual):
        if (individual.rank < other_individual.rank) or \
                ((individual.rank == other_individual.rank) and (
                        individual.crowding_distance > other_individual.crowding_distance)):
            return 1
        else:
            return -1

    def create_children(self, population):
        children = []
        while len(children) < len(population):
            i = 0
            while True:
                constent.st.value += i
                i = 1
                parent1 = self.__tournament(population) # 1: rank 2: if equal -> crowd
                parent2 = parent1
                while parent1 == parent2:
                    parent2 = self.__tournament(population)
                child1, child2 = self.__crossover(parent1, parent2)
                self.__mutate(child1)
                self.__mutate(child2)
                if calcu_feature(child1) and calcu_feature(child2):
                    break
                else:
                    # print(parent1.features[5:11],parent1.features[5]*parent1.features[9]+parent1.features[6]*parent1.features[10]+parent1.features[7]+parent1.features[8])
                    # print(parent2.features[5:11],parent2.features[5]*parent2.features[9]+parent2.features[6]*parent2.features[10]+parent2.features[7]+parent2.features[8])
                    # print(child1.features[5:11],child1.features[5]*child1.features[9]+child1.features[6]*child1.features[10]+child1.features[7]+child1.features[8])
                    # print(child2.features[5:11],child2.features[5]*child2.features[9]+child2.features[6]*child2.features[10]+child2.features[7]+child2.features[8])
                    pass
            self.problem.calculate_objectives(child1)
            self.problem.calculate_objectives(child2)
            children.append(child1)
            children.append(child2)

        return children

    def __crossover(self, individual1, individual2):
        child1 = self.problem.generate_empty_individual()
        child2 = self.problem.generate_empty_individual()
        num_of_features = len(child1.features)
        genes_indexes = range(num_of_features)
        for i in genes_indexes:
            beta = self.__get_beta() # nomal 期望：1.0 差：0.5
            x1 = (individual1.features[i] + individual2.features[i]) / 2
            x2 = abs((individual1.features[i] - individual2.features[i]) / 2)
            child1.features[i] = x1 + beta * x2
            child2.features[i] = x1 - beta * x2
        
        return child1, child2

    def __get_beta(self):
        u = random.random()
        if u <= 0.5:
            return (2 * u) ** (1 / (self.crossover_param + 1))
        return (2 * (1 - u)) ** (-1 / (self.crossover_param + 1))

    def __mutate(self, child):
        num_of_features = len(child.features)

        for gene in range(num_of_features):
            if child.features[gene]!=0:       # ==0 则不变异
                u, delta = self.__get_delta() # delta 期望：0,差：0.2
                if u < 0.5:
                    child.features[gene] += delta * (child.features[gene] - self.problem.variables_range[0])
                else:
                    child.features[gene] += delta * (self.problem.variables_range[1] - child.features[gene])
                    
                if child.features[gene] < self.problem.variables_range[0]:
                    child.features[gene] = self.problem.variables_range[0]
                if child.features[gene] > self.problem.variables_range[1]:
                    child.features[gene] = self.problem.variables_range[1]

    def __get_delta(self):
        u = random.random()
        if u < 0.5:
            return u, (2 * u) ** (1 / (self.mutation_param + 1)) - 1
        return u, 1 - (2 * (1 - u)) ** (1 / (self.mutation_param + 1))

    def __tournament(self, population):
        # self.num_of_tour_particips = 2
        participants = random.sample(population.population, self.num_of_tour_particips)
        best = None
        for participant in participants:
            if best is None or (
                    self.crowding_operator(participant, best) == 1 and self.__choose_with_prob(self.tournament_prob)):
                best = participant

        return best

    def __choose_with_prob(self, prob):
        if random.random() <= prob:
            return True
        return False
