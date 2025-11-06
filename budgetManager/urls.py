from django.urls import path
from . import views

app_name = "budgetManager"

urlpatterns = [
    path("index/", views.budgetManager, name="budgetManager"),
    path("monthlyBudget/", views.monthlyBudget, name="monthlyBudget"),
    path("add_item_modal/", views.addItemModal, name="add_item_modal"),
    path("save_monthly_data/", views.save_monthly_data, name="save_monthly_data"),
    path("debt-manager/", views.debtManager, name="debtManager"),
    path("loan-manager/", views.loanManager, name="loanManager"),
    path('debts/new/', views.debt_form, name='debt_create'),
    path('loans/new/', views.loan_form, name='loan_create'),


    path("monthlyBudgetSheet/", views.monthlyBudgetSheet, name="monthlyBudgetSheet"),
    path("api/save_cell/", views.save_cell, name="save_cell"),
    path("api/load_sheet/<int:sheet_id>/", views.load_sheet, name="load_sheet"),
    path("show_formula/", views.show_formula, name="show_formula"),


]
