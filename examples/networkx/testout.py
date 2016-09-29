import networkx as nx
G = nx.Graph()
G.add_node((1,2,3))
G.add_node((4,5,6))
G.add_edge((1,2,3),(4,5,6))
print (list(G.nodes()))
