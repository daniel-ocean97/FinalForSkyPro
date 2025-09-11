from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import EmailAuthenticationForm, UserProfileForm, UserRegisterForm


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("restaurant:restaurant_detail")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            next_url = request.GET.get("next") or reverse(
                "restaurant:restaurant_detail"
            )
            return redirect(next_url)
    else:
        form = EmailAuthenticationForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    auth_logout(request)
    return redirect("restaurant:about")


@login_required
def profile(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:profile")
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, "users/profile.html", {"form": form})
