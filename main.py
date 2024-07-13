from random import choices, choice, randint, random
from time import time

class Graph:
    ''' Classe que representa um grafo '''
    
    def __init__(self, file: str):
        self.v = 0 # Quantidade de vértices
        self.e = 0 # Quantidade de arestas
        
        self.max_colors = 1 # Quantidade máxima de cores
        
        self.data: dict[int, list[int]] = {} # Dicionário de vértices e vizinhos
        
        self.file = file # Arquivo de instância
        
        self.load() # Carregar instância
        
    def load(self):
        ''' Carrega os dados da instância '''
        
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
                    
            max_vertex = 1 # Define o vértice com mais vizinhos
                    
            for vertex in self.data:
                if len(self.data[vertex]) > len(self.data[max_vertex]):
                    max_vertex = vertex
            
            self.max_colors = len(self.data[max_vertex])

class State:
    ''' Classe que representa um estado do problema '''
    
    def __init__(self, graph: Graph, colors: int, values: list[int]):
        self.graph = graph # Grafo
        
        self.colors = colors # Quantidade de cores
        self.values = values # Valores dos vértices
       
        self.fitness = self._fitness() # Fitness (Enquanto maior, pior)
    
    @staticmethod
    def random(graph: Graph):
        ''' Gera um estado aleatório '''
        
        colors = graph.max_colors
        values = [randint(1, colors) for _ in range(graph.v)]
        
        return State(graph, colors, values)
       
    def _fitness(self):
        ''' Calcula o fitness do estado '''
        
        fitness = 0
        
        for vertex in self.graph.data:
            for neighbor in self.graph.data[vertex]:
                if self.values[vertex - 1] == self.values[neighbor - 1]:
                    # Se o vertice tiver a mesma cor que o vizinho o fitness é incrementado
                    fitness += 1
                
        return fitness
      
class GeneticAlgorithm:
    ''' Classe que representa o algoritmo genético '''
    
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
        self.graph = graph # Grafo
        self.population_size = population_size # Tamanho da população
        self.sample_size = sample_size # Tamanho da amostra para seleção
        self.generations = generations # Quantidade de gerações
        self.improvements = improvements # Quantidade de melhorias
        self.pc = pc # Probabilidade de crossover
        self.pm = pm # Probabilidade de mutação
        
    def selection(self, population: list[State]):
        ''' Seleciona um indivíduo da população a partir de um torneio '''
        
        sample = choices(population, k=self.sample_size) # Amostra da população
        return min(sample, key=lambda item: item.colors) # Indivíduo com menos cores na amostra
    
    def reproduce(self, x: State, y: State):
        ''' Realiza o crossover entre dois indivíduos '''
        
        i = randint(0, len(x.values)) # Ponto de corte
        
        colors = max(x.colors, y.colors) # Máximo de cores
        
        x_ = State(self.graph, colors, x.values[:i] + y.values[i:])
        y_ = State(self.graph, colors, y.values[:i] + x.values[i:])
        
        return x_, y_ # 2 novos indivíduos
    
    def rep_op(self, x: State):
        ''' Operador de reparo '''
        
        colors = x.colors
        values = x.values.copy() # Copia dos valores para não alterar o original
        
        for i in self.graph.data:
            for j in self.graph.data[i]:
                # Enquanto um vertice tiver a mesma cor que o vizinho, troca a cor do vizinho
                while values[i - 1] == values[j - 1]:
                    values[j - 1] = randint(1, colors)
        
        # Retorna um novo indivíduo
        y = State(self.graph, colors, values)
        
        return min(x, y, key=lambda item: item.fitness) # Caso haja melhoria, retorna o melhor
    
    def repair(self, x: State):
        ''' Realiza a tentativa de reparo N vezes '''
        
        for _ in range(self.improvements):
            if x.fitness == 0:
                break
            
            x = self.rep_op(x)
            
        return x
    
    def mp_sp_mutation(self, x: State):
        ''' 
            Operador de mutação especial decrementando a quantidade de cores
        
            Exemplo de mutação especial:
            estado = [1, 2, 3, 4, 5]
            cor_a_ser_removida = 3
            
            resultado = [1, 2, aleatorio_entre(1, 4), 3, 4] 
        '''
        
        colors = x.colors
        values = x.values.copy() # Copia dos valores para não alterar o original
        
        remove = randint(1, colors) # Cor a ser removida
        
        for i in range(len(values)):
            if values[i] == remove: # Se o vertice tiver a cor a ser removida troca por uma cor aleatória
                values[i] = randint(1, colors - 1)
                
            elif values[i] > remove: # Se o vertice tiver uma cor maior que a removida, decrementa
                values[i] -= 1
        
        return State(self.graph, colors - 1, values)
    
    def run(self):
        ''' Executa o algoritmo genético '''
        
        timer = time() # Inicia o cronômetro
        
        population: list[State] = []
        
        print('GENERATING INITIAL POPULATION...')

        while len(population) < self.population_size: # Gera a população até atingir o tamanho desejado
            print(f'POPULATION SIZE: {len(population)} / {self.population_size}')
            
            random_state = self.repair(State.random(self.graph))
            
            if random_state.fitness == 0: # Se o estado for válido, adiciona à população
                population.append(random_state)
    
        best = min(population, key=lambda item: item.colors) # Melhor indivíduo
        
        for i in range(self.generations): # Para cada geração
            print(f'I: {i} | FITNESS: {best.fitness} | COLORS: {best.colors}')
            
            new_population: list[State] = []
            
            # print('GENERATING NEW POPULATION...')
                 
            while len(new_population) < self.population_size: # Gera a nova população até atingir o tamanho desejado
                # print(f'POPULATION SIZE: {len(new_population)} / {self.population_size}')
                
                x = self.selection(population) # Seleciona um indivíduo
                y = self.selection(population) # Seleciona outro indivíduo
                
                if random() < self.pc: # Se a probabilidade de crossover for atingida
                    x, y = self.reproduce(x, y) # Realiza o crossover
                    
                    x, y = self.repair(x), self.repair(y) # Realiza o reparo dos indivíduos
                
                for ind in [x, y]: # Para cada indivíduo gerado
                    if ind.fitness != 0: # Se o indivíduo for inválido pulamos para o próximo
                        continue
                    
                    if random() < self.pm: # Se a probabilidade de mutação for atingida
                        ind = self.repair(self.mp_sp_mutation(ind)) # Realiza a mutação especial
                        
                        if ind.fitness == 0: # Se o indivíduo for válido, adiciona à nova população
                            new_population.append(ind)
                    
                    else: # Se não realizar a mutação, adiciona à nova população
                        new_population.append(ind)
            
            population = new_population # Atualiza a população
            best = min(population, key=lambda item: item.colors) # Atualiza o melhor indivíduo
        
        timer = time() - timer # Finaliza o cronômetro
        
        print('ELAPSED TIME:', timer)
                     
        print(f'FITNESS: {best.fitness} | BEST: {best.values}')
          
