from abc import ABCMeta, abstractclassmethod, abstractmethod
import re
from typing import List

class CommandComponent(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def regex_generater(self):
        pass

class Normal(CommandComponent):
    index: int
    match: str

    def __init__(self, match_string, index):
        self.match = match_string
        self.index = index

    def regex_generater(self):
        return re.escape(self.match)

    def __repr__(self):
        return f"<Normal match='{self.match}'>"

class Require(CommandComponent):
    name: str
    flags: List[str]

    def __init__(self, name, index, flags=[]):
        self.name = name
        self.flags = flags
        self.index = index

    def regex_generater(self):
        return f"(?P<{self.name}>((?!\ ).)*)"

    def __repr__(self):
        return f"<Require name='{self.name}' flags={self.flags}>"

class Optional(CommandComponent):
    index: str
    name: str
    flags: List[str]

    def __init__(self, name, index, flags=[]):
        self.name = name
        self.flags = flags
        self.index = index

    def regex_generater(self):
        return f"(?P<{self.name}>((?!\ ).)*)?"

    def __repr__(self):
        return f"<Optional name='{self.name}' flags={self.flags}>"