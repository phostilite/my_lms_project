from django.shortcuts import render

def dashboard(request):
    return render(request, 'learner/dashboard.html')

def calendar(request):
    return render(request, 'learner/calendar.html')

def my_courses(request):
    return render(request, 'learner/my_courses.html')


def my_certificates(request):
    return render(request, 'learner/my_certificates.html')


def my_badge(request):
    return render(request, 'learner/my_badge.html')

def leaderboard(request):
    return render(request, 'learner/leaderboard.html')