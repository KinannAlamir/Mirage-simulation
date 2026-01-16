import json
import dataclasses
from typing import Any, Dict
from .models import PeriodState

def serialize_simulation_state(session_state_dict: Dict[str, Any]) -> str:
    """
    Serializes relevant parts of the session state to a JSON string.
    Specifically handles the PeriodState object and primitive types.
    """
    export_data = {}
    
    for key, value in session_state_dict.items():
        # Handle the main PeriodState object
        if key == "state" and isinstance(value, PeriodState):
            state_dict = dataclasses.asdict(value)
            state_dict["__type__"] = "PeriodState"
            export_data[key] = state_dict
        
        # Handle standard Streamlit widget keys (inputs usually strings, ints, floats, bools)
        # We exclude keys that might be internal or non-serializable
        elif isinstance(value, (str, int, float, bool, type(None))):
            export_data[key] = value
        elif isinstance(value, (list, dict)):
             # Basic check for serializable containers
             try:
                 json.dumps(value)
                 export_data[key] = value
             except (TypeError, OverflowError):
                 pass
                 
    return json.dumps(export_data, indent=2)

def deserialize_simulation_state(json_str: str) -> Dict[str, Any]:
    """
    Deserializes the JSON string back into a dictionary.
    Reconstructs PeriodState objects.
    """
    try:
        data = json.loads(json_str)
        
        # Reconstruct PeriodState if present
        if "state" in data and isinstance(data["state"], dict):
            state_data = data["state"]
            if state_data.get("__type__") == "PeriodState":
                del state_data["__type__"]
                # Filter out any keys in JSON that don't match the dataclass (forward compatibility)
                field_names = {f.name for f in dataclasses.fields(PeriodState)}
                filtered_state_data = {k: v for k, v in state_data.items() if k in field_names}
                data["state"] = PeriodState(**filtered_state_data)
                
        return data
    except json.JSONDecodeError:
        return {}
    except Exception as e:
        print(f"Error deserializing state: {e}")
        return {}
