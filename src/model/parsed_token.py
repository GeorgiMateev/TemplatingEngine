from dataclasses import dataclass
from typing import List, Literal


@dataclass
class ParsedToken:
    is_valid: bool
    function_name: str
    arguments: List[str]
    scope: Literal["open", "close", "none"]
    raw_text: str
