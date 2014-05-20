from django.shortcuts import render

def error400(request):
    return render(request, "error/400.html")
def error403(request):
    return render(request, "error/403.html")
def error404(request):
    return render(request, "error/404.html")
def error500(request):
    return render(request, "error/500.html")
