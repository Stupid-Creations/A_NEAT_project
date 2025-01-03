import random
import math
import pygame
import sys
import matplotlib.pyplot as plt

pygame.display.init()
wn = pygame.display.set_mode((800,800))

sigmoid = lambda x: 1 / (1 + math.exp(-x))

class Node:
    def __init__(self, index, connections=[], type="H",parent=None):
        self.type = type
        self.index = index
        self.connections = connections
        self.pred = None
        self.parent = parent

    def activate(self, input_val=None):
        self.pred = 0
        if input_val is not None:
            self.pred = input_val
        else:
            try:
                for i in self.connections:
                    if i is not i.disabled:
                        try:
                            self.pred+=i.input.pred*i.weight
                        except:
                            i.input.activate()
                            self.pred+=i.input.pred*i.weight
                self.pred = sigmoid(self.pred)
            except Exception as e:
                print(self.index)
                print([i.input.index for i in self.connections])
                print([i.input.pred for i in self.connections])
                print("ERROR ERROR ERROR ERROR ERROR")
                raise Exception(f"{self.index} {[i.input.index for i in self.connections]} {[i.input.pred for i in self.connections]}"+str(e))

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
        self.Nodes = [[Node(i,type="I") for i in range(self.info[0])], [Node(self.info[0] + j,type="O") for j in range(output_size)], []]
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
        new_node = Node(new_node_index,connections=[])
        self.Nodes[2].append(new_node)

        self.add_connection(doomed.input, new_node, innov,weight = 1)
        self.add_connection(new_node, doomed.output, innov,weight = doomed.weight)

        # if doomed.output.type == "H":
        #     self.Nodes[2].pop(self.Nodes[2].index(new_node))
        #     self.Nodes[2].insert(self.Nodes[2].index(doomed.output),new_node)

    def mutate_weight(self):
        #CHANGE TO ADD 90% PERTURBANCE ChaNcE
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
                try:
                    indexer = random.randint(0,2) if len(self.Nodes[2]) > 1 else random.randint(0,1)
                    chosen = random.choice(self.Nodes[2])
                    if indexer == 0:
                        noncon = random.choice([a for a in self.Nodes[0] if a not in [i.output for i in chosen.connections]])
                        self.add_connection(noncon,chosen,innov)     
                    else:
                        if indexer == 1:
                            if random.random > 0.5:
                                noncon = random.choice([a for a in self.Nodes[1] if chosen not in [i.input for i in a.connections]])
                                self.add_connection(chosen,noncon,innov)     
                        if indexer == 2:
                            noncon = random.choice([a for a in self.Nodes[2] if a not in [i.output for i in chosen.connections] + [i.input for i in chosen.connections]])
                            self.add_connection(chosen,noncon,innov)
                            self.Nodes[2].pop(self.Nodes[2].index(chosen))
                            self.Nodes[2].insert(self.Nodes[2].index(noncon),chosen) 
                except:
                    #print("dense net found, redoing")
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
    common = []
    for i in poc:
        if i in pfc:
            common.append(random.choice([i,pfc[pfc.index(i)]]))
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
        Nodes[i].type="I"
        DivNodes[0].append(Nodes[i])
    for i in range(pa.info[0],pa.info[1]+pa.info[0]):
        Nodes[i].type="O"
        DivNodes[1].append(Nodes[i])
    for i in range(pa.info[1]+pa.info[0],len(Nodes)):
        DivNodes[2].append(Nodes[i])
    
    child = Network(pa.info[0]-1,pa.info[1],innov)
    child.Connections = Connections
    child.Nodes = DivNodes

    for i in child.Nodes[2]:
        for j in i.connections:
            if j.input.type == "H" and j.disabled == False:
                if child.Nodes[2].index(j.input) > child.Nodes[2].index(i):
                    child.Nodes[2].pop(child.Nodes[2].index(j.input))
                    child.Nodes[2].insert(child.Nodes[2].index(i),j.input)


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

def stress_test():
    a = Network(3,2,inn)
    #a.add_node(inn)
    b = Network(3,2,inn)
    a.fitness,b.fitness = 1,-1
    # a.mutate(inn)
    # b.mutate(inn)
    innovs = []
    time = []
    #CHECK THE 10,000 error
    for i in range(1): 
        c,d = reproduce(a,b,inn),reproduce(a,b,inn)

        oopsies = [c.Nodes[0],c.Nodes[2],c.Nodes[1]]
        previous = (a,b)
        a,b = c,d
        a.fitness,b.fitness = 1,-1
        # print([i.index for i in c.Nodes[2]])
        try:
            c.activate([1,2,3])
        except Exception as e:
            print([a.index for a in oopsies[1]])
            print_connections(c)
            print(e)
            sys.exit()

        innovs.append(len(inn))
        time.append(i)
        if i%100 == 0:
            print("hemlo",i)

    print('done running')
    # plt.plot(time,innovs)
    # plt.show()
    return c,d,previous[0],previous[1],oopsies


c,d,a,b,oopsiess = stress_test()
print("DONE")
print_connections(b)
run = True

def get_coords(net,xp,yp):
    x,y = xp,yp
    coords = [[],[],[]]
    oopsies = [net.Nodes[0],net.Nodes[2],net.Nodes[1]]
    for i in oopsies:
        x+=100
        y = 75+((max([len(j) for j in oopsies])-len(i))/2)*75+yp
        for j in i:
            coords[oopsies.index(i)].append([x,y])
            y+=75
    return coords[0]+coords[2]+coords[1]

def render_net(net,xp,yp,color=(0,0,0),rh = False):
    oopsies = [net.Nodes[0],net.Nodes[2],net.Nodes[1]]
    x,y = xp,yp
    coords = get_coords(net,x,y)
    for i in range(len(oopsies)):
        x+=100
        y = 75+((max([len(j) for j in oopsies])-len(oopsies[i]))/2)*75+yp
        for j in oopsies[i]:
            pygame.draw.circle(wn,color,(x,y),25)
            y+=75
    for i in net.Connections:
        try:
            if i.disabled == False:
                pygame.draw.line(wn,color,coords[i.input.index],coords[i.output.index],max(abs(int(i.weight*10)),1))

        except Exception as e:
            print(e,[len(a) for a in net.Nodes])
    for i in net.Connections:
        try:
            if i.disabled == True and rh:
                pygame.draw.line(wn,(255,0,0),coords[i.input.index],coords[i.output.index],abs(1))

        except Exception as e:
            print(e,[len(a) for a in net.Nodes])
    
uh = Network(3,2,inn)
uh.add_node(inn)
rh = False
while run:
    wn.fill((255,255,255))
    render_net(a,-50,0,rh=rh)
    render_net(b,250,0,color=(255,125,255),rh=rh)
    render_net(c,200,250,color=(125,125,0),rh=rh)
    pygame.display.flip()
    c.activate([1,3,4])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("CHILD MADE WOO")
                c,d = reproduce(a,b,inn),reproduce(a,b,inn)
                oopsies = [c.Nodes[0],c.Nodes[2],c.Nodes[1]]
                previous = (a,b)
                a,b = c,d
                a.fitness,b.fitness = 1,-1
                print_connections(b)
            if event.key == pygame.K_f:
                rh = not rh


#TODO: ADD FUNCTION TO CHECK FOR DENSE NETS (or just use try catch lol)
#TODO 2 Electric Bogaloo: ADD RECURSIVE NETWORK FUNCTIONALITY TO ACTIVATION AND MUTATION
