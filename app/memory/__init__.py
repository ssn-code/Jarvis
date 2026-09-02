from app.memory.short_term import ShortTermMemory
from app.memory.long_term import LongTermMemory, long_term_mem

# Shared short-term memory instance using the default database context
short_term_mem = ShortTermMemory()

__all__ = [
    "ShortTermMemory",
    "LongTermMemory",
    "short_term_mem",
    "long_term_mem",
]
