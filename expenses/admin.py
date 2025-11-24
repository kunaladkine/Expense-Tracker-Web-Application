from django.contrib import admin
from .models import Category, Expense

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    search_fields = ("name", "user__username")

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "amount", "category", "date")
    list_filter = ("category", "date")
    search_fields = ("title", "notes", "user__username")
