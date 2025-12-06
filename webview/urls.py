from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('stock-analyser/', views.stockAnalyser, name='stockAnalyser'),

    path('scanner/', views.stockScanner, name="stockScanner"),
    path('scanner/api/', views.scannerAPI, name="scannerAPI"),
    path('stock/api/ai/', views.groq_analysis, name="groq_analysis"),

    path('stock/analysis/ai/<str:stockName>', views.analysisWithAi, name="analysisWithAi"),
    path('fetch-multibaggers/', views.fetch_multibaggers_view, name='fetch_multibaggers'),


]
