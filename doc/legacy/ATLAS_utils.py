import logging
import networkx as nx
import matplotlib.pyplot as plt 
from typing import Dict, List, Any, Callable, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ATLASNetwork:
    def __init__(self):
        self.graph: nx.DiGraph = nx.DiGraph()
        logging.info("Initialized ATLAS Network")

    def add_entity(self, entity_id: str, attributes: Optional[Dict[str, Any]] = None, 
                   patterns: Optional[List[str]] = None) -> None:
        self.graph.add_node(entity_id, node_type='entity', 
                            attributes=attributes or {}, patterns=patterns or [])
        logging.info(f"Added entity: {entity_id} with attributes: {attributes} and patterns: {patterns}")

    def add_pattern(self, pattern_id: str, qkit: Optional[List[str]] = None, 
                    parents: Optional[List[str]] = None, children: Optional[List[str]] = None) -> None:
        self.graph.add_node(pattern_id, node_type='pattern', 
                            qkit=qkit or [], parents=parents or [], children=children or [])
        logging.info(f"Added pattern: {pattern_id} with qkit: {qkit}, parents: {parents}, children: {children}")

    def add_iquery(self, iquery_id: str, ref_id: str, prompts: List[str]) -> None:
        self.graph.add_node(iquery_id, node_type='iquery', ref_id=ref_id, prompts=prompts)
        logging.info(f"Added iQuery: {iquery_id} with ref_id: {ref_id} and prompts: {prompts}")

    def add_attribute(self, attribute_id: str, ref_id: str, 
                      attributes: Optional[Dict[str, Any]] = None, 
                      patterns: Optional[List[str]] = None) -> None:
        self.graph.add_node(attribute_id, node_type='attribute', ref_id=ref_id, 
                            attributes=attributes or {}, patterns=patterns or [])
        logging.info(f"Added attribute: {attribute_id} with ref_id: {ref_id}, attributes: {attributes}, patterns: {patterns}")

    def add_prompt_interface(self, pi_id: str, function: Callable) -> None:
        self.graph.add_node(pi_id, node_type='prompt_interface', function=function)
        logging.info(f"Added prompt interface: {pi_id}")

    def add_relationship(self, source: str, target: str, relationship_type: str) -> None:
        self.graph.add_edge(source, target, relationship_type=relationship_type)
        logging.info(f"Added relationship from {source} to {target} of type {relationship_type}")

    def get_nodes_by_type(self, node_type: str) -> List[str]:
        return [node for node, data in self.graph.nodes(data=True) if data.get('node_type') == node_type]

    def get_node_attributes(self, node_id: str) -> Dict[str, Any]:
        return self.graph.nodes[node_id]

    def get_relationships(self, node_id: str, relationship_type: Optional[str] = None) -> List[tuple]:
        if relationship_type:
            return [(u, v, d) for (u, v, d) in self.graph.edges(node_id, data=True) 
                    if d.get('relationship_type') == relationship_type]
        return list(self.graph.edges(node_id, data=True))

    def visualize(self) -> None:
        pos = nx.spring_layout(self.graph)
        node_colors = [self._get_node_color(data['node_type']) for _, data in self.graph.nodes(data=True)]
        nx.draw(self.graph, pos, with_labels=True, node_size=3000, node_color=node_colors, 
                font_size=10, font_weight="bold")
        edge_labels = nx.get_edge_attributes(self.graph, 'relationship_type')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        plt.show()
        logging.info("Visualized the network")

    @staticmethod
    def _get_node_color(node_type: str) -> str:
        color_map = {
            'entity': 'skyblue',
            'pattern': 'lightgreen',
            'iquery': 'lightcoral',
            'attribute': 'lightyellow',
            'prompt_interface': 'lightpink'
        }
        return color_map.get(node_type, 'gray')

def save_network_to_file(atlas_network: ATLASNetwork, file_path: str) -> None:
    """
    Save the ATLAS network to a file in GraphML format.
    
    :param atlas_network: ATLASNetwork instance
    :param file_path: Path to the file where the network will be saved
    """
    try:
        nx.write_graphml(atlas_network.graph, file_path)
        logging.info(f"Network saved to {file_path}")
    except Exception as e:
        logging.error(f"Failed to save network to file: {e}")

