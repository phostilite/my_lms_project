from django.shortcuts import render

def discussions(request):
    return render(request, 'learner/discussions.html')
