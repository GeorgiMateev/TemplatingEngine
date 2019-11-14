from dataclasses import dataclass


@dataclass
class FunctionSignature:
    name: str
    arity: int
    has_scope: bool
