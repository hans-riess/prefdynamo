from agents import Preference,Agent,SocialNetwork
from concurrent.futures import ProcessPoolExecutor


def update_preference_profile(network):
    #Input: 'network' of class "SocialNetowork'
    #Output: 'new_network' of class 'SocialNetwork'
    if not isinstance(network,SocialNetwork):
        raise TypeError("'network' must be an instance of 'Network'")
    nodes = list(network.graph.nodes())
    results = []
    if __name__ == '__main__':
        with ProcessPoolExecutor() as executor:
                results = list(executor.map(network.update_preference,nodes))
    new_agent_dict = dict(zip(nodes,results))
    network.agent_dict = new_agent_dict