import sys,os
sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from nsga2_gp_example.individual import Individual
from nsga2_gp_example.utils import adjust
import random
from example.data import table_p

N_EB = 0.97
T_SH = 0.06
A_CO2 = 0.853

N_SH = 0.87

QEB_MAX = 400
SELL_PRICE = 0.4

class Problem:

    def __init__(self, objectives):
        self.num_of_objectives = len(objectives)
        self.objectives = objectives
        self.variables_range = []

    def generate_individual(self):
        individual = Individual()
        heat_rest_p = 960
        for row in table_p:
            individual.range[0] = max(row[2]*N_EB - heat_rest_p*N_SH,0)
            peb = random.uniform(individual.range[0],QEB_MAX)
            individual.features.append(peb)
            heat_rest_p = (1-T_SH)*heat_rest_p+(peb-row[2]*N_EB)*N_SH

        return individual
    
    def calculate_objectives(self, individual):
        individual.objectives = [f(individual) for f in self.objectives]

# if __name__=='__main__':
#     problem = Problem(objectives=[f1, f2], num_of_variables=24, variables_range=[(0,3)])
#     individual = problem.generate_individual()
#     print(individual.features)