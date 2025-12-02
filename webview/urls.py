from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('stock-analyser/', views.stockAnalyser, name='stockAnalyser'),

    path('scanner/', views.stockScanner, name="stockScanner"),
    path('scanner/api/', views.scannerAPI, name="scannerAPI"),

]
