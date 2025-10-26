from django.contrib import admin
from .models import Expense, Invoice, UserProfile

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'category', 'date', 'user', 'created_at']
    list_filter = ['category', 'date', 'user']
    search_fields = ['title', 'description']
    date_hierarchy = 'date'

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client_name', 'amount', 'status', 'issue_date', 'due_date']
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = ['invoice_number', 'client_name', 'client_email']
    date_hierarchy = 'issue_date'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'phone']
    list_filter = ['role']
    search_fields = ['user__username', 'department']