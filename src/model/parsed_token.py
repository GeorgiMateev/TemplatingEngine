from dataclasses import dataclass
from enum import Enum
from typing import List


class ScopeAction(Enum):
    OPEN = 1
    CLOSE = 2
    NONE = 3


@dataclass
class ParsedToken:
    is_valid: bool
    function_name: str
    arguments: List[str]
    scope: ScopeAction
    raw_text: List[str]
