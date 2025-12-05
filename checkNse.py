import nsepython
from nsepython import *
# print(nse_index())
df=nse_index()
nifty_row = df[df["indexName"] == "NIFTY 50"].iloc[0]
print(nifty_row)
# print("Listing all functions, classes, and attributes in nsepython:\n")
# all_attrs = dir(nsepython)

# for attr in all_attrs:
#     print(attr)

# Optional: filter only functions (ignores classes/variables)
# import types

# functions = [f for f in all_attrs if isinstance(getattr(nsepython, f), types.FunctionType)]
# print("\nAvailable functions in nsepython:\n")
# for f in functions:
#     print(f)
