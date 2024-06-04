from django.shortcuts import render

def assignments(request):
    return render(request, 'learner/assignments.html')