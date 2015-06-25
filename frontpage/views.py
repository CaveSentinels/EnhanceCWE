from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import JsonResponse

# Home screen
def index(request):
    return render(request, 'frontpage/index.html')
