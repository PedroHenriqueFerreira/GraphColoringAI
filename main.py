from random import choices, choice, randint, random

class Graph:
    def __init__(self, file: str):
        self.v = 0
        self.e = 0
        
        self.max_colors = 0
        
        self.data: dict[list[int]] = {}
        
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
                    
            for vertex in self.data:
                self.max_colors = max(self.max_colors, len(self.data[vertex]))

class State:
    def __init__(self, graph: Graph, colors: int, values: list[int]):
        self.graph = graph
        
        self.colors = colors
        self.values = values
       
        self.fitness = self.calculate()
       
    @staticmethod
    def random(graph: Graph):
        colors = graph.max_colors
        values = [randint(1, colors) for _ in range(graph.v)]
        
        return State(graph, colors, values)
       
    def calculate(self):
        fitness = 0
        
        for vertex in self.graph.data:
            for neighbor in self.graph.data[vertex]:
                if self.values[vertex - 1] != self.values[neighbor - 1]:
                    continue
                
                fitness += 1
                
        return fitness
      
class GeneticAlgorithm:
    def __init__(
        self, 
        graph: Graph, 
        population_size=100, 
        sample_size=10,
        generations=10000,
        improvements=25,
        pc=0.9,
        pm=0.1
    ):
        self.graph = graph
        self.population_size = population_size
        self.sample_size = sample_size
        self.generations = generations
        self.improvements = improvements
        self.pc = pc
        self.pm = pm
        
    def selection(self, population: list[State]):
        sample = choices(population, k=self.sample_size)
        return min(sample, key=lambda item: item.colors)
    
    def reproduce(self, x: State, y: State):
        i = randint(0, len(x.values))
        
        x_ = State(self.graph, max(x.colors, y.colors), x.values[:i] + y.values[i:])
        y_ = State(self.graph, max(x.colors, y.colors), y.values[:i] + x.values[i:])
        
        return x_, y_
    
    def rep_op(self, x: State):
        if x.fitness == 0:
            return x
        
        colors = x.colors
        values = x.values[:]
        
        for i in range(len(values)):
            for j in range(len(values)):
                if i != j:
                    while values[i] == values[j]:
                        values[j] = randint(1, colors)
        
        y = State(self.graph, colors, values)
        
        return min(x, y, key=lambda item: item.fitness)
    
    def repair(self, x: State):
        for _ in range(self.improvements):
            if x.fitness == 0:
                break
            
            x = self.rep_op(x)
            
        return x
    
    def mp_sp_mutation(self, x: State):
        colors = x.colors
        values = x.values[:]
        
        remove = randint(1, colors)
        
        for i in range(len(values)):
            if values[i] == remove:
                values[i] = randint(1, colors - 1)
                
            elif values[i] > remove:
                values[i] -= 1
        
        return State(self.graph, colors - 1, values)
    
    def run(self):
        population: list[State] = []
        
        # print('GENERATING INITIAL POPULATION...')
        
        while len(population) < self.population_size:
            # print(f'POPULATION SIZE: {len(population)} / {self.population_size}')
            
            random_state = State.random(self.graph)
            repaired_state = self.repair(random_state)
            
            if repaired_state.fitness == 0:
                population.append(repaired_state)
    
        best = min(population, key=lambda item: item.colors)
        
        for _ in range(self.generations):
            print(f'FITNESS: {best.fitness} | COLORS: {best.colors}')
            
            new_population: list[State] = []
            
            # print('GENERATING NEW POPULATION...')
                 
            while len(new_population) < self.population_size:
                # print(f'POPULATION SIZE: {len(new_population)} / {self.population_size}')
                
                x = self.selection(population)
                y = self.selection(population)
                
                if random() < self.pc:
                    x, y = self.reproduce(x, y)
                    
                    x, y = self.repair(x), self.repair(y)
                
                if x.fitness == 0:
                    if random() < self.pm:
                        x = self.repair(self.mp_sp_mutation(x))
                        
                        if x.fitness == 0:
                            new_population.append(x)
                            
                    else:
                        new_population.append(x)
                
                if y.fitness == 0:
                    if random() < self.pm:
                        y = self.repair(self.mp_sp_mutation(y))
                        
                        if y.fitness == 0:
                            new_population.append(y)
                            
                    else:
                        new_population.append(y)
            
            population = new_population
            best = min(population, key=lambda item: item.colors)
                     
        print(f'FITNESS: {best.fitness} | BEST: {best.values}')
                     
if __name__ == '__main__':
    graph = Graph('instances/david.col')
    
    ga = GeneticAlgorithm(graph)
    
    ga.run()