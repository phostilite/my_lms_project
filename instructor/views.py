from django.shortcuts import render

def dashboard(request):
    return render(request, 'instructor/dashboard.html')