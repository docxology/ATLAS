import networkx as nx
import matplotlib.pyplot as plt
import logging
from typing import Dict, List, Any, Callable, Optional, Union
from ATLAS_utils import ATLASNetwork, save_network_to_file, load_network_from_file, find_shortest_path, get_node_attributes, get_edge_attributes, get_nodes_by_type, get_relationships

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    atlas_network = ATLASNetwork()

    # Adding coffee-related entities
    atlas_network.add_entity('CoffeeBean', attributes={'type': 'Arabica'}, patterns=['BeanPattern'])
    atlas_network.add_entity('Roaster', attributes={'name': 'Roaster One'}, patterns=['RoasterPattern'])
    atlas_network.add_entity('CoffeeShop', attributes={'name': 'Coffee Shop One'}, patterns=['ShopPattern'])

    # Adding coffee-related patterns
    atlas_network.add_pattern('BeanPattern', qkit=['BeanQuery'], parents=[], children=['RoasterPattern'])
    atlas_network.add_pattern('RoasterPattern', qkit=['RoasterQuery'], parents=['BeanPattern'], children=['ShopPattern'])
    atlas_network.add_pattern('ShopPattern', qkit=['ShopQuery'], parents=['RoasterPattern'], children=[])

    # Adding iQueries
    atlas_network.add_iquery('BeanQuery', ref_id='BID1', prompts=['BeanPrompt'])
    atlas_network.add_iquery('RoasterQuery', ref_id='RID1', prompts=['RoasterPrompt'])
    atlas_network.add_iquery('ShopQuery', ref_id='SID1', prompts=['ShopPrompt'])

    # Adding attributes
    atlas_network.add_attribute('BeanAttribute', ref_id='BID1', attributes={'origin': 'Ethiopia'}, patterns=['BeanPattern'])
    atlas_network.add_attribute('RoasterAttribute', ref_id='RID1', attributes={'method': 'Medium Roast'}, patterns=['RoasterPattern'])
    atlas_network.add_attribute('ShopAttribute', ref_id='SID1', attributes={'location': 'Downtown'}, patterns=['ShopPattern'])

    # Adding prompt interfaces
    atlas_network.add_prompt_interface('BeanPrompt', function=lambda x: x)
    atlas_network.add_prompt_interface('RoasterPrompt', function=lambda x: x)
    atlas_network.add_prompt_interface('ShopPrompt', function=lambda x: x)

    # Adding relationships
    atlas_network.add_relationship('CoffeeBean', 'Roaster', 'processed_by')
    atlas_network.add_relationship('Roaster', 'CoffeeShop', 'supplies')
    atlas_network.add_relationship('BeanPattern', 'RoasterPattern', 'parent_of')
    atlas_network.add_relationship('RoasterPattern', 'ShopPattern', 'parent_of')
    atlas_network.add_relationship('BeanQuery', 'BeanPrompt', 'uses')
    atlas_network.add_relationship('RoasterQuery', 'RoasterPrompt', 'uses')
    atlas_network.add_relationship('ShopQuery', 'ShopPrompt', 'uses')

    # Visualize the network
    atlas_network.visualize()

    # Summarize to terminal
    logging.info("Summary of the ATLAS Coffee Network:")
    for node_type in ['entity', 'pattern', 'iquery', 'attribute', 'prompt_interface']:
        nodes = get_nodes_by_type(atlas_network, node_type)
        logging.info(f"{node_type.capitalize()} nodes: {nodes}")

    for edge in atlas_network.graph.edges(data=True):
        logging.info(f"Edge: {edge}")

if __name__ == "__main__":
    main()