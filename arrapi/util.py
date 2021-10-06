from datetime import datetime
from typing import Any, List, Optional

from arrapi.exceptions import Invalid


def parse(data: Any, attribute: Optional[str] = None, value_type: str = "str",
          date_format: str = "%Y-%m-%dT%H:%M:%S", default_is_none: bool = False):
    """ Validate the value given from the options given.

        Parameters:
            data (Any): data to check
            attribute (Optional[str]): check data for this attribute.
            value_type (str): Type that the value is.
            date_format (str): Format for Date parsing.
            default_is_none (bool): Makes default None.

        Returns:
            Any: Parsed Value
    """
    if default_is_none is False and value_type in ["int", "float"]:
        default = 0
    elif default_is_none is False and value_type.endswith("List"):
        default = []
    else:
        default = None

    if attribute is None:
        value = data
    else:
        if attribute not in data:
            return default
        value = data[attribute]
    if value is None:
        return default
    elif value_type == "int":
        return int(value)
    elif value_type == "float":
        return float(value)
    elif value_type == "bool":
        if isinstance(value, bool):
            return value
        elif str(value).lower() in ["t", "true"]:
            return True
        elif str(value).lower() in ["f", "false"]:
            return False
        else:
            return default
    elif value_type.endswith("List"):
        return [parse(v, value_type=value_type[:-4]) for v in value]
    elif value_type == "date":
        return datetime.strptime(value[:-1].split(".")[0], date_format)
    else:
        return str(value)


def validate_options(title: str, value: str, options: List[str]):
    """ Validate the value given from the options given.

        Parameters:
            title (str): Name of what is being validated.
            value (str): Value to check options for.
            options (List[str]): List of options to check the value against.

        Returns:
            str: Valid Value

        Raises:
            :class:`~arrapi.exceptions.Invalid`: If the value isn't in the options.
    """
    if value in options:
        return value
    raise Invalid(f"Invalid {title}: '{value}' Options: {options}")
