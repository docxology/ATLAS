from ATLAS_utils import ATLASNetwork  # Ensure this import is correct

def terminal_experience():
    """
    Creates a terminal-like experience for the user to interact with the ATLAS Network.

    The user can add entities, patterns, iQueries, attributes, prompt interfaces, and relationships.
    The user can also visualize the network.

    Returns:
    None
    """
    # Ensure ATLASNetwork is defined
    try:
        atlas_network = ATLASNetwork()
    except NameError:
        print("Error: ATLASNetwork is not defined. Please ensure it is imported or defined correctly.")
        return

    print("Welcome to the ATLAS Network Terminal Experience!")
    print("You can interact with the network by typing commands.")
    print("Type 'help' to see a list of commands.")
    print("Type 'exit' to quit the terminal experience.")

    while True:
        command = input("Enter command: ").strip().lower()

        if command == 'exit':
            print("Exiting the terminal experience. Goodbye!")
            break
        elif command == 'help':
            print("Available commands:")
            print("  add_entity <entity_id> <attributes> <patterns>")
            print("  add_pattern <pattern_id> <qkit> <parents> <children>")
            print("  add_iquery <iquery_id> <ref_id> <prompts>")
            print("  add_attribute <attribute_id> <ref_id> <attributes> <patterns>")
            print("  add_prompt_interface <pi_id> <function>")
            print("  add_relationship <source> <target> <relationship_type>")
            print("  visualize")
            print("  exit")
        elif command.startswith('add_entity'):
            parts = command.split()
            entity_id = parts[1]
            attributes = eval(parts[2]) if len(parts) > 2 else {}
            patterns = eval(parts[3]) if len(parts) > 3 else []
            atlas_network.add_entity(entity_id, attributes, patterns)
        elif command.startswith('add_pattern'):
            parts = command.split()
            pattern_id = parts[1]
            qkit = eval(parts[2]) if len(parts) > 2 else []
            parents = eval(parts[3]) if len(parts) > 3 else []
            children = eval(parts[4]) if len(parts) > 4 else []
            atlas_network.add_pattern(pattern_id, qkit, parents, children)
        elif command.startswith('add_iquery'):
            parts = command.split()
            iquery_id = parts[1]
            ref_id = parts[2]
            prompts = eval(parts[3]) if len(parts) > 3 else []
            atlas_network.add_iquery(iquery_id, ref_id, prompts)
        elif command.startswith('add_attribute'):
            parts = command.split()
            attribute_id = parts[1]
            ref_id = parts[2]
            attributes = eval(parts[3]) if len(parts) > 3 else {}
            patterns = eval(parts[4]) if len(parts) > 4 else []
            atlas_network.add_attribute(attribute_id, ref_id, attributes, patterns)
        elif command.startswith('add_prompt_interface'):
            parts = command.split()
            pi_id = parts[1]
            function = eval(parts[2]) if len(parts) > 2 else None
            atlas_network.add_prompt_interface(pi_id, function)
        elif command.startswith('add_relationship'):
            parts = command.split()
            source = parts[1]
            target = parts[2]
            relationship_type = parts[3]
            atlas_network.add_relationship(source, target, relationship_type)
        elif command == 'visualize':
            atlas_network.visualize()
        else:
            print("Unknown command. Type 'help' to see a list of commands.")

# Call the function to start the terminal experience
if __name__ == "__main__":
    terminal_experience()