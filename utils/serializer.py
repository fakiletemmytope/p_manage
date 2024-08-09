from typing import List, Any, Dict
from decimal import Decimal

async def serialize(lists: List[str], obj: Any) -> Dict[str, Any]:
    """
    Serialize an object's attributes to a dictionary, converting Decimal values to float.

    :param lists: A list of attribute names to serialize from the object.
    :param obj: The object instance from which to extract attributes.
    :return: A dictionary with attribute names and their serialized values.
    """
    serialized = {}
    for l in lists:            
            value = getattr(obj, l, None)  # Fetch the attribute value from the object
            if isinstance(value, Decimal):  # Check if the value is of type Decimal
                value = float(value)  # Convert Decimal to float
            serialized[l] = value    
    return serialized
