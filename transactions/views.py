from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Transaction, Category
from .forms import TransactionForm

@login_required
def transaction_list(request):
    qs = Transaction.objects.filter(user=request.user)
    t = request.GET.get("type","")
    c = request.GET.get("category","")
    df = request.GET.get("date_from","")
    dt = request.GET.get("date_to","")
    s = request.GET.get("search","")
    if t: qs = qs.filter(transaction_type=t)
    if c: qs = qs.filter(category_id=c)
    if df: qs = qs.filter(date__gte=df)
    if dt: qs = qs.filter(date__lte=dt)
    if s: qs = qs.filter(Q(title__icontains=s)|Q(notes__icontains=s))
    paginator = Paginator(qs, 15)
    transactions = paginator.get_page(request.GET.get("page"))
    categories = Category.objects.filter(Q(user=request.user)|Q(is_default=True))
    return render(request,"transactions/list.html",{"transactions":transactions,"categories":categories})

@login_required
def transaction_add(request):
    form = TransactionForm(user=request.user)
    if request.method == "POST":
        form = TransactionForm(request.user, request.POST)
        if form.is_valid():
            t = form.save(commit=False); t.user = request.user; t.save()
            messages.success(request,"Transaction added!")
            return redirect("transaction_list")
    return render(request,"transactions/form.html",{"form":form,"action":"Add"})

@login_required
def transaction_edit(request, pk):
    txn = get_object_or_404(Transaction, pk=pk, user=request.user)
    form = TransactionForm(user=request.user, instance=txn)
    if request.method == "POST":
        form = TransactionForm(request.user, request.POST, instance=txn)
        if form.is_valid():
            form.save(); messages.success(request,"Updated!")
            return redirect("transaction_list")
    return render(request,"transactions/form.html",{"form":form,"action":"Edit"})

@login_required
def transaction_delete(request, pk):
    txn = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == "POST":
        txn.delete(); messages.success(request,"Deleted.")
        return redirect("transaction_list")
    return render(request,"transactions/confirm_delete.html",{"object":txn})
