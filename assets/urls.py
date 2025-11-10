from django.urls import path
from . import views

app_name = "assets"

urlpatterns = [
    path("index/", views.assets, name="assets"),
    path("mtft/", views.mtftManager, name="mtftManager"),
    path("mtft/transactions/", views.mtftTransactions, name="mtftTransactions"),
    path("save/", views.saveTrans, name="saveTrans"),

    path("swing/", views.swingManager, name="swingManager"),
    path("swing/transactions/", views.swingTransactions, name="swingTransactions"),

    path("intra/", views.intraManager, name="intraManager"),
    path("intra/transactions/", views.intraTransactions, name="intraTransactions"),

    path("long/", views.longManager, name="longManager"),
    path("long/transactions/", views.longTransactions, name="longTransactions"),

    path("option/", views.longManager, name="optionManager"),
    path("option/transactions/", views.longTransactions, name="optionTransactions"),

    path("show/stocks/", views.showStocks, name="showStocks"),

    path("mf/", views.mfManager, name="mfManager"),
    path("mf/transactions/", views.mfTransactions, name="mfTransactions"),

    path("show/mf/", views.showMfs, name="showMfs"),

    path("process/<str:transType>/<str:processType>/", views.process, name="process")


]