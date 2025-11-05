from django.contrib import admin
from .models import Sheet, Cell, CellChange

@admin.register(Sheet)
class SheetAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")

@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ("id", "sheet", "row", "col", "value", "version", "updated_at")
    list_filter = ("sheet",)

@admin.register(CellChange)
class CellChangeAdmin(admin.ModelAdmin):
    list_display = ("id", "cell", "version", "changed_at")
    list_filter = ("changed_at",)
