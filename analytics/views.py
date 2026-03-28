from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from transactions.models import Transaction
from budgets.models import Budget
import datetime, json

@login_required
def dashboard(request):
    user = request.user
    today = datetime.date.today()
    monthly_income = Transaction.objects.filter(user=user,transaction_type="income",
        date__month=today.month,date__year=today.year).aggregate(total=Sum("amount"))["total"] or 0
    monthly_expense = Transaction.objects.filter(user=user,transaction_type="expense",
        date__month=today.month,date__year=today.year).aggregate(total=Sum("amount"))["total"] or 0
    net_balance = monthly_income - monthly_expense
    total_income = Transaction.objects.filter(user=user,transaction_type="income").aggregate(total=Sum("amount"))["total"] or 0
    total_expense = Transaction.objects.filter(user=user,transaction_type="expense").aggregate(total=Sum("amount"))["total"] or 0
    recent_transactions = Transaction.objects.filter(user=user)[:8]
    budgets = Budget.objects.filter(user=user,month=today.month,year=today.year)
    budget_alerts = [{"budget":b,"percentage":b.get_percentage()} for b in budgets if b.get_percentage()>=80]
    trend_data = []
    for i in range(5,-1,-1):
        d = today - datetime.timedelta(days=30*i)
        inc = Transaction.objects.filter(user=user,transaction_type="income",date__month=d.month,date__year=d.year).aggregate(total=Sum("amount"))["total"] or 0
        exp = Transaction.objects.filter(user=user,transaction_type="expense",date__month=d.month,date__year=d.year).aggregate(total=Sum("amount"))["total"] or 0
        trend_data.append({"month":d.strftime("%b %Y"),"income":float(inc),"expense":float(exp)})
    expense_by_cat = Transaction.objects.filter(user=user,transaction_type="expense",
        date__month=today.month,date__year=today.year).values(
        "category__name","category__color","category__icon").annotate(total=Sum("amount")).order_by("-total")[:8]
    return render(request,"analytics/dashboard.html",{
        "monthly_income":monthly_income,"monthly_expense":monthly_expense,
        "net_balance":net_balance,"total_income":total_income,"total_expense":total_expense,
        "recent_transactions":recent_transactions,"budget_alerts":budget_alerts,
        "trend_data":json.dumps(trend_data),
        "expense_by_category":json.dumps([{"name":e["category__name"] or "Uncategorized",
            "color":e["category__color"] or "#6366f1","icon":e["category__icon"] or "💰",
            "total":float(e["total"])} for e in expense_by_cat]),
        "today":today,
    })
