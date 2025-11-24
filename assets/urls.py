from django.urls import path
from . import views

app_name = "assets"

urlpatterns = [
    path("index/", views.assets, name="assets"),
    path("index/<str:transType>/", views.indexManager, name="indexManager"),
    path("transactions/<str:transType>/", views.transManager, name="transManager"),

    path("save/", views.saveTrans, name="saveTrans"),
    path("show/stocks/", views.showStocks, name="showStocks"),
    path("show/mf/", views.showMfs, name="showMfs"),

    path("process/<str:transType>/<str:processType>/", views.process, name="process"),
    path("clear/data", views.clearData, name="clearData"),

    path('divident/', views.dividentManager, name="dividentManager"),
    path("add-dividend/", views.addDividend, name="addDividend"),


]