"""types

Custom types for validation
"""

from pydantic import conint

# unsigned integers
uint1 = conint(ge=0, lt=2)
uint2 = conint(ge=0, lt=4)
uint4 = conint(ge=0, lt=16)
uint7 = conint(ge=0, lt=128)
uint8 = conint(ge=0, lt=256)
uint16 = conint(ge=0, lt=2**16)
