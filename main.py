
import networkx as nx
import matplotlib.pyplot as plt
from itertools import permutations



class Job(object):
	 def __init__(self, Id, r, p):
	 	self.Id = Id
	 	self.r = r  # ruta
	 	self.p = p  # tiempo de procesamineto

#----------------------------------------------------------------------------------------------------------

jobs = {}   # id, maquinas orden(procesos),  tiempo
jobs[1] = Job(1, [1,2,3], [10, 8, 4])
jobs[2] = Job(2, [2,1,4,3,5], [8,3,5,6,11])
jobs[3] = Job(3, [1,2,4], [4,7,3])
jobs[4] = Job(4, [1,3,4,2,5], [4,7,3,3,15])
jobs[5] = Job(5, [1,4,2,3], [5,3,3,1])
jobs[6] = Job(6, [5,4,3,2,1], [4,7,3,2,1])

#----------------------------------------------------------------------------------------------------------

class Jobshop(nx.DiGraph):     # es para crear el grafo
	def __init__(self):
	        super().__init__()
	        self.machines = {}
	        #start node
	        self.add_node("U", p=0)
	        #finish node
	        self.add_node("V", p=0)
	        #set dirty flag
	        self._dirty = True
	        #set initial makespan
	        self._makespan = -1
	        #define criticla path
	        self._criticalPath = None

	def add_node(self, *args, **kwargs):
       										# _dirty sirve para efectuar una conexion con la funcion "update"
		self._dirty = True
		super().add_node(*args, **kwargs)   # puede agregar nodos sin restricciones con atributos

	def add_nodes_from(self, *args, **kwargs):
        									# _dirty sirve para efectuar una conexion con la funcion "update" 
		self._dirty = True
		super().add_nodes_from(*args, **kwargs)  # agrega un contenedor de nodos, al parecer los nodos del mismo argumento solo toma uno.

	def add_edge(self, *args):
        									# _dirty sirve para efectuar una conexion con la funcion "update"	
		self._dirty = True
		super().add_edge(*args)             # aca une dos nodos, tambien se le asigna el valor a ese borde, todo en args  (agrega de a un solo borde)

	def add_edges_from(self, *args, **kwargs):
         									# _dirty sirve para efectuar una conexion con la funcion "update"
		self._dirty = True
		super().add_edges_from(*args, **kwargs) # agregar mas de un borde a los nodos,  pueden ser los mismos nodos, pero no el mismo borde.

	def remove_node(self, *args, **kwargs):
         									# _dirty sirve para efectuar una conexion con la funcion "update"
		self._dirty = True
		super().remove_node(*args, **kwargs)  # elimina el nodo especificado y todos los bordes adyacentes

	def remove_nodes_from(self, *args, **kwargs):
        									# _dirty sirve para efectuar una conexion con la funcion "update"
		self._dirty = True
		super().remove_nodes_from(*args, **kwargs)  # elimina varios nodos, y  sus bordes igual

	def remove_edge(self, *args):
         									# _dirty sirve para efectuar una conexion con la funcion "update"
		self._dirty = True
		super().remove_edge(*args)         # elimina borde entre dos nodos especificados

	def remove_edges_from(self, *args, **kwargs):
        									# _dirty sirve para efectuar una conexion con la funcion "update"
		self._dirty = True
		super().remove_edges_from(*args, **kwargs)  # elimina varios bordes.

	def handleJobRoutings(self, jobs):   # crea los bordes de los graficos junto con los nodos de oirguen y finalizar
		for j in jobs.values():
            							# agrega borde de inicio y que los iniciales de las tareas, o puede ser el de la operacion1 de la tarea 1 solamente
			self.add_edge("U", (j.r[0], j.Id))
            							#agregar los bordes (orden de procesamiento) enrutando los nodos (tareas), pero no veo que agregue el tiempo de procesamiento a los bordes
			for m, n in zip(j.r[:-1], j.r[1:]):
				self.add_edge((m, j.Id), (n, j.Id))
                                        # agrega el borde hacie el ultimo nodo
			self.add_edge((j.r[-1], j.Id), "V")

	def handleJobProcessingTimes(self, jobs):
		for j in jobs.values():
		  									 # agrega cada tarea y los tiempo de procesamineto
			for m, p in zip(j.r, j.p):
				self.add_node((m, j.Id), p=p)

#---------------------------------- no probado---------------------------------------
	def makeMachineSubgraphs(self):
	        machineIds = set(ij[0] for ij in self if ij[0] not in ("U", "V"))
	        #print(machineIds)
	        for m in machineIds:
	            self.machines[m] = self.subgraph(ij for ij in self if ij[0] == m)
	            #print(list(self.machines[m].nodes))
	            #self.machines[m].remove_nodes_from(["U", "V"])
	def addJobs(self, jobs):
			self.handleJobRoutings(jobs)
			self.handleJobProcessingTimes(jobs)
			self.makeMachineSubgraphs()
	        
	def output(self):
	        for m in sorted(self.machines):  # itera sobre el numero de maquinas de manera ascendente
	            for j in sorted(self.machines[m]):	 # lo mismo pero en la maquina anterior
	                print("{}: {}".format(j, self.node[j]['C']))

