from django.shortcuts import render

# TODO: is this still required ?


def error400(request, exception=None):
    return render(request, "error/400.html", status=400)


def error403(request, exception=None):
    return render(request, "error/403.html", status=403)


def error404(request, exception=None):
    return render(request, "error/404.html", status=404)


def error500(request, exception=None):
    return render(request, "error/500.html", status=500)
