from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/delete/<int:pk>/', views.expense_delete, name='expense_delete'),
    path('expenses/export/', views.export_expenses_csv, name='export_expenses'),
    path('invoices/export/', views.export_invoices_csv, name='export_invoices'),
    path('expenses/bulk-import/', views.bulk_import_expenses, name='bulk_import_expenses'),
    path('invoices/bulk-import/', views.bulk_import_invoices, name='bulk_import_invoices'),
    
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/delete/<int:pk>/', views.invoice_delete, name='invoice_delete'),
    path('reports/', views.financial_reports, name='financial_reports'),
    path('profile/', views.user_profile, name='user_profile'),
    path('api/expenses/', views.api_expenses, name='api_expenses'),
    path('api/invoices/', views.api_invoices, name='api_invoices'),
    path('api/summary/', views.api_dashboard_summary, name='api_summary'),
    
]