class GoldenBall:
    def __init__(
        self,
        graph: Graph, 
        tn=10,
        pt=10,
        improvements=5,
        
        sample_size=10,
        generations=10000,
        pc=0.9,
        pm=0.2
    ):
        self.graph = graph # Grafo
        self.tn = tn # Quantidade de times
        self.pt = pt # Quantidade de jogadores por time
        self.improvements = improvements # Quantidade de melhorias
        ...
       
    def rep_op(self, x: State):
        ''' Operador de reparo '''
        
        values = x.values.copy() # Copia dos valores para não alterar o original
        
        for i in self.graph.data:
            for j in self.graph.data[i]:
                # Enquanto um vertice tiver a mesma cor que o vizinho, troca a cor do vizinho
                while values[i - 1] == values[j - 1]:
                    values[j - 1] = randint(1, x.colors)
        
        # Retorna um novo indivíduo
        y = State(self.graph, x.colors, values)
        
        return min(x, y, key=lambda item: item.fitness) # Caso haja melhoria, retorna o melhor
    
    def repair(self, x: State):
        ''' Realiza a tentativa de reparo N vezes '''
        
        for _ in range(self.improvements):
            if x.fitness == 0:
                break
            
            x = self.rep_op(x)
            
        return x
    
    def mp_sp_mutation(self, x: State):
        ''' 
            Operador de mutação especial decrementando a quantidade de cores
        
            Exemplo de mutação especial:
            estado = [1, 2, 3, 4, 5]
            cor_a_ser_removida = 3
            
            resultado = [1, 2, aleatorio_entre(1, 4), 3, 4] 
        '''
        
        colors = x.colors
        values = x.values.copy() # Copia dos valores para não alterar o original
        
        remove = randint(1, colors) # Cor a ser removida
        
        for i in range(len(values)):
            if values[i] == remove: # Se o vertice tiver a cor a ser removida troca por uma cor aleatória
                values[i] = randint(1, colors - 1)
                
            elif values[i] > remove: # Se o vertice tiver uma cor maior que a removida, decrementa
                values[i] -= 1
        
        return State(self.graph, colors - 1, values)
          
    def run(self):
        population: list[list[State]] = []
        
        for _ in range(self.tn):
            team = []

            while len(team) < self.pt:
                random_state = self.repair(State.random(self.graph))
                
                if random_state.fitness == 0:
                    team.append(random_state)
                    
            population.append(team)
            
        while True: # Enquanto não atingir a condição de parada
            team_fitness = [0] * self.tn
            
            for j in [1, 2]:
                ...                
            
                     
if __name__ == '__main__':
    graph = Graph('instances/miles1000.col')
    
    # ga = GeneticAlgorithm(graph)
    
    # ga.run()
    
    gb = GoldenBall(graph)
    
    gb.run()