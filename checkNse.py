import nsepython
from nsepython import *
print(indiavix())
print("Listing all functions, classes, and attributes in nsepython:\n")
all_attrs = dir(nsepython)

for attr in all_attrs:
    print(attr)

# Optional: filter only functions (ignores classes/variables)
import types

functions = [f for f in all_attrs if isinstance(getattr(nsepython, f), types.FunctionType)]
print("\nAvailable functions in nsepython:\n")
# for f in functions:
#     print(f)
