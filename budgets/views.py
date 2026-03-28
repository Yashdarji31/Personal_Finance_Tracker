from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Budget
from .forms import BudgetForm
import datetime

@login_required
def budget_list(request):
    today = datetime.date.today()
    month = int(request.GET.get("month", today.month))
    year = int(request.GET.get("year", today.year))
    budgets = Budget.objects.filter(user=request.user, month=month, year=year)
    budget_data = [{"budget":b,"spent":b.get_spent(),"remaining":b.get_remaining(),"percentage":b.get_percentage()} for b in budgets]
    return render(request,"budgets/list.html",{"budget_data":budget_data,"month":month,"year":year,"months":range(1,13),"years":range(today.year-2,today.year+2)})

@login_required
def budget_add(request):
    form = BudgetForm(user=request.user)
    if request.method == "POST":
        form = BudgetForm(request.user, request.POST)
        if form.is_valid():
            b = form.save(commit=False); b.user = request.user; b.save()
            messages.success(request,"Budget created!")
            return redirect("budget_list")
    return render(request,"budgets/form.html",{"form":form,"action":"Create"})

@login_required
def budget_edit(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    form = BudgetForm(user=request.user, instance=budget)
    if request.method == "POST":
        form = BudgetForm(request.user, request.POST, instance=budget)
        if form.is_valid():
            form.save(); messages.success(request,"Updated!")
            return redirect("budget_list")
    return render(request,"budgets/form.html",{"form":form,"action":"Edit"})

@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == "POST":
        budget.delete(); messages.success(request,"Deleted.")
        return redirect("budget_list")
    return render(request,"budgets/confirm_delete.html",{"object":budget})
