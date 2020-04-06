from typing import List

class StatsTransferError(Exception):
    pass

class ValueCheckError(Exception):
    pass

class FlagConflictError(Exception):
    pass

class ArgumentParseError(Exception):
    param_name: str
    flags: List[str]
    should_be: str

    def __init__(self, msg, param_name, flags, should_be):
        super().__init__(f"{msg}: {param_name}(with {flags}) should be {should_be}.")
        self.param_name = param_name
        self.flags = flags
        self.should_be = should_be