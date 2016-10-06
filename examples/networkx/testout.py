import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
#nodelist = [(1,2,3), (4,5,6),(7,8,9)]

#G.add_node((1,2,3))
#G.add_node((4,5,6))
#G.add_nodes_from(nodelist)
G.add_edge((1,2,3),(4,5,6), distance = 4.5)
G.add_edge((4,5,6),(70,8,9), distance = 10)
G.add_edge((70,8,9), (10,5,9), distance = 20)
G.add_edge((1,2,3), (10,5,9), distance = 20)
print G.nodes(data=True)
#print type(nx.shortest_path(G, source = (1,2,3), target = (70,8,9)))
print G.edges(data=True)[0][2]["distance"]
#nx.draw(G)
#plt.show()