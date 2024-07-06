from random import choices, randint, random

class Graph:
    def __init__(self, file: str):
        self.v = 0
        self.e = 0
        
        self.data = {}
        
        self.file = file
        
        self.load()
        
    def load(self):
        with open(self.file) as f:
            for line in f:
                letter, *row = line.split()
                
                if letter == 'p':
                    self.v = int(row[1])
                    self.e = int(row[2])
                elif letter == 'e':
                    vertex = int(row[0])
                    neighbor = int(row[1])
                    
                    if vertex not in self.data:
                        self.data[vertex] = []
              
                    self.data[vertex].append(neighbor)

# GAMBIARRA
k = 8

class State:
    def __init__(self, graph: Graph, values: list[int]):
        self.graph = graph
        self.values = values
       
        self.fitness = self.calculate()
       
    @staticmethod
    def random(graph: Graph):
        values = [randint(0, k - 1) for _ in range(graph.v)]
        return State(graph, values)
       
    def calculate(self):
        fitness = 0
        
        for vertex in self.graph.data:
            for neighbor in self.graph.data[vertex]:
                if self.values[vertex - 1] != self.values[neighbor - 1]:
                    continue
                
                fitness += 1
                
        return fitness
      
    def reproduce(self, other: 'State'):
        pivot = randint(0, len(self.values) - 1)
        return State(self.graph, self.values[:pivot] + other.values[pivot:])
      
    def mutate(self):
        ''' ERRADO '''
        
        pivot = randint(0, len(self.values) - 1)
        
        values = self.values.copy()

        values[pivot] = randint(0, k - 1)
        
        return State(self.graph, values)
      
class GeneticAlgorithm:
    def __init__(
        self, 
        graph: Graph, 
        population_size=200, 
        sample_size=10, 
        mutation_rate=0.4, 
        generations=10000
    ):
        self.graph = graph
        self.population_size = population_size
        self.sample_size = sample_size
        self.mutation_rate = mutation_rate
        self.generations = generations
        
    def selection(self, population: list[State]):
        sample = choices(population, k=self.sample_size)
        return min(sample, key=lambda item: item.fitness)
    
    def reproduce(self, x: State, y: State):
        return x.reproduce(y), y.reproduce(x)
    
    def mutate(self, x: State):
        return x.mutate()
    
    def run(self):
        population = [State.random(self.graph) for _ in range(self.population_size)]
        best = min(population, key=lambda item: item.fitness)
        
        for i in range(self.generations):
            print(f'* STEPS: {i + 1} | COST: {best.fitness}')
            
            new_population: list[State] = []
            
            for _ in range(self.population_size // 2):
                x = self.selection(population)
                y = self.selection(population)
                
                z1, z2 = self.reproduce(x, y)
                
                if random() < self.mutation_rate:
                    z1 = self.mutate(z1)
                    
                if random() < self.mutation_rate:
                    z2 = self.mutate(z2)
                    
                new_population.append(z1)
                new_population.append(z2)
            
            population = new_population
            best = min(population, key=lambda item: item.fitness)
                     
        print(f'FITNESS: {best.fitness} | BEST: {best.values}')
                     
if __name__ == '__main__':
    graph = Graph('instances/queen7_7.col')
    
    ga = GeneticAlgorithm(graph)
    
    ga.run()    