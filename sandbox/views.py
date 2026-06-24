from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def sandbox_view(request):
    return render(request, "sandbox/sandbox.html")