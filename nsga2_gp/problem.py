from nsga2.individual import Individual
import random
from example import constent 


class Problem:

    def __init__(self, objectives):
        self.num_of_objectives = len(objectives)
        self.objectives = objectives

    def generate_individual(self):
        individual = Individual()
        device_limit = [random.randint(0,mx) for mx in constent.DEVICE_LIMIT]
        elic_feature = [random.randint(0,mx) for mx in device_limit]

        individual.features.append()
        for row in table_p:
            pass

        return individual

    def calculate_objectives(self, individual):
        individual.objectives = [f(individual) for f in self.objectives]
