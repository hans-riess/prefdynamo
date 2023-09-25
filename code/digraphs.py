from networkx import DiGraph,Graph
from networkx import transitive_closure,transitive_reduction,compose,neighbors,is_directed_acyclic_graph,has_path,dfs_preorder_nodes,random_tree
from random import shuffle,sample,seed,choice
from numpy.random import rand
from itertools import permutations

def reflexive_closure(digraph):
    if not isinstance(digraph, DiGraph):
        raise ValueError("Input should be an instance of the 'DiGraph' class.")
    digraph.add_edges_from([(i,i) for i in digraph.nodes()])
    
    return digraph

def intersection(digraph_1,digraph_2):
    if not isinstance(digraph_1, DiGraph):
        raise ValueError("Input should be an instance of the 'DiGraph' class.")
    if not isinstance(digraph_2, DiGraph):
            raise ValueError("Input should be an instance of the 'DiGraph' class.")
    digraph = DiGraph()
    digraph.add_nodes_from(digraph_1.nodes())
    digraph.add_nodes_from(digraph_2.nodes())
    for edge in digraph_1.edges():
        if edge in digraph_2.edges():
            digraph.add_edge(*edge)
    return digraph

def generate_random_preorder(n_nodes, edge_prob):
    # Step 1: Generate a random DAG
    digraph = DiGraph()
    digraph.add_nodes_from(range(n_nodes))
    
    for i, j in permutations(range(n_nodes), 2):
        if has_path(digraph, j, i):  # Ensure acyclicity
            continue
        if edge_prob > rand():
            digraph.add_edge(i, j)
    
    # Step 2: Ensure transitivity
    for i, j in permutations(range(n_nodes), 2):
        if has_path(digraph, i, j) and not digraph.has_edge(i, j):
            digraph.add_edge(i, j)
            
    return digraph

def generate_random_arborescence(num_nodes):
    G = DiGraph()
    nodes = list(range(num_nodes))
    shuffle(nodes)

    root = nodes.pop()
    G.add_node(root)
    
    for node in nodes:
        possible_parents = list(G.nodes())
        parent = choice(possible_parents)
        G.add_edge(parent, node)

    return G

def clean_digraph(digraph):
    #removes self-loops
    edges_to_remove = []
    for edge in digraph.edges():
        if edge[0] == edge[1]:
            edges_to_remove.append(edge)
    digraph.remove_edges_from(edges_to_remove)
    return digraph