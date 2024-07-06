from random import choices, random

class GeneticAlgorithm:
    ''' Algoritmo genético '''
    
    def __init__(
        self, 
        tsp: TSP, 
        verbose=False, 
        population_size=100, 
        sample_size=10, 
        mutation_rate=0.2, 
        generations=1000
    ):
        self.population_size = population_size # Tamanho da população
        self.sample_size = sample_size # Tamanho das amostras
        self.mutation_rate = mutation_rate # Taxa de mutação
        self.generations = generations # Número de gerações
    
    def selection(self, population: list[list[int]]):
        ''' Seleciona um indivíduo da população '''

        sample = choices(population, k=self.sample_size)
        
        return min(sample, key=lambda item: item.cost)

    def reproduce(self, x: TSPState, y: TSPState):
        ''' Realiza o cruzamento entre dois indivíduos '''
 
        return x.random_merge(y), y.random_merge(x)

    def mutate(self, x: TSPState):
        ''' Realiza a mutação de um indivíduo '''
        
        return x.random_successor()

    def run(self):
        ''' Executa o algoritmo genético '''
        
        population = [self.tsp.random_state() for _ in range(self.population_size)]
        best = min(population, key=lambda item: item.cost)
        
        for _ in range(self.generations):
            if self.verbose:
                print(f'* STEPS: {len(self.steps)} | COST: {best.cost}')
            
            new_population: list[TSPState] = []
            
            for _ in range(self.population_size // 2):
                x = self.selection(population)
                y = self.selection(population)
                
                child1, child2 = self.reproduce(x, y)
                
                if random() < self.mutation_rate:
                    child1 = self.mutate(child1)
                    
                if random() < self.mutation_rate:
                    child2 = self.mutate(child2)
                    
                new_population.append(child1)
                new_population.append(child2)
            
            population = new_population
            
            best = min(population, key=lambda item: item.cost)
