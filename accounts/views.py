from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from transactions.models import Category

def register(request):
    if request.user.is_authenticated: return redirect("dashboard")
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            _seed()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect("dashboard")
    return render(request, "accounts/register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated: return redirect("dashboard")
    form = AuthenticationForm()
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(request.GET.get("next", "dashboard"))
        messages.error(request, "Invalid credentials.")
    return render(request, "accounts/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

def _seed():
    defaults = [
        ("Salary","income","💼","#10b981"),("Freelance","income","💻","#06b6d4"),
        ("Investment","income","📈","#8b5cf6"),("Other Income","income","💰","#f59e0b"),
        ("Food & Dining","expense","🍽️","#ef4444"),("Transport","expense","🚗","#f97316"),
        ("Shopping","expense","🛍️","#ec4899"),("Utilities","expense","💡","#eab308"),
        ("Healthcare","expense","🏥","#14b8a6"),("Entertainment","expense","🎬","#6366f1"),
        ("Education","expense","📚","#0ea5e9"),("Rent","expense","🏠","#84cc16"),
    ]
    for name,ctype,icon,color in defaults:
        Category.objects.get_or_create(name=name, category_type=ctype,
            defaults={"icon":icon,"color":color,"is_default":True})
