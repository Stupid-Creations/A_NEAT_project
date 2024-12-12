import random
import math

sigmoid = lambda x: 1 / (1 + math.exp(-x))

def ConnIn(object,list):
    for i in list:
        if object == i:
            return True
    return False

class Node:
    def __init__(self, index, connections=None, type="H"):
        if connections is None:
            connections = []
        self.type = type
        self.index = index
        self.connections = connections
        self.pred = None

    def activate(self, input_val=None):
        if input_val is not None:
            self.pred = input_val
        else:
            self.pred = sigmoid(sum([i.input.pred * i.weight for i in self.connections if not i.disabled]))

class Connection:
    def __init__(self, output, innov, inp, disabled=False, weight=None):
        self.weight = weight if weight is not None else random.random() * random.choice([-1, 1])
        self.input = inp
        self.output = output
        self.innov = self.get_innov(innov)
        self.disabled = disabled
        self.pred = None
        #print(f"Weight: {self.weight}, Input Index: {self.input.index}, Output Index: {self.output.index}")

    def get_innov(self, innov):
        for conn in innov:
            if conn == self:
                return conn.innov
        innov.append(self)
        return len(innov)

    def __eq__(self, other):
        return self.input.index == other.input.index and self.output.index == other.output.index



class Network:
    def __init__(self, input_size, output_size, innov):
        self.pred = []
        self.info = [input_size, output_size]
        self.Nodes = [[Node(i) for i in range(input_size)], [Node(input_size + j) for j in range(output_size)], []]
        self.Connections = []
        self.fitness = None

        for inp_node in self.Nodes[0]:
            for out_node in self.Nodes[1]:
                connection = Connection(out_node, innov, inp_node)
                out_node.connections.append(connection)
                self.Connections.append(connection)

        self.FNodes = [node for sublist in self.Nodes for node in sublist]

    def activate(self, input_vals):
        if len(input_vals) != self.info[0]:
            raise ValueError("Incorrect Input Size")
        
        for i, node in enumerate(self.Nodes[0]):
            node.activate(input_val=input_vals[i])

        for node in self.Nodes[2]:
            node.activate()

        for node in self.Nodes[1]:
            node.activate()

        self.pred = [node.pred for node in self.Nodes[1]]

    def add_connection(self, input_node, output_node, innov,weight=None):
        connection = Connection(output_node, innov, input_node) if weight == None else Connection(output_node, innov, input_node,weight=weight)
        output_node.connections.append(connection)
        self.Connections.append(connection)

    def add_node(self, innov):
        doomed = random.choice(self.Connections)
        doomed.disabled = True

        new_node_index = self.info[0] + self.info[1] + len(self.Nodes[2])
        new_node = Node(new_node_index)
        self.Nodes[2].append(new_node)

        self.add_connection(doomed.input, new_node, innov,weight = 1)
        self.add_connection(new_node, doomed.output, innov,weight = doomed.weight)

    def mutate_weight(self):
        for i in self.Nodes[1]:
            for j in i.connections:
                if random.random()>0.1:
                    j.weight = random.random()*random.choice([-1,1])
                    self.Connections[self.Connections.index(j)].weight = random.random()*random.choice([-1,1])
                    return

        for i in self.Nodes[2]:
            for j in i.connections:
                if random.random()>0.1:
                    j.weight = random.random()*random.choice([-1,1])
                    self.Connections[self.Connections.index(j)].weight = random.random()*random.choice([-1,1])
                    return

    def mutate(self,innov,mut=None):
        mutator = random.randint(0,2) if mut == None else mut
        match mutator:
            case 0: 
                self.mutate_weight()
            case 1:
                self.add_node(innov)
            case 2:
                if len(self.Nodes[2]) > 0:
                    indexer = random.randint(0,1)
                    chosen = random.choice(self.Nodes[2])
                    if indexer == 0:
                        noncon = random.choice([a for a in self.Nodes[0] if a not in [i.input for i in chosen.connections]])
                        self.add_connection(noncon,chosen,innov)     
                    else:
                        noncon = random.choice([a for a in self.Nodes[1] if chosen not in [i.output for i in a.connections]])
                        self.add_connection(noncon,chosen,innov)     
                else:
                    print("dense net found, redoing")
                    self.mutate(innov,mut=random.choice([0,1]))
                    
        
def print_connections(network):
    for connection in network.Connections:
        print('\n')
        print(f"Input Node: {connection.input.index}")
        print(f"Output Node: {connection.output.index}")
        print(f"Weight: {connection.weight}")
        print(f"Innov: {connection.innov}")        
        print(f"Disabled: {connection.disabled}")


inn = []
a = Network(3,2, inn)
a.activate([1,2,3])
print("Output Predictions:", a.pred)
a.add_node(inn)
a.activate([1,2,3])
print("Output Predictions:", a.pred)

print_connections(a)
