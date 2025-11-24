from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Expense, Category
from .forms import ExpenseForm, RegisterForm, CategoryForm
from django.db.models import Sum
from django.http import HttpResponse
import csv
from datetime import date
from django.contrib import messages
from django.db.models.functions import TruncMonth

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created. Please log in.")
            return redirect("expenses:login")
    else:
        form = RegisterForm()
    return render(request, "expenses/register.html", {"form": form})

@login_required
def dashboard(request):
    user = request.user
    recent = user.expenses.select_related("category").all()[:5]
    total_month = user.expenses.filter(date__year=date.today().year, date__month=date.today().month).aggregate(total=Sum("amount"))["total"] or 0
    return render(request, "expenses/dashboard.html", {"recent": recent, "total_month": total_month})


@login_required
def expense_list(request):
    qs = request.user.expenses.select_related("category").all()
    category = request.GET.get("category")
    if category:
        qs = qs.filter(category_id=category)
    return render(request, "expenses/expense_list.html", {"expenses": qs, "categories": request.user.categories.all()})

@login_required
def expense_create(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = request.user
            exp.save()
            messages.success(request, "Expense added.")
            return redirect("expenses:expense_list")
    else:
        form = ExpenseForm()
    return render(request, "expenses/expense_form.html", {"form": form})

@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated.")
            return redirect("expenses:expense_list")
    else:
        form = ExpenseForm(instance=expense)
    return render(request, "expenses/expense_form.html", {"form": form, "expense": expense})

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted.")
        return redirect("expenses:expense_list")
    return render(request, "expenses/expense_confirm_delete.html", {"expense": expense})

@login_required
def report(request):
    qs = request.user.expenses.annotate(month=TruncMonth("date")).values("month").annotate(total=Sum("amount")).order_by("month")
    data = [{"month": item["month"].strftime("%Y-%m"), "total": float(item["total"])} for item in qs]
    cats = request.user.categories.annotate(total=Sum("expenses__amount")).values("name", "total")
    categories = [{"name": c["name"], "total": float(c["total"] or 0)} for c in cats]
    return render(request, "expenses/report.html", {"data": data, "categories": categories})

@login_required
def export_csv(request):
    expenses = request.user.expenses.all().order_by("-date")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(["Title", "Amount", "Date", "Category", "Notes"])
    for e in expenses:
        writer.writerow([e.title, str(e.amount), e.date.isoformat(), e.category.name if e.category else "", e.notes])
    return response


@login_required
def category_list(request):
    qs = request.user.categories.all()
    return render(request, "expenses/category_list.html", {"categories": qs})

@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = request.user
            cat.save()
            messages.success(request, "Category added.")
            return redirect("expenses:category_list")
    else:
        form = CategoryForm()
    return render(request, "expenses/category_form.html", {"form": form})

@login_required
def category_update(request, pk):
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect("expenses:category_list")
    else:
        form = CategoryForm(instance=cat)
    return render(request, "expenses/category_form.html", {"form": form, "category": cat})

@login_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == "POST":
        cat.delete()
        messages.success(request, "Category deleted.")
        return redirect("expenses:category_list")
    return render(request, "expenses/category_confirm_delete.html", {"category": cat})


# --- Enhanced dashboard and report views appended by patch ---

from django.db.models import Sum
from django.db.models.functions import TruncMonth
import datetime as _dt

@login_required
def dashboard(request):
    user = request.user
    recent = user.expenses.select_related("category").all()[:5]

    # totals
    from django.db.models import Sum
    from datetime import date
    total_month = user.expenses.filter(date__year=date.today().year, date__month=date.today().month).aggregate(total=Sum("amount"))["total"] or 0
    total_all = user.expenses.aggregate(total=Sum("amount"))["total"] or 0
    expense_count = user.expenses.count()
    highest = user.expenses.order_by("-amount").first()
    highest_amount = highest.amount if highest else 0

    # monthly series
    qs = user.expenses.annotate(month=TruncMonth("date")).values("month").annotate(total=Sum("amount")).order_by("month")
    data = [{"month": item["month"].strftime("%Y-%m"), "total": float(item["total"])} for item in qs]

    today = _dt.date.today()
    labels = []
    vals = []
    # last 6 months labels
    for i in range(5, -1, -1):
        ym = (today.replace(day=1) - _dt.timedelta(days=30*i))
        label = f"{ym.year}-{ym.month:02d}"
        labels.append(label)
        found = next((d for d in data if d["month"] == label), None)
        vals.append(found["total"] if found else 0)

    summary = {
        "total_month": total_month,
        "total_all": total_all,
        "expense_count": expense_count,
        "highest_amount": highest_amount,
        "labels": labels,
        "values": vals,
    }

    return render(request, "expenses/dashboard.html", {"recent": recent, "summary": summary})

@login_required
def report(request):
    user = request.user
    # monthly totals (last 12 months)
    qs = user.expenses.annotate(month=TruncMonth("date")).values("month").annotate(total=Sum("amount")).order_by("month")
    data = [{"month": item["month"].strftime("%Y-%m"), "total": float(item["total"])} for item in qs]

    # compute last 12 months labels and values
    today = _dt.date.today()
    months = []
    values = []
    for i in range(11, -1, -1):
        ym = (today.replace(day=1) - _dt.timedelta(days=30*i))
        label = f"{ym.year}-{ym.month:02d}"
        months.append(label)
        found = next((d for d in data if d["month"] == label), None)
        values.append(found["total"] if found else 0)

    # category breakdown (top categories)
    cats = user.categories.annotate(total=Sum("expenses__amount")).values("name", "total")
    categories = [{"name": c["name"], "total": float(c["total"] or 0)} for c in cats]
    top_cats = sorted(categories, key=lambda x: x["total"], reverse=True)[:8]

    # top expenses
    top_expenses_qs = user.expenses.select_related("category").order_by("-amount")[:10]
    top_expenses = [{"title": e.title, "amount": float(e.amount), "date": e.date.strftime("%Y-%m-%d"), "category": (e.category.name if e.category else "")} for e in top_expenses_qs]

    total_sum = sum(values)
    months_count = len(values)
    avg_month = (total_sum / months_count) if months_count else 0

    return render(request, "expenses/report.html", {
        "months": months, "values": values, "top_cats": top_cats,
        "top_expenses": top_expenses, "avg_month": avg_month
    })
