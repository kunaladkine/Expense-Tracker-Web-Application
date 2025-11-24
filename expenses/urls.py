from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "expenses"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/add/", views.expense_create, name="expense_add"),
    path("expenses/<int:pk>/edit/", views.expense_update, name="expense_edit"),
    path("expenses/<int:pk>/delete/", views.expense_delete, name="expense_delete"),
    path("report/", views.report, name="report"),
    path("export/csv/", views.export_csv, name="export_csv"),

    # categories
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_create, name="category_add"),
    path("categories/<int:pk>/edit/", views.category_update, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),

    # auth
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="expenses/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="expenses:login"), name="logout"),
]
