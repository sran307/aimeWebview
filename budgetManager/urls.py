from django.urls import path
from . import views

app_name = "budgetManager"

urlpatterns = [
    path("index/", views.budgetManager, name="budgetManager"),
    path("monthlyBudget/", views.monthlyBudgetSheet, name="monthlyBudgetSheet"),
    path("api/save_cell/", views.save_cell, name="save_cell"),
    path("api/load_sheet/<int:sheet_id>/", views.load_sheet, name="load_sheet"),
    path("show_formula/", views.show_formula, name="show_formula"),
]
