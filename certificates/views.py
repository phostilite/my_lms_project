from django.shortcuts import render

def certificates(request):
    return render(request, 'learner/certificates.html')
