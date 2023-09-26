import numpy as np
from agents import Preference,Agent,SocialNetwork
from digraphs import generate_random_preorder,generate_random_arborescence
from random import choices,seed
from networkx import DiGraph,random_regular_graph,set_node_attributes,neighbors,draw_networkx_nodes,draw_networkx_edges,circular_layout
import matplotlib.pyplot as plt
import csv
from datetime import datetime

#initial data for problem

path = 'experiments/'
experiment_number = 6
experiment_description = 'random initial profiles, fixed regular graph, posterior'
date = datetime.now().strftime('%Y-%m-%d')
n_seed = 29
n_trials = 10
n_iterations = 16
n_agents = 20
n_neighbors = 2
n_alternatives = 5
p_preference = 0.2
energy_method = 'sum' #either 'max' or 'sum'

#seed
seed(n_seed)

#data for each randomly-generated agent
r_values = choices(list(range(1,n_neighbors+1)),k=n_agents) #r-values
update_rules = choices(['posterior'],k=n_agents) #'prior','posterior','meet' or 'join'

#generate a random graph defining agent-agent interactions
graph = random_regular_graph(n_neighbors,n_agents,seed=n_seed)


#write metadata to file
variables = [ 
    ('date',date),
    ('experiment_description', experiment_description),
    ('n_seed', n_seed),
    ('n_trials', n_trials),
    ('n_iterations', n_iterations),
    ('n_agents', n_agents),
    ('n_neighbors', n_neighbors),
    ('n_alternatives', n_alternatives),
    ('p_preference', p_preference),
    ('r_values',r_values),
    ('update_rules',update_rules),
    ('graph',graph.edges()),
    ('energy_method',energy_method)
]
with open(path+'experiment_' + str(experiment_number)+'_metadata.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['data', 'variable'])
    for var_name, var_value in variables:
        writer.writerow([var_name, var_value])

#experiment
losses = np.zeros([n_trials,n_iterations])
for trial in range(n_trials):
    print('trial = '+str(trial))
    print('Preferences updating...')
    agent_dict = {}
    for node in range(n_agents): #initialize each agent
        digraph = generate_random_preorder(n_alternatives,p_preference,n_seed=n_seed+node+trial)
        print('Agent: '+str(node))
        print(digraph.edges)
        agent_dict[node] = Agent(Preference(digraph),r_values[node],update_rules[node])
    network = SocialNetwork(graph,agent_dict) #initialize social network
    #calculate loss
    if energy_method == 'sum':
        initial_loss = 0.5*np.sum(network.distance_matrix(normalized=False))
    if energy_method == 'max':
        initial_loss = np.max(network.distance_matrix(normalized=False))
    print('Initial loss = '+str(initial_loss))
    for t in range(n_iterations):
        #calculate loss
        if energy_method == 'sum':
            loss = 0.5*np.sum(network.distance_matrix(normalized=False))
        if energy_method == 'max':
            loss = np.max(network.distance_matrix(normalized=False))
        print('loss = ' +str(loss))
        losses[trial,t] = loss
        #update preference profile
        network.update_preference_profile()
    print('Done! \n')

#write results to file
header_str = ",".join(map(str, range(n_iterations)))
filename =  path + 'experiment_' + str(experiment_number)  + '.csv'
np.savetxt(filename,losses, delimiter=",",header=header_str,comments="")

