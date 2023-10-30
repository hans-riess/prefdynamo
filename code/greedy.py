from agents import Preference
from networkx import DiGraph,get_edge_attributes,transitive_closure
from networkx.algorithms.tree.branchings import Edmonds
from digraphs import clean_digraph

class NaiveGreedy:
    def __init__(self,ref_digraph,pref=None):
        '''
        The variable 'ref_digraph' is a weighted digraph, an instance of DiGraph, from which an agent optimally adds edges to 'pref'.
        In most cases, 'ref_digraph' is the complete graph and the weight on 'ref_digraph' is the utility for adding each edge.
        '''
        if pref==None:
            self.preference = Preference(DiGraph()) #empty preference relation
        if pref!=None:
            if not isinstance(pref,Preference):
                ValueError("'pref' must be an instance of 'Preference'.")
            self.preference = pref
        self.ref_digraph = ref_digraph
        self.weight_dict = get_edge_attributes(ref_digraph,'weight') #dictionary storing (possible) edges and weights
     
    def utility(self):
        util = 0
        '''
        This method takes the current prefernce diagraph and sums the value of the utilities (i.e. weights) over every edge.
        '''
        for edge in self.preference.digraph.edges():
            util+=self.weight_dict[edge]
        return util

    def find_optimum(self, n_steps):
        '''
        This method adds edges one-by-one from ref_digraph, applies the transitive closure, and chooses the edge to add that results in
        the highest utility.
        '''
        for step in range(n_steps):
            utility = {}
            for edge in self.ref_digraph.edges(): #looping over every edge in the reference digraph
                if edge not in self.preference.digraph.edges: #we consider only edges that were not already addded to the current preference digraph
                    new_pref = Preference(DiGraph())
                    an_edge = DiGraph()
                    an_edge.add_edge(*edge) #we construct a weighted digraph with a single edge
                    atom = Preference(an_edge)
                    new_pref = self.preference.join(atom)
                    #For each possible edge to add, we calculate the utility as the result of adding that edge.
                    util = 0
                    for edge in new_pref.digraph.edges():
                        util += self.weight_dict[edge]
                    utility[edge] = util
            if utility!=dict():
                edge_to_add = max(utility, key=utility.get)
                #We choose the edge that maximizes the utility
                self.preference.digraph.add_edge(*edge_to_add)
                # Ensure the preference relation is transitively closed and has no self-loops.
                self.preference.digraph = clean_digraph(transitive_closure(self.preference.digraph))
        return self.preference

class BruteForce:
    #TO WRITE
    def __init__(self):
        return True










