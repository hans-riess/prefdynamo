from networkx import DiGraph,Graph,set_node_attributes,get_node_attributes,transitive_closure,compose
from digraphs import reflexive_closure,intersection,clean_digraph
from functools import reduce
from itertools import combinations
from networkx import draw_networkx_nodes,draw_networkx_edges,draw_networkx_labels,draw_networkx_edge_labels,circular_layout
import matplotlib.pyplot as plt
from numpy import zeros,amax,amin
import copy

class Preference(DiGraph):
    def __init__(self, digraph,**kwargs):
        if not isinstance(digraph, DiGraph):
            raise ValueError("Input should be an instance of the 'DiGraph' class.")
        # super().__init__(digraph,utility=None, **kwargs)
        self.digraph = digraph
        self.n_alternatives = len(digraph.nodes)
        
    def join(self,other):
        #least upper bound of two preference relations under information order
        if not isinstance(other, Preference):
            raise ValueError("Input should be an instance of the 'Preference' class.")
        return Preference(clean_digraph(transitive_closure(compose(self.digraph, other.digraph))).copy())
    
    def meet(self,other):
        #greatest lower bound of two preference relation under information order
        if not isinstance(other, Preference):
            raise ValueError("Input should be an instance of the 'Pref' class.")
        return Preference(intersection(self.digraph,other.digraph).copy())
    
    def tau_distance(self,other):
        if not isinstance(other,Preference):
            raise ValueError("Input should be an instance of the 'Pref' class.")
        if len(self.digraph) != len(other.digraph):
            raise ValueError("Digraphs should have same number of nodes.")
        dist = 0
        for i in range(self.n_alternatives):
            for j in range(self.n_alternatives):
                if (i,j) in self.digraph.edges and (j,i) in other.digraph.edges:
                    dist+=1
        return dist
    
    def clean(self):
        return Preference(clean_digraph(self.digraph).copy())
    
    def plot(self,edge_color='blue',**kwargs):
        pos = circular_layout(self.digraph)
        draw_networkx_nodes(self.digraph,pos,node_color='black',node_size=5)
        draw_networkx_edges(self.digraph,pos,edge_color=edge_color,width=1, alpha=0.5)
        

class Agent(Preference):
    def __init__(self,preference,r_median,update_rule):
        if not isinstance(preference, Preference):
            raise ValueError("Input should be an instance of the 'Preference' class.")
        self.update_rules = ['prior','posterior','meet','join']
        if update_rule not in self.update_rules:
            raise ValueError("Input should be 'prior','posterior','meet', or 'join'")
        self.r_median = r_median #the type of aggregation 1<=r<=len(agent_list)
        self.update_rule = update_rule
        self.initial_preference = preference
        self.preference = preference
        self.update_rule = update_rule
        
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
        return reduce(Preference.join,[reduce(Preference.meet,group) for group in groups])
    
    def update(self,agent_list):
        if self.update_rule == 'prior':
            return self.preference
        if self.update_rule == 'posterior':
            return self.aggregate(agent_list)
        if self.update_rule == 'join':
            return self.preference.join(self.aggregate(agent_list))
        if self.update_rule == 'meet':
            return self.preference.meet(self.aggregate(agent_list))

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
        self.n_agents = len(graph.nodes)
        self.agent_dict = agent_dict
        
    def update_preference(self,node):
        if node not in self.graph.nodes:
            raise ValueError("'node' must be in graph.")
        agent = self.agent_dict[node]
        agent_list = [self.agent_dict[j] for j in self.graph.neighbors(node)]
        return agent.update(agent_list)
        
    def update_preference_profile(self):
        new_agent_dict = {}
        for node in self.graph.nodes:
            new_agent_dict[node] = Agent(self.update_preference(node),self.agent_dict[node].r_median,self.agent_dict[node].update_rule)
        self.agent_dict = new_agent_dict.copy()
    
    def get_digraph(self,node,option=None):
        digraph = self.graph.nodes[node]['agent'].preference.digraph
        if option == 'clean':
            return clean_digraph(digraph)
        else:
            return digraph

    def distance_matrix(self,normalized=False):
        distance_matrix = zeros([self.n_agents, self.n_agents])
        nodes = list(self.graph.nodes())
        for i, node_i in enumerate(nodes):
            for j, node_j in enumerate(nodes):
                if (node_i, node_j) in self.graph.edges():
                    try:
                        distance_matrix[i, j] = self.agent_dict[node_i].preference.tau_distance(self.agent_dict[node_j].preference)
                    except KeyError:
                        print(f"Error: Missing keys {node_i} or {node_j} in agent_dict.")
        # Normalizing the distance matrix
        min_val = amin(distance_matrix)
        max_val = amax(distance_matrix)
        range_val = max_val - min_val
        if range_val != 0:  # To avoid division by zero
            normalized_distance_matrix = (distance_matrix - min_val) / range_val
        else:
            normalized_distance_matrix = distance_matrix - min_val

        if normalized == False:
            return distance_matrix
        if normalized == True:
            return normalized_distance_matrix
        
    def copy(self):
        new_graph = self.graph.copy()
        set_node_attributes(new_graph, name='agent', values=None)
        new_agent_dict = copy.deepcopy(self.agent_dict)
        return SocialNetwork(new_graph,new_agent_dict)