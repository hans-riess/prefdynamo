from networkx import DiGraph,Graph,set_node_attributes,transitive_closure,compose
from digraphs import reflexive_closure,intersection,clean_digraph
from functools import reduce
from itertools import combinations
import copy

class Preference(DiGraph):
    def __init__(self, digraph, **kwargs):
        if not isinstance(digraph, DiGraph):
            raise ValueError("Input should be an instance of the 'DiGraph' class.")
        super().__init__(digraph, **kwargs)
        self.digraph = transitive_closure(reflexive_closure(digraph)).copy()
        self.alternatives = digraph.nodes()
        
    def join(self,other):
        #least upper bound of two preference relation under information order
        if not isinstance(other, Preference):
            raise ValueError("Input should be an instance of the 'Preference' class.")
        return Preference(transitive_closure(reflexive_closure(compose(self.digraph, other.digraph))).copy())
    
    def meet(self,other):
        #greatest lower bound of two preference relation under information order
        if not isinstance(other, Preference):
            raise ValueError("Input should be an instance of the 'Pref' class.")
        return Preference(intersection(self.digraph,other.digraph).copy())

class Agent(Preference):
    def __init__(self,preference,r_median,update_rule,**kwargs):
        if not isinstance(preference, Preference):
            raise ValueError("Input should be an instance of the 'Preference' class.")
        if update_rule not in {'prior','posterior','meet','join'}:
            raise ValueError("Input should be 'prior','posterior','meet', or 'join'")
        self.r_median = r_median #the type of aggregation 1<=r<=len(agent_list)
        self.update_rule = update_rule #keeps prior pref, uses posterior (aggregated), or join/meet of both
        super().__init__(preference.digraph,**kwargs)
        self.preference = preference
        
    def aggregate(self,agent_list):
        #if r==len(agent_list), then a join-projection
        #if r==1, then a meet-projection
        r = max(1,min(self.r_median, len(agent_list)))
        pref_list = []
        for agent in agent_list:
            if not isinstance(agent, Agent):
                raise ValueError("Input should be an instance of the 'Agent' class.")
            pref_list.append(agent.preference)
        groups = [list(comb) for comb in combinations(pref_list,r)]
        return reduce(self.preference.join,[reduce(self.preference.meet,group) for group in groups])
    
    def update(self,agent_list):
        if self.update_rule == 'prior':
            return Preference(self.digraph)
        if self.update_rule == 'posterior':
            return self.aggregate(agent_list)
        if self.update_rule == 'join':
            return Preference(self.digraph).join(self.aggregate(agent_list))
        if self.update_rule == 'meet':
            return Preference(self.digraph).meet(self.aggregate(agent_list))

class SocialNetwork:
    def __init__(self,graph,agent_dict):
        #'graph' is a networkx class 'Graph'
        #'pref_dict' is a dictionary '{node, agent}' where 'agent' is an instance of 'Agent'
        if not isinstance(graph,Graph):
            raise ValueError("'graph' must be an instance of 'Graph'")
        for node in agent_dict.keys():
            if not isinstance(agent_dict[node],Agent):
                raise ValueError("The values of 'pref_dict' must be instances of the class 'Preference")
        set_node_attributes(graph, agent_dict ,'agent')
        self.graph = graph
        self.agent_dict = agent_dict
        
    def update_preference(self,node):
        #Input: networkx 'graph' of class "Graph" with node-attribute 'agent' of class 'Agent'
        #Output: instance of class 'Preference'
        agent = self.graph.nodes[node]['agent']
        agent_list = [self.graph.nodes[j]['agent'] for j in self.graph.neighbors(node)]
        return agent.update(agent_list)
    
    def get_digraph(self,node,option=None):
        digraph = self.graph.nodes[node]['agent'].digraph
        if option == 'clean':
            return clean_digraph(digraph)
        else:
            return digraph
        
    def copy(self):
        new_graph = self.graph.copy()
        set_node_attributes(new_graph, name='agent', values=None)
        new_agent_dict = copy.deepcopy(self.agent_dict)
        return SocialNetwork(new_graph,new_agent_dict)