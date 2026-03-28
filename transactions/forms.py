from django import forms
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
