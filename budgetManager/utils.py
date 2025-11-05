# import re
# from .models import Cell

# def evaluate_formula(sheet, formula):
#     """
#     Supports simple formulas like =A1+A2 (currently only addition).
#     """
#     if not formula.startswith("="):
#         return formula

#     expression = formula[1:]  # remove '='
#     parts = re.split(r'([+\-*/])', expression)  # split by operator, keep it
#     result = 0
#     operator = '+'

#     for part in parts:
#         part = part.strip()
#         if part == "":
#             continue

#         if part in "+-*/":
#             operator = part
#             continue

#         # Convert A1 → (row=1, col=1)
#         match = re.match(r'([A-Z]+)([0-9]+)', part)
        
#         if match:
#             col_letters, row = match.groups()
#             row = int(row)
#             col = sum([(ord(c) - 64) * (26 ** i) for i, c in enumerate(col_letters[::-1])])
#             try:
#                 ref_cell = sheet.cells.get(row=row, col=col)
#                 try:
#                     value = float(ref_cell.value)
#                 except (TypeError, ValueError):
#                     value = 0
#             except Cell.DoesNotExist:
#                 value = 0
#         else:
#             # It's a number
#             try:
#                 value = float(part)
#             except ValueError:
#                 value = 0

#         if operator == '+':
#             result += value
#         elif operator == '-':
#             result -= value
#         elif operator == '*':
#             result *= value
#         elif operator == '/':
#             result = result / value if value != 0 else 0

#     return str(result)

import re
from .models import Cell

def col_to_index(col_letters):
    """Convert column letters (A, B, AA) to 1-based index."""
    return sum((ord(c.upper()) - 64) * (26 ** i) for i, c in enumerate(col_letters[::-1]))

def evaluate_formula(sheet, formula):
    """
    Supports formulas like:
    =A1+A2
    =SUM(B1:B2)
    """
    if not formula.startswith("="):
        return formula

    expression = formula[1:].strip()  # remove '='

    # Handle SUM() function first
    sum_match = re.match(r'SUM\(\s*([A-Z]+)([0-9]+):([A-Z]+)([0-9]+)\s*\)', expression, re.IGNORECASE)
    if sum_match:
        start_col, start_row, end_col, end_row = sum_match.groups()
        start_col = col_to_index(start_col)
        end_col = col_to_index(end_col)
        start_row = int(start_row)
        end_row = int(end_row)

        total = 0
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                ref_cell = sheet.cells.filter(row=row, col=col).first()
                try:
                    value = float(ref_cell.value) if ref_cell else 0
                except (TypeError, ValueError):
                    value = 0
                total += value
        return str(total)

    # fallback to simple arithmetic like before
    parts = re.split(r'([+\-*/])', expression)  # split by operator, keep operators
    result = 0
    operator = '+'

    for part in parts:
        part = part.strip()
        if part == "":
            continue

        if part in "+-*/":
            operator = part
            continue

        # Convert A1 → (row, col)
        match = re.match(r'([A-Z]+)([0-9]+)', part, re.IGNORECASE)
        if match:
            col_letters, row = match.groups()
            row = int(row)
            col = col_to_index(col_letters)

            ref_cell = sheet.cells.filter(row=row, col=col).first()
            try:
                value = float(ref_cell.value) if ref_cell else 0
            except (TypeError, ValueError):
                value = 0
        else:
            # It's a number
            try:
                value = float(part)
            except ValueError:
                value = 0

        if operator == '+':
            result += value
        elif operator == '-':
            result -= value
        elif operator == '*':
            result *= value
        elif operator == '/':
            result = result / value if value != 0 else 0

    return str(result)
