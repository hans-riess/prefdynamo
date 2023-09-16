from networkx import DiGraph,Graph
from networkx import transitive_closure,transitive_reduction,compose,neighbors,is_directed_acyclic_graph
from random import shuffle,sample,seed

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

def generate_random_dag(n_alternatives, n_comparisons,seed_value=None):
    if seed_value is not None:
        seed(seed_value)
    dag = DiGraph()
    dag.add_nodes_from(range(n_alternatives))
    alternatives = list(dag.nodes())
    shuffle(alternatives)

    while dag.number_of_edges() < n_comparisons:
        # Pick two random alternatives
        source, target = sample(alternatives, 2)
        
        # Ensure the source node comes before the target node in the ordering
        if alternatives.index(source) < alternatives.index(target):
            if not dag.has_edge(source, target):
                dag.add_edge(source, target)
    return dag

def clean_digraph(digraph):
    #for visualizing preferences
    edges_to_remove = []
    for edge in digraph.edges():
        if edge[0] == edge[1]:
            edges_to_remove.append(edge)
    digraph.remove_edges_from(edges_to_remove)
    if is_directed_acyclic_graph(digraph) == False:
        raise ValueError("'DiGraph' instance must be a DAG.")
    return transitive_reduction(digraph)