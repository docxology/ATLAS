import networkx as nx
import matplotlib.pyplot as plt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ATLASNetwork:
    def __init__(self):
        """
        Initializes the ATLAS Network as a directed graph.
        """
        self.graph = nx.DiGraph()
        logging.info("Initialized ATLAS Network")

    def add_entity(self, entity_id: str, attributes: dict = None, patterns: list = None) -> bool:
        """
        Adds an entity to the network with optional attributes and patterns.

        Parameters:
        entity_id (str): The unique identifier for the entity.
        attributes (dict, optional): A dictionary of attributes for the entity. Defaults to an empty dictionary.
        patterns (list, optional): A list of patterns associated with the entity. Defaults to an empty list.

        Notes:
        If attributes or patterns are not provided, they default to an empty dictionary or list, respectively.

        Returns:
        bool: True if the entity is added successfully.
        """
        self.graph.add_node(entity_id, attributes=attributes or {}, patterns=patterns or [])
        logging.info(f"Added entity: {entity_id} with attributes: {attributes} and patterns: {patterns}")
        return True

    def add_pattern(self, pattern_id: str, qkit: list = None, parents: list = None, children: list = None) -> bool:
        """
        Adds a pattern to the network with optional qkit, parents, and children.

        Parameters:
        pattern_id (str): The unique identifier for the pattern.
        qkit (list, optional): A list of qkit associated with the pattern. Defaults to an empty list.
        parents (list, optional): A list of parent patterns. Defaults to an empty list.
        children (list, optional): A list of child patterns. Defaults to an empty list.

        Notes:
        If qkit, parents, or children are not provided, they default to an empty list.

        Returns:
        bool: True if the pattern is added successfully.
        """
        self.graph.add_node(pattern_id, qkit=qkit or [], parents=parents or [], children=children or [])
        logging.info(f"Added pattern: {pattern_id} with qkit: {qkit}, parents: {parents}, children: {children}")
        return True

    def add_iquery(self, iquery_id: str, ref_id: str, prompts: list) -> bool:
        """
        Adds an iQuery to the network.

        Parameters:
        iquery_id (str): The unique identifier for the iQuery.
        ref_id (str): The reference identifier associated with the iQuery.
        prompts (list): A list of prompts associated with the iQuery.

        Returns:
        bool: True if the iQuery is added successfully.
        """
        self.graph.add_node(iquery_id, ref_id=ref_id, prompts=prompts)
        logging.info(f"Added iQuery: {iquery_id} with ref_id: {ref_id} and prompts: {prompts}")
        return True

    def add_attribute(self, attribute_id: str, ref_id: str, attributes: dict = None, patterns: list = None) -> bool:
        """
        Adds an attribute to the network with optional attributes and patterns.

        Parameters:
        attribute_id (str): The unique identifier for the attribute.
        ref_id (str): The reference identifier associated with the attribute.
        attributes (dict, optional): A dictionary of attributes. Defaults to an empty dictionary.
        patterns (list, optional): A list of patterns associated with the attribute. Defaults to an empty list.

        Notes:
        If attributes or patterns are not provided, they default to an empty dictionary or list, respectively.

        Returns:
        bool: True if the attribute is added successfully.
        """
        self.graph.add_node(attribute_id, ref_id=ref_id, attributes=attributes or {}, patterns=patterns or [])
        logging.info(f"Added attribute: {attribute_id} with ref_id: {ref_id}, attributes: {attributes}, patterns: {patterns}")
        return True

    def add_prompt_interface(self, pi_id: str, function) -> bool:
        """
        Adds a prompt interface to the network.

        Parameters:
        pi_id (str): The unique identifier for the prompt interface.
        function (callable): The function associated with the prompt interface.

        Returns:
        bool: True if the prompt interface is added successfully.
        """
        self.graph.add_node(pi_id, function=function)
        logging.info(f"Added prompt interface: {pi_id}")
        return True

    def add_relationship(self, source: str, target: str, relationship_type: str) -> bool:
        """
        Adds a relationship between two nodes in the network.

        Parameters:
        source (str): The source node identifier.
        target (str): The target node identifier.
        relationship_type (str): The type of relationship between the source and target nodes.

        Returns:
        bool: True if the relationship is added successfully.
        """
        self.graph.add_edge(source, target, relationship_type=relationship_type)
        logging.info(f"Added relationship from {source} to {target} of type {relationship_type}")
        return True

    def visualize(self) -> bool:
        """
        Visualizes the network using matplotlib.

        Returns:
        bool: True if the network is visualized successfully.
        """
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold")
        edge_labels = nx.get_edge_attributes(self.graph, 'relationship_type')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        plt.show()
        logging.info("Visualized the network")
        return True

def main():
    """
    Main function to create and manipulate the ATLAS Network.
    """
    atlas_network = ATLASNetwork()

    # Adding entities
    atlas_network.add_entity('Entity1', attributes={'name': 'Entity One'}, patterns=['Pattern1'])
    atlas_network.add_entity('Entity2', attributes={'name': 'Entity Two'}, patterns=['Pattern2'])

    # Adding patterns
    atlas_network.add_pattern('Pattern1', qkit=['iQuery1'], parents=[], children=['Pattern2'])
    atlas_network.add_pattern('Pattern2', qkit=['iQuery2'], parents=['Pattern1'], children=[])

    # Adding iQueries
    atlas_network.add_iquery('iQuery1', ref_id='RID1', prompts=['Prompt1'])
    atlas_network.add_iquery('iQuery2', ref_id='RID2', prompts=['Prompt2'])

    # Adding attributes
    atlas_network.add_attribute('Attribute1', ref_id='RID1', attributes={'key1': 'value1'}, patterns=['Pattern1'])
    atlas_network.add_attribute('Attribute2', ref_id='RID2', attributes={'key2': 'value2'}, patterns=['Pattern2'])

    # Adding prompt interfaces
    atlas_network.add_prompt_interface('Prompt1', function=lambda x: x)
    atlas_network.add_prompt_interface('Prompt2', function=lambda x: x)

    # Adding relationships
    atlas_network.add_relationship('Entity1', 'Pattern1', 'conforms_to')
    atlas_network.add_relationship('Entity2', 'Pattern2', 'conforms_to')
    atlas_network.add_relationship('Pattern1', 'Pattern2', 'parent_of')
    atlas_network.add_relationship('iQuery1', 'Prompt1', 'uses')
    atlas_network.add_relationship('iQuery2', 'Prompt2', 'uses')

    # Visualize the network
    atlas_network.visualize()

if __name__ == "__main__":
    main()
