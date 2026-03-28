from django import forms
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
