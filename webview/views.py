from django.shortcuts import render

def home(request):
    return render(request, 'main/home.html')

def stockAnalyser(request):
    return render(request, 'stock/index.html')

def budgetManager(request):
    return render(request, 'budget/index.html')