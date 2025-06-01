# ATLAS Specification

## Introduction
The ATLAS system, evolving since the late 1990s, stands as a dynamic and comprehensive knowledge management tool that addresses the complexities of modern information supply chains. The antecedent to ATLAS was the Atlas of Risk, an informal assemblage of various risks associated with digital interactions. This document provides an initial specification for digital prototypes and paper-and-pencil implementations of a matured ATLAS architecture, integrating pattern language approaches with question-oriented procedures to manage and interpret meaning and context.

## Purpose
ATLAS, as a Knowledge Management System, is intended to:
- Enable the development and documentation of local and community information standards.
- Facilitate rapid expansion and networking of knowledge.
- Provide a basis for sharing common reference to objects (data, artifacts, abstractions) within, between, and among communities.
- Reframe intercoder reliability issues as useful information.
- Restructure existing and developing knowledge bases to:
  - Enable interoperability and exchange.
  - Reveal knowledge gaps by default.
  - Support synthetic intelligence by providing a foundation for stable communication among human and automated agents.

## Scope
This document addresses the core components of the ATLAS system, a question-oriented approach for structuring, expanding, and establishing relationships within a knowledge base, and for dynamic typing of objects using pattern language approaches. The components, properties, and methods included would allow for functionality of the core mechanisms of the system both in digital prototype and paper-and-pencil implementations.

## System Definition

### Entity
Entities are the fundamental objects within the ATLAS system. They can represent any identifiable object and are assigned attributes and patterns. Formally, an Entity \( E \) is defined as a tuple \( E = (A, P) \) where:
- **Attributes \( A \)**: A set of key-value pairs \( \{(k_1, v_1), (k_2, v_2), \ldots, (k_n, v_n)\} \) allowing for flexible assignment and retrieval.
- **Patterns \( P \)**: A set of patterns \( \{p_1, p_2, \ldots, p_m\} \) that the entity conforms to.

Methods associated with an Entity include:
- **Mark Anomaly**: Marks the Entity as an anomaly to a specific iQuery.
- **Mark Exception**: Marks the Entity as an exception in relation to a specific iQuery.
- **CallRFIs**: Calls open requests for information generated from Entity Attributes with no values and unresolved iQueries.

### Pattern
Patterns are a subclass of the Entity class, representing abstract phenomena and objects which other Entity objects might instantiate or exemplify. Formally, a Pattern \( P \) is defined as a tuple \( P = (Q, \text{Parents}, \text{Children}) \) where:
- **QKit \( Q \)**: A set of references to iQuery objects \( \{q_1, q_2, \ldots, q_k\} \) representing the set of requests for information expected to be made and resolved if an object is assigned this pattern.
- **Parents**: A set of Patterns \( \{P_1, P_2, \ldots, P_p\} \) indicating that any Entity assigned to this Pattern should also be assigned to each pattern in the Parents set.
- **Children**: A set of Pattern objects \( \{C_1, C_2, \ldots, C_c\} \) to which this Pattern object is a Parent.

### iQuery
The iQuery class, short for itemized query, manages and facilitates the resolution of requests for information and leverages the latent information in such requests. Formally, an iQuery \( I \) is defined as a tuple \( I = (\text{RefID}, \text{Prompts}) \) where:
- **RefID**: A pointer to a RID used for managing merge, import, and export operations with other ATLAS entities.
- **Prompts**: A set of references to Prompt Interfaces \( \{p_1, p_2, \ldots, p_r\} \) used to request, receive, and retrieve information and package them into Data Types receivable by appropriate ATLAS attributes.

### Attribute
Attributes within the ATLAS system are extensions of the Entity class, carrying Reference IDs and their own Attributes and Patterns. Formally, an Attribute \( A \) is defined as a tuple \( A = (\text{RefID}, \text{Attributes}, \text{Patterns}) \) where:
- **RefID**: A unique identifier for the attribute.
- **Attributes**: A set of key-value pairs \( \{(k_1, v_1), (k_2, v_2), \ldots, (k_n, v_n)\} \).
- **Patterns**: A set of patterns \( \{p_1, p_2, \ldots, p_m\} \).

Attributes can be shared between systems and linked via common Reference IDs despite differing ontology or split despite overlaps in ontology.

### Prompt Interface
Prompt Interfaces are used to call and transform data between systems, enabling interoperability of data even where schemas are not agreed upon. Formally, a Prompt Interface \( PI \) is defined as a function \( PI: D \rightarrow D' \) where \( D \) and \( D' \) are data sets from different systems. They facilitate structured data exchange and can be used to request Entity objects of particular types from an existing ATLAS.

### Information Exchange Environments (IXE) and Verified Information Exchange Environments (VIE)
IXEs are ATLAS instances that support the exchange of iQuery objects. Formally, an IXE is a category \( \mathcal{C} \) where objects are iQuery instances and morphisms are transformations between these instances. VIEs are IXEs that implement defined quality assurance standards and procedures, providing measurable functional reliability and enforcement of standards. VIEs offer additional verification features, enhancing reliability and value for system users.

## Core Mechanisms and Implications

### Dynamic Typing and Management of Exponential Expansion
ATLAS instances facilitate rapid expansion of a knowledge base through dynamic Pattern assignment and structured, itemized queries (iQuery objects). The system is driven by Entity reference and structured queries, networking existing Entity objects and managing exponential expansion through careful structure and networking of components. Formally, this can be represented as a directed graph \( G = (V, E) \) where vertices \( V \) are Entities and edges \( E \) are relationships defined by iQueries.

### Data Interoperability without Shared Standards
Attributes within the ATLAS system can be shared between systems and linked via common Reference IDs, allowing for interoperability of data even where schemas are not agreed upon. Pattern assignment within Entity objects helps reveal duplicates or opportunities for transformation, supporting comparability of analysis without requiring new Attributes. Formally, this can be represented as a mapping \( f: A \rightarrow A' \) where \( A \) and \( A' \) are attribute sets from different systems.

### Restructuring and Maintaining Navigability
The ATLAS system ensures that knowledge bases remain navigable and structured through the use of Patterns and iQueries. This involves maintaining a hierarchical structure and ensuring that Entities are appropriately categorized and linked. Formally, this can be represented as a tree \( T = (N, E) \) where nodes \( N \) are Entities and edges \( E \) are hierarchical relationships defined by Patterns and iQueries.

