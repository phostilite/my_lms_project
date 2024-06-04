from django.shortcuts import render

def course_catalog(request):
    return render(request, 'learner/course_catalog.html')
