import os
BASE = os.path.dirname(os.path.abspath(__file__))
def write(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  created: {path}')
print('Starting setup...')

write('finance_tracker/settings.py', '''from pathlib import Path
from decouple import config
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config("SECRET_KEY", default="django-insecure-change-me")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
INSTALLED_APPS = [
    "django.contrib.admin","django.contrib.auth","django.contrib.contenttypes",
    "django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles",
    "crispy_forms","crispy_bootstrap5","accounts","transactions","budgets","analytics",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "finance_tracker.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates","DIRS": [BASE_DIR / "templates"],"APP_DIRS": True,"OPTIONS": {"context_processors": ["django.template.context_processors.debug","django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages",]},}]
WSGI_APPLICATION = "finance_tracker.wsgi.application"
DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql","NAME": config("DB_NAME", default="finance_tracker"),"USER": config("DB_USER", default="postgres"),"PASSWORD": config("DB_PASSWORD", default=""),"HOST": config("DB_HOST", default="localhost"),"PORT": config("DB_PORT", default="5432"),}}
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/analytics/"
LOGOUT_REDIRECT_URL = "/accounts/login/"
''')
print('settings done')

write('finance_tracker/urls.py', '''from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("transactions/", include("transactions.urls")),
    path("budgets/", include("budgets.urls")),
    path("analytics/", include("analytics.urls")),
    path("", RedirectView.as_view(url="/analytics/", permanent=False)),
]
''')
write('accounts/models.py', '')
write('accounts/admin.py', 'from django.contrib import admin\n')
write('analytics/models.py', '')
write('analytics/admin.py', 'from django.contrib import admin\n')
write('budgets/admin.py', 'from django.contrib import admin\nfrom .models import Budget\nadmin.site.register(Budget)\n')
write('transactions/admin.py', 'from django.contrib import admin\nfrom .models import Transaction, Category\nadmin.site.register(Transaction)\nadmin.site.register(Category)\n')
os.makedirs(os.path.join(BASE, 'static'), exist_ok=True)
os.makedirs(os.path.join(BASE, 'templates/accounts'), exist_ok=True)
os.makedirs(os.path.join(BASE, 'templates/analytics'), exist_ok=True)
os.makedirs(os.path.join(BASE, 'templates/transactions'), exist_ok=True)
os.makedirs(os.path.join(BASE, 'templates/budgets'), exist_ok=True)
print('urls and dirs done')

write('accounts/urls.py', '''from django.urls import path
from . import views
urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
''')
write('accounts/views.py', '''from django.shortcuts import render, redirect
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
''')
print('accounts done')

write('transactions/models.py', '''from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    CATEGORY_TYPES = [("income","Income"),("expense","Expense")]
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    icon = models.CharField(max_length=50, default="💰")
    color = models.CharField(max_length=7, default="#6366f1")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]
    def __str__(self):
        return f"{self.icon} {self.name}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [("income","Income"),("expense","Expense")]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-date","-created_at"]
    def __str__(self):
        return f"{self.title} - {self.amount}"
''')
write('transactions/forms.py', '''from django import forms
from django.db.models import Q
from .models import Transaction, Category

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["title","amount","transaction_type","category","date","notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type":"date"}),
            "notes": forms.Textarea(attrs={"rows":3}),
        }
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["category"].queryset = Category.objects.filter(
                Q(user=user)|Q(is_default=True))
        for f in self.fields.values():
            f.widget.attrs["class"] = "form-control"
''')
print('transactions models+forms done')

write('transactions/views.py', '''from django.shortcuts import render, redirect, get_object_or_404
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
''')
write('transactions/urls.py', '''from django.urls import path
from . import views
urlpatterns = [
    path("", views.transaction_list, name="transaction_list"),
    path("add/", views.transaction_add, name="transaction_add"),
    path("<int:pk>/edit/", views.transaction_edit, name="transaction_edit"),
    path("<int:pk>/delete/", views.transaction_delete, name="transaction_delete"),
]
''')
write('transactions/management/__init__.py', '')
write('transactions/management/commands/__init__.py', '')
write('transactions/management/commands/seed_categories.py', '''from django.core.management.base import BaseCommand
from transactions.models import Category
class Command(BaseCommand):
    help = "Seed default categories"
    def handle(self, *args, **kwargs):
        defaults = [
            ("Salary","income","💼","#10b981"),("Freelance","income","💻","#06b6d4"),
            ("Investment","income","📈","#8b5cf6"),("Other Income","income","💰","#f59e0b"),
            ("Food & Dining","expense","🍽️","#ef4444"),("Transport","expense","🚗","#f97316"),
            ("Shopping","expense","🛍️","#ec4899"),("Utilities","expense","💡","#eab308"),
            ("Healthcare","expense","🏥","#14b8a6"),("Entertainment","expense","🎬","#6366f1"),
            ("Education","expense","📚","#0ea5e9"),("Rent","expense","🏠","#84cc16"),
        ]
        created = 0
        for name,ctype,icon,color in defaults:
            _,made = Category.objects.get_or_create(name=name,category_type=ctype,
                defaults={"icon":icon,"color":color,"is_default":True})
            if made: created += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} categories."))
''')
print('transactions views+urls+seed done')

write('budgets/models.py', '''from django.db import models
from django.contrib.auth.models import User
from transactions.models import Category
import datetime

class Budget(models.Model):
    PERIOD_CHOICES = [("monthly","Monthly"),("weekly","Weekly"),("yearly","Yearly")]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budgets")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default="monthly")
    month = models.IntegerField(default=datetime.date.today().month)
    year = models.IntegerField(default=datetime.date.today().year)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ["user","category","month","year"]
        ordering = ["-year","-month"]
    def __str__(self):
        return f"{self.category.name} Budget"
    def get_spent(self):
        from transactions.models import Transaction
        return Transaction.objects.filter(user=self.user,category=self.category,
            transaction_type="expense",date__month=self.month,date__year=self.year
        ).aggregate(models.Sum("amount"))["amount__sum"] or 0
    def get_percentage(self):
        s = self.get_spent()
        return min(round((s/self.amount)*100),100) if self.amount else 0
    def get_remaining(self):
        return self.amount - self.get_spent()
''')
write('budgets/forms.py', '''from django import forms
from django.db.models import Q
from .models import Budget
from transactions.models import Category
import datetime

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ["category","amount","period","month","year"]
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["category"].queryset = Category.objects.filter(
                Q(user=user)|Q(is_default=True), category_type="expense")
        for f in self.fields.values():
            f.widget.attrs["class"] = "form-control"
        y = datetime.date.today().year
        self.fields["month"].widget = forms.Select(attrs={"class":"form-control"},
            choices=[(i,i) for i in range(1,13)])
        self.fields["year"].widget = forms.Select(attrs={"class":"form-control"},
            choices=[(y2,y2) for y2 in range(y-2,y+3)])
''')
write('budgets/urls.py', '''from django.urls import path
from . import views
urlpatterns = [
    path("", views.budget_list, name="budget_list"),
    path("add/", views.budget_add, name="budget_add"),
    path("<int:pk>/edit/", views.budget_edit, name="budget_edit"),
    path("<int:pk>/delete/", views.budget_delete, name="budget_delete"),
]
''')
write('budgets/views.py', '''from django.shortcuts import render, redirect, get_object_or_404
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
''')
print('budgets done')

write('analytics/urls.py', '''from django.urls import path
from . import views
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
]
''')
write('analytics/views.py', '''from django.shortcuts import render
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
''')
print('analytics done')

write('templates/accounts/login.html', '''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><title>Sign In - Ledger</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#0c0e14;--bg2:#13151f;--bg3:#1a1d2b;--border:rgba(255,255,255,0.07);--text:#e8eaf0;--muted:#6b7280;--accent:#c9f03d;}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:"DM Sans",sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;}
body::before{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(201,240,61,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(201,240,61,0.03) 1px,transparent 1px);background-size:50px 50px;pointer-events:none;}
.wrap{width:100%;max-width:400px;padding:20px;position:relative;z-index:1;animation:fadeUp .4s ease both;}
.brand{text-align:center;margin-bottom:32px;}.brand h1{font-family:"Playfair Display",serif;font-size:36px;color:var(--accent);}.brand p{color:var(--muted);font-size:13px;margin-top:6px;}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:16px;padding:32px;}
.form-label{display:block;font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:6px;}
.form-control{width:100%;background:var(--bg3);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:11px 14px;font-size:14px;font-family:"DM Sans",sans-serif;outline:none;transition:border-color .15s;}
.form-control:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(201,240,61,.1);}
.form-group{margin-bottom:18px;}
.btn{width:100%;background:var(--accent);color:#000;border:none;border-radius:8px;padding:12px;font-size:14px;font-weight:600;cursor:pointer;margin-top:8px;}
.footer{text-align:center;margin-top:20px;font-size:13px;color:var(--muted);}.footer a{color:var(--accent);text-decoration:none;}
.error{color:#f87171;font-size:12px;margin-top:4px;}
.alert{background:rgba(248,113,113,.1);border:1px solid rgba(248,113,113,.2);color:#f87171;border-radius:8px;padding:10px 14px;font-size:13px;margin-bottom:18px;}
@keyframes fadeUp{from{opacity:0;transform:translateY(16px);}to{opacity:1;transform:translateY(0);}}
</style></head><body>
<div class="wrap">
  <div class="brand"><h1>Ledger</h1><p>Your personal finance companion</p></div>
  <div class="card">
    <h2 style="font-size:18px;margin-bottom:24px;font-weight:600;">Welcome back</h2>
    {% if messages %}{% for message in messages %}<div class="alert">{{ message }}</div>{% endfor %}{% endif %}
    <form method="post">{% csrf_token %}
    {% for field in form %}<div class="form-group"><label class="form-label">{{ field.label }}</label>
    <input type="{{ field.field.widget.input_type }}" name="{{ field.html_name }}" class="form-control" {% if field.value %}value="{{ field.value }}"{% endif %}>
    {% if field.errors %}<div class="error">{{ field.errors.0 }}</div>{% endif %}</div>{% endfor %}
    <button type="submit" class="btn">Sign In</button></form>
  </div>
  <div class="footer">No account? <a href="{% url "register" %}">Create one</a></div>
</div></body></html>''')

write('templates/accounts/register.html', '''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><title>Register - Ledger</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#0c0e14;--bg2:#13151f;--bg3:#1a1d2b;--border:rgba(255,255,255,0.07);--text:#e8eaf0;--muted:#6b7280;--accent:#c9f03d;}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:"DM Sans",sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;}
body::before{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(201,240,61,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(201,240,61,0.03) 1px,transparent 1px);background-size:50px 50px;pointer-events:none;}
.wrap{width:100%;max-width:440px;padding:20px;position:relative;z-index:1;animation:fadeUp .4s ease both;}
.brand{text-align:center;margin-bottom:32px;}.brand h1{font-family:"Playfair Display",serif;font-size:36px;color:var(--accent);}.brand p{color:var(--muted);font-size:13px;margin-top:6px;}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:16px;padding:32px;}
.form-label{display:block;font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:6px;}
.form-control{width:100%;background:var(--bg3);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:11px 14px;font-size:14px;font-family:"DM Sans",sans-serif;outline:none;transition:border-color .15s;}
.form-control:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(201,240,61,.1);}
.form-group{margin-bottom:16px;}
.btn{width:100%;background:var(--accent);color:#000;border:none;border-radius:8px;padding:12px;font-size:14px;font-weight:600;cursor:pointer;margin-top:8px;}
.footer{text-align:center;margin-top:20px;font-size:13px;color:var(--muted);}.footer a{color:var(--accent);text-decoration:none;}
.error{color:#f87171;font-size:12px;margin-top:4px;}.help{color:var(--muted);font-size:11px;margin-top:4px;}
@keyframes fadeUp{from{opacity:0;transform:translateY(16px);}to{opacity:1;transform:translateY(0);}}
</style></head><body>
<div class="wrap">
  <div class="brand"><h1>Ledger</h1><p>Start tracking your finances today</p></div>
  <div class="card">
    <h2 style="font-size:18px;margin-bottom:24px;font-weight:600;">Create account</h2>
    <form method="post">{% csrf_token %}
    {% for field in form %}<div class="form-group"><label class="form-label">{{ field.label }}</label>
    <input type="{{ field.field.widget.input_type }}" name="{{ field.html_name }}" class="form-control" {% if field.value %}value="{{ field.value }}"{% endif %}>
    {% if field.help_text %}<div class="help">{{ field.help_text }}</div>{% endif %}
    {% if field.errors %}<div class="error">{{ field.errors.0 }}</div>{% endif %}</div>{% endfor %}
    <button type="submit" class="btn">Create Account</button></form>
  </div>
  <div class="footer">Already have an account? <a href="{% url "login" %}">Sign in</a></div>
</div></body></html>''')
print('auth templates done')

write('templates/base.html', '''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{% block title %}Ledger{% endblock %}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
<style>
:root{--bg:#0c0e14;--bg2:#13151f;--bg3:#1a1d2b;--border:rgba(255,255,255,0.07);--text:#e8eaf0;--muted:#6b7280;--accent:#c9f03d;--accent2:#3dbbf0;--income:#34d399;--expense:#f87171;--font-display:"Playfair Display",serif;--font-body:"DM Sans",sans-serif;--font-mono:"DM Mono",monospace;}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:var(--font-body);font-size:14px;min-height:100vh;}
.sidebar{position:fixed;top:0;left:0;width:220px;height:100vh;background:var(--bg2);border-right:1px solid var(--border);display:flex;flex-direction:column;z-index:100;}
.sidebar-brand{padding:28px 24px 20px;border-bottom:1px solid var(--border);}
.sidebar-brand h1{font-family:var(--font-display);font-size:22px;color:var(--accent);}
.sidebar-brand span{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;font-family:var(--font-mono);}
.sidebar-nav{padding:20px 12px;flex:1;display:flex;flex-direction:column;gap:2px;}
.nav-label{font-size:9px;text-transform:uppercase;letter-spacing:2px;color:var(--muted);padding:12px 12px 6px;font-family:var(--font-mono);}
.sidebar-nav a{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:8px;color:var(--muted);text-decoration:none;font-weight:500;font-size:13px;transition:all .15s;}
.sidebar-nav a:hover,.sidebar-nav a.active{background:var(--bg3);color:var(--text);}
.sidebar-nav a.active{color:var(--accent);box-shadow:inset 2px 0 0 var(--accent);border-radius:0 8px 8px 0;margin-left:-12px;padding-left:24px;}
.sidebar-bottom{padding:16px 12px;border-top:1px solid var(--border);}
.sidebar-bottom a{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:8px;color:var(--muted);text-decoration:none;font-size:13px;transition:all .15s;}
.sidebar-bottom a:hover{background:var(--bg3);color:var(--expense);}
.user-chip{display:flex;align-items:center;gap:10px;padding:10px 12px;margin-bottom:8px;}
.user-avatar{width:30px;height:30px;background:linear-gradient(135deg,var(--accent),var(--accent2));border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#000;}
.main-wrap{margin-left:220px;min-height:100vh;display:flex;flex-direction:column;}
.topbar{background:var(--bg2);border-bottom:1px solid var(--border);padding:14px 32px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:50;}
.topbar-title{font-family:var(--font-display);font-size:19px;}
.topbar-actions{display:flex;gap:10px;align-items:center;}
.page-content{padding:32px;flex:1;}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:14px;}
.card-header{background:transparent;border-bottom:1px solid var(--border);padding:16px 20px;font-weight:600;font-size:13px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);}
.card-body{padding:20px;}
.stat-card{background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:22px 24px;position:relative;overflow:hidden;transition:transform .2s;}
.stat-card:hover{transform:translateY(-2px);}
.stat-card::before{content:"";position:absolute;top:0;left:0;right:0;height:2px;}
.stat-card.income::before{background:var(--income);}.stat-card.expense::before{background:var(--expense);}.stat-card.balance::before{background:var(--accent);}.stat-card.total::before{background:var(--accent2);}
.stat-label{font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:var(--muted);font-family:var(--font-mono);margin-bottom:10px;}
.stat-value{font-family:var(--font-display);font-size:28px;font-weight:700;line-height:1;}
.stat-value.income{color:var(--income);}.stat-value.expense{color:var(--expense);}.stat-value.balance{color:var(--accent);}.stat-value.total{color:var(--accent2);}
.stat-sub{font-size:11px;color:var(--muted);margin-top:6px;}
.stat-icon{position:absolute;right:20px;top:50%;transform:translateY(-50%);font-size:36px;opacity:.08;}
.btn-accent{background:var(--accent);color:#000;border:none;border-radius:8px;padding:8px 18px;font-size:13px;font-weight:600;cursor:pointer;font-family:var(--font-body);transition:opacity .15s;text-decoration:none;display:inline-block;}
.btn-accent:hover{opacity:.9;color:#000;}
.btn-ghost{background:transparent;border:1px solid var(--border);color:var(--muted);border-radius:8px;padding:8px 16px;font-size:13px;cursor:pointer;text-decoration:none;display:inline-block;transition:all .15s;}
.btn-ghost:hover{border-color:rgba(255,255,255,.2);color:var(--text);}
.btn-danger-ghost{background:transparent;border:1px solid rgba(248,113,113,.3);color:var(--expense);border-radius:8px;padding:6px 14px;font-size:12px;cursor:pointer;text-decoration:none;display:inline-block;transition:all .15s;}
.btn-danger-ghost:hover{background:rgba(248,113,113,.1);}
.data-table{width:100%;border-collapse:collapse;}
.data-table th{font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:var(--muted);font-family:var(--font-mono);padding:12px 16px;text-align:left;border-bottom:1px solid var(--border);}
.data-table td{padding:13px 16px;border-bottom:1px solid var(--border);font-size:13px;}
.data-table tr:last-child td{border-bottom:none;}
.data-table tr:hover td{background:rgba(255,255,255,.02);}
.badge-income{background:rgba(52,211,153,.12);color:var(--income);border:1px solid rgba(52,211,153,.2);border-radius:20px;padding:3px 10px;font-size:11px;}
.badge-expense{background:rgba(248,113,113,.12);color:var(--expense);border:1px solid rgba(248,113,113,.2);border-radius:20px;padding:3px 10px;font-size:11px;}
.amount-income{color:var(--income);font-family:var(--font-mono);font-weight:500;}
.amount-expense{color:var(--expense);font-family:var(--font-mono);font-weight:500;}
.form-control,.form-select{background:var(--bg3)!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:8px!important;padding:10px 14px!important;font-size:13px!important;transition:border-color .15s!important;}
.form-control:focus,.form-select:focus{border-color:var(--accent)!important;box-shadow:0 0 0 3px rgba(201,240,61,.1)!important;outline:none!important;}
.form-label{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);font-family:var(--font-mono);margin-bottom:6px;}
.form-control::placeholder{color:#4b5563!important;}
.progress{background:var(--bg3);border-radius:99px;height:6px;}
.progress-bar{border-radius:99px;transition:width .6s ease;}
.alert{border-radius:10px;font-size:13px;padding:12px 16px;}
.alert-success{background:rgba(52,211,153,.1);color:var(--income);border:1px solid rgba(52,211,153,.2)!important;}
.alert-danger{background:rgba(248,113,113,.1);color:var(--expense);border:1px solid rgba(248,113,113,.2)!important;}
.alert-warning{background:rgba(251,191,36,.1);color:#fbbf24;border:1px solid rgba(251,191,36,.2)!important;}
.mono{font-family:var(--font-mono);}
.text-muted{color:var(--muted)!important;}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px);}to{opacity:1;transform:translateY(0);}}
.fade-up{animation:fadeUp .4s ease both;}.fade-up-1{animation-delay:.05s;}.fade-up-2{animation-delay:.1s;}.fade-up-3{animation-delay:.15s;}.fade-up-4{animation-delay:.2s;}
::-webkit-scrollbar{width:6px;}::-webkit-scrollbar-track{background:var(--bg);}::-webkit-scrollbar-thumb{background:var(--bg3);border-radius:3px;}
option{background:var(--bg3);}
</style></head><body>
{% if user.is_authenticated %}
<aside class="sidebar">
  <div class="sidebar-brand"><h1>Ledger</h1><span>Finance Tracker</span></div>
  <nav class="sidebar-nav">
    <div class="nav-label">Overview</div>
    <a href="{% url "dashboard" %}" class="{% if request.resolver_match.url_name == "dashboard" %}active{% endif %}"><i class="bi bi-grid-1x2"></i> Dashboard</a>
    <div class="nav-label">Money</div>
    <a href="{% url "transaction_list" %}" class="{% if "transaction" in request.resolver_match.url_name %}active{% endif %}"><i class="bi bi-arrow-left-right"></i> Transactions</a>
    <a href="{% url "transaction_add" %}"><i class="bi bi-plus-circle"></i> Add Transaction</a>
    <div class="nav-label">Planning</div>
    <a href="{% url "budget_list" %}" class="{% if "budget" in request.resolver_match.url_name %}active{% endif %}"><i class="bi bi-bullseye"></i> Budgets</a>
    <a href="{% url "budget_add" %}"><i class="bi bi-plus-square"></i> New Budget</a>
  </nav>
  <div class="sidebar-bottom">
    <div class="user-chip"><div class="user-avatar">{{ user.username|first|upper }}</div><span>{{ user.username }}</span></div>
    <a href="{% url "logout" %}"><i class="bi bi-box-arrow-left"></i> Sign Out</a>
  </div>
</aside>
{% endif %}
<div class="main-wrap">
  <div class="topbar"><span class="topbar-title">{% block page_title %}Dashboard{% endblock %}</span><div class="topbar-actions">{% block topbar_actions %}{% endblock %}</div></div>
  <div class="page-content">
    {% for message in messages %}<div class="alert alert-{{ message.tags }} alert-dismissible fade show mb-3">{{ message }}<button type="button" class="btn-close" data-bs-dismiss="alert" style="filter:invert(1);opacity:.5;"></button></div>{% endfor %}
    {% block content %}{% endblock %}
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
{% block extra_js %}{% endblock %}
</body></html>''')
print('base template done')

write('templates/analytics/dashboard.html', '''{% extends "base.html" %}
{% block title %}Dashboard - Ledger{% endblock %}
{% block page_title %}Dashboard{% endblock %}
{% block topbar_actions %}<a href="{% url "transaction_add" %}" class="btn-accent"><i class="bi bi-plus"></i> Add Transaction</a>{% endblock %}
{% block content %}
<div class="row g-3 mb-4">
  <div class="col-md-3 fade-up fade-up-1"><div class="stat-card income"><div class="stat-label">Monthly Income</div><div class="stat-value income">Rs. {{ monthly_income|floatformat:0 }}</div><div class="stat-sub">{{ today|date:"F Y" }}</div><i class="bi bi-arrow-down-circle stat-icon"></i></div></div>
  <div class="col-md-3 fade-up fade-up-2"><div class="stat-card expense"><div class="stat-label">Monthly Expenses</div><div class="stat-value expense">Rs. {{ monthly_expense|floatformat:0 }}</div><div class="stat-sub">{{ today|date:"F Y" }}</div><i class="bi bi-arrow-up-circle stat-icon"></i></div></div>
  <div class="col-md-3 fade-up fade-up-3"><div class="stat-card balance"><div class="stat-label">Net Balance</div><div class="stat-value balance">Rs. {{ net_balance|floatformat:0 }}</div><div class="stat-sub">Income - Expenses</div><i class="bi bi-wallet2 stat-icon"></i></div></div>
  <div class="col-md-3 fade-up fade-up-4"><div class="stat-card total"><div class="stat-label">Total Income</div><div class="stat-value total">Rs. {{ total_income|floatformat:0 }}</div><div class="stat-sub">All time</div><i class="bi bi-graph-up-arrow stat-icon"></i></div></div>
</div>
{% if budget_alerts %}{% for alert in budget_alerts %}<div class="alert alert-warning d-flex align-items-center gap-2 mb-3"><i class="bi bi-exclamation-triangle-fill"></i><span><strong>{{ alert.budget.category }}</strong> budget is at {{ alert.percentage }}%</span></div>{% endfor %}{% endif %}
<div class="row g-3 mb-4">
  <div class="col-lg-7 fade-up fade-up-2"><div class="card h-100"><div class="card-header">6-Month Income vs Expense</div><div class="card-body"><canvas id="trendChart" height="220"></canvas></div></div></div>
  <div class="col-lg-5 fade-up fade-up-3"><div class="card h-100"><div class="card-header">Spending by Category</div><div class="card-body d-flex align-items-center justify-content-center"><canvas id="categoryChart" height="220"></canvas></div></div></div>
</div>
<div class="row g-3">
  <div class="col-lg-7 fade-up"><div class="card"><div class="card-header d-flex justify-content-between align-items-center">Recent Transactions <a href="{% url "transaction_list" %}" class="btn-ghost" style="font-size:11px;">View All</a></div>
  <div class="card-body p-0">{% if recent_transactions %}<table class="data-table"><thead><tr><th>Title</th><th>Category</th><th>Date</th><th>Amount</th></tr></thead><tbody>
  {% for txn in recent_transactions %}<tr><td><div style="font-weight:500;">{{ txn.title }}</div></td><td>{% if txn.category %}{{ txn.category.icon }} {{ txn.category.name }}{% else %}-{% endif %}</td><td><span class="mono" style="font-size:12px;color:var(--muted);">{{ txn.date|date:"d M" }}</span></td><td>{% if txn.transaction_type == "income" %}<span class="amount-income">+Rs.{{ txn.amount|floatformat:0 }}</span>{% else %}<span class="amount-expense">-Rs.{{ txn.amount|floatformat:0 }}</span>{% endif %}</td></tr>{% endfor %}
  </tbody></table>{% else %}<div style="padding:40px;text-align:center;color:var(--muted);"><i class="bi bi-inbox" style="font-size:32px;display:block;margin-bottom:10px;"></i>No transactions yet. <a href="{% url "transaction_add" %}" style="color:var(--accent);">Add one!</a></div>{% endif %}</div></div></div>
  <div class="col-lg-5 fade-up fade-up-2"><div class="card"><div class="card-header d-flex justify-content-between align-items-center">Budget Goals <a href="{% url "budget_list" %}" class="btn-ghost" style="font-size:11px;">Manage</a></div>
  <div class="card-body">{% if budget_alerts %}{% for alert in budget_alerts %}<div class="mb-3"><div class="d-flex justify-content-between mb-1"><span>{{ alert.budget.category }}</span><span class="mono" style="font-size:12px;">{{ alert.percentage }}%</span></div><div class="progress"><div class="progress-bar" style="width:{{ alert.percentage }}%;background:{% if alert.percentage >= 100 %}var(--expense){% elif alert.percentage >= 80 %}#fbbf24{% else %}var(--income){% endif %};"></div></div></div>{% endfor %}
  {% else %}<div style="text-align:center;color:var(--muted);padding:30px 0;"><i class="bi bi-bullseye" style="font-size:28px;display:block;margin-bottom:8px;"></i><div>No budgets this month.</div><a href="{% url "budget_add" %}" style="color:var(--accent);">Create a budget</a></div>{% endif %}</div></div></div>
</div>
{% endblock %}
{% block extra_js %}<script>
const trendData={{trend_data|safe}};const categoryData={{expense_by_category|safe}};
Chart.defaults.color="#6b7280";Chart.defaults.borderColor="rgba(255,255,255,0.06)";Chart.defaults.font.family="DM Sans,sans-serif";
new Chart(document.getElementById("trendChart"),{type:"bar",data:{labels:trendData.map(d=>d.month),datasets:[{label:"Income",data:trendData.map(d=>d.income),backgroundColor:"rgba(52,211,153,0.25)",borderColor:"#34d399",borderWidth:2,borderRadius:5},{label:"Expenses",data:trendData.map(d=>d.expense),backgroundColor:"rgba(248,113,113,0.25)",borderColor:"#f87171",borderWidth:2,borderRadius:5}]},options:{responsive:true,plugins:{legend:{labels:{boxWidth:12,padding:20}}},scales:{x:{grid:{display:false}},y:{ticks:{callback:v=>"Rs."+v.toLocaleString()},grid:{color:"rgba(255,255,255,0.04)"}}}}});
if(categoryData.length>0){new Chart(document.getElementById("categoryChart"),{type:"doughnut",data:{labels:categoryData.map(d=>d.icon+" "+d.name),datasets:[{data:categoryData.map(d=>d.total),backgroundColor:categoryData.map(d=>d.color+"cc"),borderColor:categoryData.map(d=>d.color),borderWidth:1,hoverOffset:8}]},options:{cutout:"68%",plugins:{legend:{position:"bottom",labels:{boxWidth:10,padding:12,font:{size:11}}},tooltip:{callbacks:{label:ctx=>" Rs."+ctx.raw.toLocaleString()}}}}})}
</script>{% endblock %}''')

write('templates/transactions/list.html', '''{% extends "base.html" %}
{% block title %}Transactions - Ledger{% endblock %}
{% block page_title %}Transactions{% endblock %}
{% block topbar_actions %}<a href="{% url "transaction_add" %}" class="btn-accent"><i class="bi bi-plus"></i> Add</a>{% endblock %}
{% block content %}
<div class="card mb-4 fade-up"><div class="card-body"><form method="get" class="row g-2 align-items-end">
<div class="col-md-3"><label class="form-label">Search</label><input type="text" name="search" class="form-control" placeholder="Title..." value="{{ request.GET.search }}"></div>
<div class="col-md-2"><label class="form-label">Type</label><select name="type" class="form-control"><option value="">All</option><option value="income" {% if request.GET.type == "income" %}selected{% endif %}>Income</option><option value="expense" {% if request.GET.type == "expense" %}selected{% endif %}>Expense</option></select></div>
<div class="col-md-2"><label class="form-label">Category</label><select name="category" class="form-control"><option value="">All</option>{% for cat in categories %}<option value="{{ cat.id }}" {% if request.GET.category == cat.id|stringformat:"s" %}selected{% endif %}>{{ cat }}</option>{% endfor %}</select></div>
<div class="col-md-2"><label class="form-label">From</label><input type="date" name="date_from" class="form-control" value="{{ request.GET.date_from }}"></div>
<div class="col-md-2"><label class="form-label">To</label><input type="date" name="date_to" class="form-control" value="{{ request.GET.date_to }}"></div>
<div class="col-md-1"><button type="submit" class="btn-accent w-100" style="padding:10px;">Go</button></div>
</form></div></div>
<div class="card fade-up fade-up-2"><div class="card-body p-0">
{% if transactions %}<table class="data-table"><thead><tr><th>Title</th><th>Type</th><th>Category</th><th>Date</th><th>Amount</th><th>Actions</th></tr></thead><tbody>
{% for txn in transactions %}<tr>
<td><div style="font-weight:500;">{{ txn.title }}</div>{% if txn.notes %}<div style="font-size:11px;color:var(--muted);">{{ txn.notes|truncatechars:50 }}</div>{% endif %}</td>
<td>{% if txn.transaction_type == "income" %}<span class="badge-income">Income</span>{% else %}<span class="badge-expense">Expense</span>{% endif %}</td>
<td>{% if txn.category %}{{ txn.category.icon }} {{ txn.category.name }}{% else %}-{% endif %}</td>
<td><span class="mono" style="font-size:12px;color:var(--muted);">{{ txn.date|date:"d M Y" }}</span></td>
<td>{% if txn.transaction_type == "income" %}<span class="amount-income">+Rs.{{ txn.amount|floatformat:2 }}</span>{% else %}<span class="amount-expense">-Rs.{{ txn.amount|floatformat:2 }}</span>{% endif %}</td>
<td><div class="d-flex gap-2"><a href="{% url "transaction_edit" txn.pk %}" class="btn-ghost" style="padding:5px 12px;font-size:11px;"><i class="bi bi-pencil"></i></a><a href="{% url "transaction_delete" txn.pk %}" class="btn-danger-ghost"><i class="bi bi-trash"></i></a></div></td>
</tr>{% endfor %}</tbody></table>
{% if transactions.has_other_pages %}<div class="d-flex justify-content-center gap-2 p-3">{% if transactions.has_previous %}<a href="?page={{ transactions.previous_page_number }}" class="btn-ghost">Prev</a>{% endif %}<span style="padding:8px 14px;color:var(--muted);">{{ transactions.number }} / {{ transactions.paginator.num_pages }}</span>{% if transactions.has_next %}<a href="?page={{ transactions.next_page_number }}" class="btn-ghost">Next</a>{% endif %}</div>{% endif %}
{% else %}<div style="padding:60px;text-align:center;color:var(--muted);"><i class="bi bi-inbox" style="font-size:40px;display:block;margin-bottom:12px;"></i>No transactions. <a href="{% url "transaction_add" %}" style="color:var(--accent);">Add one</a></div>{% endif %}
</div></div>{% endblock %}''')

write('templates/transactions/form.html', '''{% extends "base.html" %}
{% block title %}{{ action }} Transaction - Ledger{% endblock %}
{% block page_title %}{{ action }} Transaction{% endblock %}
{% block content %}<div class="row justify-content-center"><div class="col-lg-6"><div class="card fade-up"><div class="card-header">Transaction Details</div><div class="card-body">
<form method="post">{% csrf_token %}{% for field in form %}<div class="mb-3"><label class="form-label">{{ field.label }}</label>{{ field }}{% if field.errors %}<div style="color:var(--expense);font-size:12px;margin-top:4px;">{{ field.errors.0 }}</div>{% endif %}</div>{% endfor %}
<div class="d-flex gap-2 mt-4"><button type="submit" class="btn-accent">{{ action }} Transaction</button><a href="{% url "transaction_list" %}" class="btn-ghost">Cancel</a></div>
</form></div></div></div></div>{% endblock %}''')

write('templates/transactions/confirm_delete.html', '''{% extends "base.html" %}
{% block title %}Delete - Ledger{% endblock %}
{% block page_title %}Delete Transaction{% endblock %}
{% block content %}<div class="row justify-content-center"><div class="col-lg-5"><div class="card fade-up"><div class="card-header">Confirm Delete</div><div class="card-body">
<div class="alert alert-danger mb-4"><i class="bi bi-exclamation-triangle-fill me-2"></i>Delete <strong>{{ object.title }}</strong>? This cannot be undone.</div>
<form method="post" class="d-flex gap-2">{% csrf_token %}<button type="submit" class="btn-danger-ghost" style="padding:8px 20px;">Yes, Delete</button><a href="{% url "transaction_list" %}" class="btn-ghost">Cancel</a></form>
</div></div></div></div>{% endblock %}''')

write('templates/budgets/list.html', '''{% extends "base.html" %}
{% block title %}Budgets - Ledger{% endblock %}
{% block page_title %}Budget Goals{% endblock %}
{% block topbar_actions %}<a href="{% url "budget_add" %}" class="btn-accent"><i class="bi bi-plus"></i> New Budget</a>{% endblock %}
{% block content %}
<div class="card mb-4 fade-up"><div class="card-body"><form method="get" class="d-flex gap-3 align-items-end">
<div><label class="form-label">Month</label><select name="month" class="form-control" style="width:100px;">{% for m in months %}<option value="{{ m }}" {% if m == month %}selected{% endif %}>{{ m }}</option>{% endfor %}</select></div>
<div><label class="form-label">Year</label><select name="year" class="form-control" style="width:100px;">{% for y in years %}<option value="{{ y }}" {% if y == year %}selected{% endif %}>{{ y }}</option>{% endfor %}</select></div>
<button type="submit" class="btn-ghost">Apply</button></form></div></div>
{% if budget_data %}<div class="row g-3">{% for item in budget_data %}<div class="col-md-6 col-lg-4 fade-up"><div class="card h-100"><div class="card-body">
<div class="d-flex justify-content-between align-items-start mb-3"><div><div style="font-size:18px;">{{ item.budget.category.icon }}</div><div style="font-weight:600;">{{ item.budget.category.name }}</div></div>
<div class="d-flex gap-2"><a href="{% url "budget_edit" item.budget.pk %}" class="btn-ghost" style="padding:5px 10px;font-size:11px;"><i class="bi bi-pencil"></i></a><a href="{% url "budget_delete" item.budget.pk %}" class="btn-danger-ghost" style="padding:5px 10px;"><i class="bi bi-trash"></i></a></div></div>
<div class="d-flex justify-content-between mb-1"><span class="mono" style="font-size:12px;color:var(--muted);">Spent</span><span class="mono" style="font-size:12px;color:{% if item.percentage >= 100 %}var(--expense){% elif item.percentage >= 80 %}#fbbf24{% else %}var(--income){% endif %};">{{ item.percentage }}%</span></div>
<div class="progress mb-3"><div class="progress-bar" style="width:{{ item.percentage }}%;background:{% if item.percentage >= 100 %}var(--expense){% elif item.percentage >= 80 %}#fbbf24{% else %}var(--income){% endif %};"></div></div>
<div class="d-flex justify-content-between"><div><div style="font-size:10px;color:var(--muted);">SPENT</div><div class="mono amount-expense">Rs.{{ item.spent|floatformat:0 }}</div></div><div style="text-align:right;"><div style="font-size:10px;color:var(--muted);">BUDGET</div><div class="mono">Rs.{{ item.budget.amount|floatformat:0 }}</div></div></div>
{% if item.remaining > 0 %}<div style="margin-top:10px;font-size:11px;color:var(--income);"><i class="bi bi-check-circle-fill"></i> Rs.{{ item.remaining|floatformat:0 }} remaining</div>
{% else %}<div style="margin-top:10px;font-size:11px;color:var(--expense);"><i class="bi bi-x-circle-fill"></i> Over budget!</div>{% endif %}
</div></div></div>{% endfor %}</div>
{% else %}<div class="card fade-up"><div class="card-body" style="text-align:center;padding:60px;"><i class="bi bi-bullseye" style="font-size:40px;color:var(--muted);display:block;margin-bottom:12px;"></i><div style="color:var(--muted);">No budgets for this period.</div><a href="{% url "budget_add" %}" style="color:var(--accent);margin-top:8px;display:inline-block;">Create your first budget</a></div></div>{% endif %}
{% endblock %}''')

write('templates/budgets/form.html', '''{% extends "base.html" %}
{% block title %}{{ action }} Budget - Ledger{% endblock %}
{% block page_title %}{{ action }} Budget{% endblock %}
{% block content %}<div class="row justify-content-center"><div class="col-lg-5"><div class="card fade-up"><div class="card-header">Budget Details</div><div class="card-body">
<form method="post">{% csrf_token %}{% for field in form %}<div class="mb-3"><label class="form-label">{{ field.label }}</label>{{ field }}{% if field.errors %}<div style="color:var(--expense);font-size:12px;margin-top:4px;">{{ field.errors.0 }}</div>{% endif %}</div>{% endfor %}
<div class="d-flex gap-2 mt-4"><button type="submit" class="btn-accent">{{ action }} Budget</button><a href="{% url "budget_list" %}" class="btn-ghost">Cancel</a></div>
</form></div></div></div></div>{% endblock %}''')

write('templates/budgets/confirm_delete.html', '''{% extends "base.html" %}
{% block title %}Delete Budget - Ledger{% endblock %}
{% block page_title %}Delete Budget{% endblock %}
{% block content %}<div class="row justify-content-center"><div class="col-lg-5"><div class="card fade-up"><div class="card-header">Confirm Delete</div><div class="card-body">
<div class="alert alert-danger mb-4"><i class="bi bi-exclamation-triangle-fill me-2"></i>Delete budget for <strong>{{ object.category }}</strong>?</div>
<form method="post" class="d-flex gap-2">{% csrf_token %}<button type="submit" class="btn-danger-ghost" style="padding:8px 20px;">Yes, Delete</button><a href="{% url "budget_list" %}" class="btn-ghost">Cancel</a></form>
</div></div></div></div>{% endblock %}''')

print('ALL TEMPLATES DONE!')
print('Now run:')
print('  python manage.py makemigrations accounts transactions budgets analytics')
print('  python manage.py migrate')
print('  python manage.py seed_categories')
print('  python manage.py runserver')
