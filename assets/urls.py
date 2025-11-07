from django.urls import path
from . import views

app_name = "assets"

urlpatterns = [
    path("index/", views.assets, name="assets"),
    path("mtft/", views.mtftManager, name="mtftManager"),
    path("mtft/transactions/", views.mtftTransactions, name="mtftTransactions"),
    path("mtft/save/", views.saveMtftTrans, name="saveMtftTrans")
]