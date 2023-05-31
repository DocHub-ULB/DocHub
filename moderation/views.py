from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from moderation.forms import RepresentativeRequestForm
from moderation.models import RepresentativeRequest


@login_required
def moderation_home(request):
    return render(
        request,
        "moderation/home.html",
    )


@login_required
def representative_request(request):
    if RepresentativeRequest.objects.filter(
        user=request.user, processed=False
    ).exists():
        return render(
            request,
            "moderation/representative_request_received.html",
        )

    if request.method == "POST":
        form = RepresentativeRequestForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.instance.user = request.user
            form.instance.save()
            return redirect("representative_request")
    else:
        form = RepresentativeRequestForm()
    return render(request, "moderation/representative_request.html", {"form": form})