def load_network_from_file(file_path: str) -> ATLASNetwork:
    """
    Load an ATLAS network from a GraphML file.
    
    :param file_path: Path to the GraphML file
    :return: ATLASNetwork instance
    """
    try:
        graph = nx.read_graphml(file_path)
        atlas_network = ATLASNetwork()
        atlas_network.graph = graph
        logging.info(f"Network loaded from {file_path}")
        return atlas_network
    except Exception as e:
        logging.error(f"Failed to load network from file: {e}")
        return None

def find_shortest_path(atlas_network: ATLASNetwork, source: str, target: str) -> list:
    """
    Find the shortest path between two nodes in the ATLAS network.
    
    :param atlas_network: ATLASNetwork instance
    :param source: Source node ID
    :param target: Target node ID
    :return: List of nodes representing the shortest path
    """
    try:
        path = nx.shortest_path(atlas_network.graph, source=source, target=target)
        logging.info(f"Shortest path from {source} to {target}: {path}")
        return path
    except nx.NetworkXNoPath:
        logging.warning(f"No path found from {source} to {target}")
        return None
    except Exception as e:
        logging.error(f"Error finding shortest path: {e}")
        return None

def get_node_attributes(atlas_network: ATLASNetwork, node_id: str) -> dict:
    """
    Get the attributes of a node in the ATLAS network.
    
    :param atlas_network: ATLASNetwork instance
    :param node_id: Node ID
    :return: Dictionary of node attributes
    """
    try:
        attributes = atlas_network.graph.nodes[node_id]
        logging.info(f"Attributes of node {node_id}: {attributes}")
        return attributes
    except KeyError:
        logging.warning(f"Node {node_id} not found in the network")
        return None
    except Exception as e:
        logging.error(f"Error getting attributes of node {node_id}: {e}")
        return None

def get_edge_attributes(atlas_network: ATLASNetwork, source: str, target: str) -> dict:
    """
    Get the attributes of an edge in the ATLAS network.
    
    :param atlas_network: ATLASNetwork instance
    :param source: Source node ID
    :param target: Target node ID
    :return: Dictionary of edge attributes
    """
    try:
        attributes = atlas_network.graph.edges[source, target]
        logging.info(f"Attributes of edge from {source} to {target}: {attributes}")
        return attributes
    except KeyError:
        logging.warning(f"Edge from {source} to {target} not found in the network")
        return None
    except Exception as e:
        logging.error(f"Error getting attributes of edge from {source} to {target}: {e}")
        return None

def get_nodes_by_type(atlas_network: ATLASNetwork, node_type: str) -> list:
    """
    Get all nodes of a specific type in the ATLAS network.
    
    :param atlas_network: ATLASNetwork instance
    :param node_type: Type of nodes to retrieve
    :return: List of node IDs
    """
    nodes = [node for node, data in atlas_network.graph.nodes(data=True) if data.get('node_type') == node_type]
    logging.info(f"Nodes of type {node_type}: {nodes}")
    return nodes

def get_relationships(atlas_network: ATLASNetwork, node_id: str, relationship_type: Optional[str] = None) -> list:
    """
    Get all relationships of a specific type for a node in the ATLAS network.
    
    :param atlas_network: ATLASNetwork instance
    :param node_id: Node ID
    :param relationship_type: Type of relationships to retrieve (optional)
    :return: List of relationships
    """
    try:
        if relationship_type:
            relationships = [(u, v, d) for (u, v, d) in atlas_network.graph.edges(node_id, data=True) 
                             if d.get('relationship_type') == relationship_type]
        else:
            relationships = list(atlas_network.graph.edges(node_id, data=True))
        logging.info(f"Relationships of node {node_id} with type {relationship_type}: {relationships}")
        return relationships
    except Exception as e:
        logging.error(f"Error getting relationships of node {node_id}: {e}")
        return None