from random import choices, choice, randint, random
from time import time

class Graph:
    def __init__(self, file: str):
        self.v = 0
        self.e = 0
        
        self.max_colors = 1
        self.max_vertex = 1
        
        self.initial_colors: list[int] = []
        
        self.data: dict[int, list[int]] = {}
        
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
                if len(self.data[vertex]) > len(self.data[self.max_vertex]):
                    self.max_vertex = vertex
            
            self.max_colors = len(self.data[self.max_vertex])

            self.initial_colors = self._initial_colors()

    def _initial_colors(self):
        current = 1
        
        values = [0] * self.v
    
        values[self.max_vertex - 1] = current
        
        neighbors = self.data[self.max_vertex]
    
        print('MAX VERTEX:', self.max_vertex)
        print('VALUES:', values)
        
        for vertex in neighbors:
            if values[vertex - 1] != 0:
                continue
            
            current += 1
            
            values[vertex - 1] = current
            
            for neighbor in neighbors:
                if vertex == neighbor:
                    continue
                
                if values[neighbor - 1] != 0:
                    continue
                
                if vertex not in self.data[neighbor] and neighbor not in self.data[vertex]:
                    values[neighbor - 1] = current

        print('VALUES:', values)

        return values

class State:
    def __init__(self, graph: Graph, colors: int, values: list[int]):
        self.graph = graph
        
        self.colors = colors
        self.values = values
       
        self.fitness = self._fitness()
    
    @staticmethod
    def random_heuristic(graph: Graph):
        colors = graph.max_colors
        values = graph.initial_colors[:]
        
        for i in range(len(values)):
            if values[i] == 0:
                values[i] = randint(1, colors)
    
        return State(graph, colors, values)
    
    @staticmethod
    def random(graph: Graph):
        colors = graph.max_colors
        values = [randint(1, colors) for _ in range(graph.v)]
        
        return State(graph, colors, values)
       
    def _fitness(self):
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
        improvements=5,
        pc=0.9,
        pm=0.2
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
        
        for i in range(1, len(values) + 1):
            if i not in self.graph.data:
                continue
            
            for j in self.graph.data[i]:
                while values[i - 1] == values[j - 1]:
                    if self.graph.initial_colors[j - 1] == 0:
                        values[j - 1] = randint(1, colors)
                    else:
                        values[i - 1] = randint(1, colors)
        
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
        
        remove = randint(max(self.graph.initial_colors), colors)
        
        for i in range(len(values)):
            if values[i] == remove:
                values[i] = randint(1, colors - 1)
                
            elif values[i] > remove:
                values[i] -= 1
        
        return State(self.graph, colors - 1, values)
    
    def run(self):
        timer = time()
        
        population: list[State] = []
        
        # print('GENERATING INITIAL POPULATION...')
        
        while len(population) < self.population_size:
            # print(f'POPULATION SIZE: {len(population)} / {self.population_size}')
            
            random_state = State.random_heuristic(self.graph)
            repaired_state = self.repair(random_state)
            
            if repaired_state.fitness == 0:
                print(f'V: {repaired_state.values[:20]}')
                
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
        
        timer = time() - timer
        
        print('ELAPSED TIME:', timer)
                     
        print(f'FITNESS: {best.fitness} | BEST: {best.values}')
                     
if __name__ == '__main__':
    graph = Graph('instances/queen6_6.col')
    
    ga = GeneticAlgorithm(graph)
    
    ga.run()