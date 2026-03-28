from django.db import models
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
