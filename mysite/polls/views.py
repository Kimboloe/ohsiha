from django.http import HttpResponse

def index(request):
    return HttpResponse("hello, you're in the polls index!")
