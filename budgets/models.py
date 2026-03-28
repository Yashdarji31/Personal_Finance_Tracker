from django.db import models
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
