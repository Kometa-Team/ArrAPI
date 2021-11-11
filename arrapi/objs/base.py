from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Union, Any


class BaseObj(ABC):
    """ Base Class for Arr Objects.

        Attributes:
            id (int): ID of the Object.
    """

    def __init__(self, arr, data):
        self._loading = True
        self._arr = arr
        self._raw = arr._raw
        self._partial = False
        self._name = None
        self._load(data)

    @abstractmethod
    def _load(self, data):
        self._data = data
        self._loading = True
        self.id = None

    def _finish(self, name):
        self._name = name
        self._loading = False

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"[{self.id}:{self._name}]" if self.id is not None else f"[{self._name}]"

    def __eq__(self, other):
        if type(self) is type(other):
            if self.id is None and other.id is None:
                return self._name == other._name
            elif self.id is not None and other.id is not None:
                return self.id == other.id
            else:
                return False
        elif isinstance(other, int) and self.id is not None:
            return self.id == other
        else:
            return str(self._name) == str(other)

    def __getattribute__(self, item):
        value = super().__getattribute__(item)
        if item.startswith("_") or self._loading or not self._partial or value is not None:
            return value
        self._load(None)
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key.startswith("_") or self._loading:
            super().__setattr__(key, value)
        else:
            raise AttributeError("Attributes cannot be edited")

    def __delattr__(self, key):
        raise AttributeError("Attributes cannot be deleted")

    def _parse(self, data: Any = None, attrs: Optional[Union[str, list]] = None, value_type: str = "str",
               default_is_none: bool = False, is_list: bool = False):
        """ Validate the value given from the options given.

            Parameters:
                data (Any): data to check
                attrs (Optional[Union[str, list]]): check data for these attributes.
                value_type (str): Type that the value is.
                default_is_none (bool): Makes default None.
                is_list (bool): Is list of values

            Returns:
                Any: Parsed Value
        """
        if default_is_none is False and value_type in ["int", "float"]:
            default = 0
        elif default_is_none is False and value_type.endswith("List"):
            default = []
        else:
            default = None

        value = self._data if data is None else data
        if attrs:
            if not isinstance(attrs, list):
                attrs = [attrs]
            for attr in attrs:
                if attr in value:
                    value = value[attr]
                else:
                    return default

        if value is None:
            return default
        elif is_list:
            return [self._parse(data=v, value_type=value_type, default_is_none=default_is_none) for v in value]
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
        elif value_type == "date":
            return datetime.strptime(value[:-1].split(".")[0], "%Y-%m-%dT%H:%M:%S")
        elif value_type == "season":
            return arrapi.objs.simple.Season(self._arr, value)
        elif value_type == "intTag":
            return arrapi.objs.reload.Tag(self._arr, {"id": value})
        elif value_type == "intQualityProfile":
            return arrapi.objs.reload.QualityProfile(self._arr, {"id": value})
        elif value_type == "intLanguageProfile":
            return arrapi.objs.reload.LanguageProfile(self._arr, {"id": value})
        else:
            return str(value)

import arrapi.objs.simple
import arrapi.objs.reload
