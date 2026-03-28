from django.core.management.base import BaseCommand
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
