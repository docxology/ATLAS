import networkx as nx
import matplotlib.pyplot as plt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ATLASNetwork:
    def __init__(self):
        self.graph = nx.DiGraph()
        logging.info("Initialized ATLAS Network")

    def add_entity(self, entity_id, attributes=None, patterns=None):
        self.graph.add_node(entity_id, attributes=attributes or {}, patterns=patterns or [])
        logging.info(f"Added entity: {entity_id} with attributes: {attributes} and patterns: {patterns}")

    def add_pattern(self, pattern_id, qkit=None, parents=None, children=None):
        self.graph.add_node(pattern_id, qkit=qkit or [], parents=parents or [], children=children or [])
        logging.info(f"Added pattern: {pattern_id} with qkit: {qkit}, parents: {parents}, children: {children}")

    def add_iquery(self, iquery_id, ref_id, prompts):
        self.graph.add_node(iquery_id, ref_id=ref_id, prompts=prompts)
        logging.info(f"Added iQuery: {iquery_id} with ref_id: {ref_id} and prompts: {prompts}")

    def add_attribute(self, attribute_id, ref_id, attributes=None, patterns=None):
        self.graph.add_node(attribute_id, ref_id=ref_id, attributes=attributes or {}, patterns=patterns or [])
        logging.info(f"Added attribute: {attribute_id} with ref_id: {ref_id}, attributes: {attributes}, patterns: {patterns}")

    def add_prompt_interface(self, pi_id, function):
        self.graph.add_node(pi_id, function=function)
        logging.info(f"Added prompt interface: {pi_id}")

    def add_relationship(self, source, target, relationship_type):
        self.graph.add_edge(source, target, relationship_type=relationship_type)
        logging.info(f"Added relationship from {source} to {target} of type {relationship_type}")

    def visualize(self):
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold")
        edge_labels = nx.get_edge_attributes(self.graph, 'relationship_type')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        plt.show()
        logging.info("Visualized the network")

def main():
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
