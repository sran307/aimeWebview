import json
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction
from django.contrib.auth.decorators import login_required

from .models import Sheet, Cell, CellChange

# @login_required
def budgetManager(request):
    # simple page showing an editable grid
    sheet = get_object_or_404(Sheet, id=1)
    # pass basic metadata (you can change grid size as needed)
    context = {"sheet": sheet, "rows": range(1, 21), "cols": range(1, 11)}
    return render(request, "budget/sheet.html", context)


# @login_required
@require_GET
def load_sheet(request, sheet_id):
    sheet = get_object_or_404(Sheet, id=sheet_id)
    cells = Cell.objects.filter(sheet=sheet)
    data = {}
    for c in cells:
        data[f"{c.row}:{c.col}"] = {"value": c.value, "version": c.version}
    return JsonResponse({"status": "ok", "cells": data})


# @login_required
@require_POST
def save_cell(request):
    """
    Expect JSON body:
    {
      "sheet_id": 1,
      "row": 3,
      "col": 4,
      "value": "Hello",
      "version": 2   # optional; client version
    }
    """
    try:
        payload = json.loads(request.body.decode("utf-8"))
        sheet_id = int(payload.get("sheet_id"))
        row = int(payload.get("row"))
        col = int(payload.get("col"))
        new_value = payload.get("value", "")
        client_version = int(payload.get("version", 0))
    except Exception:
        return HttpResponseBadRequest("invalid request")

    sheet = get_object_or_404(Sheet, id=sheet_id)

    with transaction.atomic():
        # lock the cell row (if exists) to avoid race; get_or_create in the same transaction
        cell, created = Cell.objects.select_for_update().get_or_create(
            sheet=sheet, row=row, col=col,
            defaults={"value": new_value, "version": 1},
        )

        if not created:
            # conflict detection (optimistic)
            if client_version and client_version != cell.version:
                # let client know there's a version mismatch (409 semantics)
                return JsonResponse({
                    "status": "conflict",
                    "server_value": cell.value,
                    "server_version": cell.version,
                }, status=409)

            # record change
            old = cell.value
            if old != new_value:
                cell.value = new_value
                cell.version += 1
                cell.save(update_fields=["value", "version", "updated_at"])
                CellChange.objects.create(
                    cell=cell, old_value=old, new_value=new_value,
                    changed_by=request.user, version=cell.version
                )

    return JsonResponse({"status": "ok", "version": cell.version})

