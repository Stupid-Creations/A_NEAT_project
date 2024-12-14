import random
import math

sigmoid = lambda x: 1 / (1 + math.exp(-x))

class Node:
    def __init__(self, index, connections=[], type="H",parent=None):
        self.type = type
        self.index = index
        self.connections = connections
        self.pred = None
        self.parent = parent

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
        adjusted_input = input_size+1
        self.info = [adjusted_input, output_size]
        self.Nodes = [[Node(i) for i in range(self.info[0])], [Node(self.info[0] + j) for j in range(output_size)], []]
        self.Connections = []
        self.fitness = None

        for inp_node in self.Nodes[0]:
            for out_node in self.Nodes[1]:
                connection = Connection(out_node, innov, inp_node)
                out_node.connections.append(connection)
                self.Connections.append(connection)

    def activate(self, input_vals):
        if len(input_vals) != self.info[0]-1:
            raise ValueError("Incorrect Input Size")
        
        for i, node in enumerate(self.Nodes[0]):
            try:
                node.activate(input_val=input_vals[i])
            except:
                node.activate(input_val=1)

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

    def incheck(self,list):
        return self in list
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

def NodeIndexSquared(List,Index):
    for i in range(len(List)):
        if List[i].index == Index:
            return i
    raise ValueError("Not in List")

def reproduce(pa,pb,innov):
    fitter = pa if pa.fitness > pb.fitness else pb
    other = pa if fitter == pb else pb

    pfc = sorted(fitter.Connections,key=lambda x: x.innov)
    poc = sorted(other.Connections,key=lambda x: x.innov)

    disjoint = [i for i in pfc if i not in poc]
    common = [random.choice([x,y]) for x,y in zip(pfc,poc) if x.innov==y.innov]

    final = disjoint+common
    allnodes = list(set([i.output.index for i in final]+[j.input.index for j in final]))

    Nodes = [Node(i,connections=[]) for i in sorted(allnodes)]
    Connections = []
    for i in range(len(final)):
        for j in range(len(Nodes)):
            if Nodes[j].index == final[i].output.index:
                connection = Connection(Nodes[j],innov,Nodes[NodeIndexSquared(Nodes,final[i].input.index)],disabled = final[i].disabled,weight=final[i].weight)
                Nodes[j].connections.append(connection)
                Connections.append(connection)
    
    DivNodes = [[],[],[]]
    for i in range(pa.info[0]):
        DivNodes[0].append(Nodes[i])
    for i in range(pa.info[0],pa.info[1]+pa.info[0]):
        DivNodes[1].append(Nodes[i])
    for i in range(pa.info[1]+pa.info[0],len(Nodes)):
        DivNodes[2].append(Nodes[i])
    
    child = Network(pa.info[0]-1,pa.info[1],innov)
    child.Connections = Connections
    child.Nodes = DivNodes

    child.mutate(innov)

    return child            
        
def print_connections(network):
    for connection in network.Connections:
        print('\n')
        print(f"Input Node: {connection.input.index}")
        print(f"Output Node: {connection.output.index}")
        print(f"Weight: {connection.weight}")
        print(f"Innov: {connection.innov}")        
        print(f"Disabled: {connection.disabled}")


inn = []

a = Network(3,3,inn)
a.add_node(inn)

b = Network(3,3,inn)

a.fitness,b.fitness = 1,-1
c = reproduce(a,b,inn)
print_connections(c)
c.activate([1,3,4])
print(c.pred)

#TODO: ADD FUNCTION TO CHECK FOR DENSE NETS (or just use try catch lol)
#TODO 2 Electric Bogaloo: ADD RECURSIVE NETWORK FUNCTIONALITY TO ACTIVATION AND MUTATION
#TODO 3: Add Bias Node
