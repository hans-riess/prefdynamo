from agents import Preference
from networkx import DiGraph,get_edge_attributes
from networkx.algorithms.tree.branchings import Edmonds

class Greedy:
    def __init__(self,reference_digraph,pref=None):
        #'digraph' is a (possibly complete) weighted digraph from which an agent optimally adds edges to 'pref'
        if pref==None:
            self.preference = Preference(DiGraph()) #empty preference relation
        if pref!=None:
            if not isinstance(pref,Preference):
                ValueError("'pref' must be an instance of 'Preference'.")
            self.preference = pref
        self.reference_digraph = reference_digraph
        self.weight_dict = get_edge_attributes(reference_digraph,'weight') #dictionary storing (possible) edges and weights
     
    def utility(self):
        util = 0
        for edge in self.preference.digraph.edges():
            util+=self.weight_dict[edge]
        return util
    
    def find_optimum(self,max_steps):
        #TODO: may run into issues if 'max_steps' is too large
        for step in range(max_steps):
            utility = {}
            for edge in self.reference_digraph.edges():
                if edge not in self.preference.digraph.edges:
                    new_pref = Preference(DiGraph())
                    an_edge = DiGraph()
                    an_edge.add_edge(*edge)
                    atom = Preference(an_edge)
                    new_pref = self.preference.join(atom)
                    util = 0
                    for edge in new_pref.digraph.edges():
                        util+=self.weight_dict[edge]
                    utility[edge] = util
            edge_to_add = max(utility, key=utility.get)
            self.preference.digraph.add_edge(*edge_to_add)
        return self.preference
