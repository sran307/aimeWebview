from django.db import models
from django.conf import settings

class Sheet(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.owner})"


class Cell(models.Model):
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE, related_name="cells")
    row = models.PositiveIntegerField()
    col = models.PositiveIntegerField()
    value = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("sheet", "row", "col")
        indexes = [models.Index(fields=["sheet", "row", "col"])]

    def __str__(self):
        return f"Cell {self.row},{self.col} @ {self.sheet_id}"


class CellChange(models.Model):
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE, related_name="changes")
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField()

    class Meta:
        ordering = ("-changed_at",)
