from nsga2.individual import Individual
import random


class Problem:

    def __init__(self, objectives, num_of_variables, variables_range, expand=True, same_range=False):
        self.num_of_objectives = len(objectives)
        self.num_of_variables = num_of_variables
        self.objectives = objectives
        self.expand = expand
        self.variables_range = []
        if same_range:
            for _ in range(num_of_variables):
                self.variables_range.append(variables_range[0])
        else:
            self.variables_range = variables_range

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
        if self.expand:
            individual.objectives = [f(*individual.features) for f in self.objectives]
        else:
            individual.objectives = [f(individual.features) for f in self.objectives]