#------------------------------------Seguimos------------------------------------------------------

	def _forward(self):   # hacia delante
	        for n in nx.topological_sort(self):   # itera sobre el numero de nodos de la red que estan ordenados topologicamente ( inicia u a fin v)
	            S = max([self.nodes[j]['C'] for j in self.predecessors(n)], default = 0)  # el for es sobre iterar en el numero de nodos que preceden a al nodo n
	            self.add_node(n, S = S, C = S + self.nodes[n]['p'])    # no entendi bien

	def _backward(self):  # esta es como lo mismo que la anterior, solo que al  reves, hacia atras
	        for n in list(reversed(list(nx.topological_sort(self)))):
	            Cp = min([self.nodes[j]['Sp'] for j in self.successors(n)], default = self._makespan)
	            self.add_node(n, Sp = Cp - self.nodes[n]['p'], Cp = Cp)


	def _computeCriticalPath(self):
	        G = set()   # crea una especie de tupla (eso es set) pero esta no puede ser modificada en los elementos que la componen, no obstante se pueden eleminar y agregar uno  nuevo
	        for n in self:
	            if self.nodes[n]['C'] == self.nodes[n]['Cp']:  # detectar los nodos que estan despues de este.
	                G.add(n)  # agrega ese nodo
	        self._criticalPath = self.subgraph(G)  # y este es para almacenra el camino critico.
	
	@property
	def makespan(self):
	        if self._dirty:
	            self._update()
	        return self._makespan
	@property
	def criticalPath(self):
	        if self._dirty:
	            self._update()
	        return self._criticalPath

	def _update(self):
	        self._forward()
	        self._makespan = max(nx.get_node_attributes(self, 'C').values())
	        self._backward()
	        self._computeCriticalPath()
	        self._dirty = False

class Shift(Jobshop):
    def output(self):
        print("makespan: ", self.makespan)
        for i in self.machines:
            print("Machine: "+str(i))
            s = "{0:<7s}".format("jobs:")
            for ij in sorted(self.machines[i]):
                if ij in ("U", "V"):
                    continue
                s += "{0:>5d}".format(ij[1])
            print(s)
            s = "{0:<7s}".format("p:")
            for ij in sorted(self.machines[i]):
                if ij in ("U", "V"):
                    continue
                s += "{0:>5d}".format(self.nodes[ij]['p'])
            print(s)
            s = "{0:<7s}".format("r:")
            for ij in sorted(self.machines[i]):
                if ij in ("U", "V"):
                    continue
                s += "{0:>5d}".format(self.nodes[ij]['S'])
            print(s)
            s = "{0:<7s}".format("d:")
            for ij in sorted(self.machines[i]):
                if ij in ("U", "V"):
                    continue
                s += "{0:>5d}".format(self.nodes[ij]['Cp'])
            print(s)
            print("\n")


    def computeLmax(self): # la tarea mas atrasada
	        for m in self.machines:
	            lateness = {}
	            for seq in permutations(self.machines[m]):   # hace un for en todas las posibles combinaciones de maquinas
	                release = [self.nodes[j]['S'] for j in seq]
	                due = [self.nodes[j]['Cp'] for j in seq]
	                finish = [0]*len(release)
	                for i, j in enumerate(seq):
	                    finish[i] = max(finish[i-1], release[i]) +self.nodes[j]['p']
	                late = max([f-d for d,f in zip(due,finish)])
	                lateness[seq] = late
	            s, l = argmin_kv(lateness)
	            print("Machine: {}, lateness: {}, optimal seq: {}".format(m, l, s))


def argmin_kv(d):
    """
    esta funcion sirve para lmax, lo cual esta asociado con el retraso asociado
    """
    return min(d.items(), key=lambda x: x[1])

#------------------------ --------------------------------------------------------------------------

js = Shift()
#js.output()

#js.handleJobRoutings(jobs)
#js.handleJobProcessingTimes(jobs)
js.addJobs(jobs)  #, aca ya se construyo la red de nodos, lo compruebas con print(list(js.nodes(data= True)))
js.criticalPath
js.output()



js.computeLmax()
#H = sum(js.nodes[j]['p'] for j in js)  # suma de todo los tiempos
#print (H)

#nx.draw(js,cmap = plt.get_cmap('jet'), node_color = 'blue',with_labels=True)
#plt.show()
"""
for j in jobs.values():
		  									 # agrega cada tarea y los tiempo de procesamineto
			for m, p in zip(j.r, j.p):
				print(p)""" # esra para mostrar los tiempos

#print(list(js.nodes(data= True)))



# luego de esto, el programa nos entrega la secuencia optima, y agregamos esta secuencia con js.add_edges_from

# para maquina 1

js.add_edges_from([((5,6), (5,4)), ((5,4),(5,2))])
js.criticalPath
js.output()
js.computeLmax()


# y aca vemos como se van agregando los ejes 
#nx.draw(js,cmap = plt.get_cmap('jet'), node_color = 'blue',with_labels=True)
#plt.show()



nx.draw(js,cmap = plt.get_cmap('jet'), node_color = 'blue',with_labels=True)
plt.show()

#--------------------------------------------------------------------------------------------------------------------------


