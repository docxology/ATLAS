from typing import Any, List

@dataclass
class Entity(ABC):
"""
Descriptionr: Objects of the Entity class 
are used to represent and enable common reference to tangible or
abstract objects and patterns of objects in 
physical, digital, or conceptual space. 
"""

    ref_ID: Any 
    prompts: List[Any]
    attributes: Callable[Any, Any]

    def mark_anomaly(self, iQuery_to_mark: Any):
        """
        Mark an iQuery as an anomaly.
        """
        pass 

    def mark_exception(self, iQuery_to_mark: Any):
        """
        TODO: Replace string
        """
        pass

    def call_requests_for_information(self, List[Any]):
        """
        TODO: Replace string
        """
        pass 

    

