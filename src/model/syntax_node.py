from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class SyntaxNode:
    function_name: str
    arguments: List
    parent: SyntaxNode
    body: List[SyntaxNode] = field(default_factory=list)
