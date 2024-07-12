from nsga2.individual import Individual
import random


class Problem:

    def __init__(self, objectives, num_of_variables, variables_range, expand=True, same_range=False):
        self.num_of_objectives = len(objectives)
        self.num_of_variables = num_of_variables
        self.objectives = objectives
        self.expand = expand
        self.variables_range = [0,1]

    def generate_individual(self):
        individual = Individual()
        if round(random.random())<0:
            individual.features = [0 for x in range(1000)]
        else:
            individual.features = [round(random.random(),2) for x in range(3000)]
        return individual

    def calculate_objectives(self, individual):
        individual.objectives = [f(individual.features) for f in self.objectives]
