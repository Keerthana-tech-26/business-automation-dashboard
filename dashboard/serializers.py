from rest_framework import serializers
from .models import Expense, Invoice
class ExpenseSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Expense
        fields = ['id', 'title', 'amount', 'category', 'category_display', 'date', 'description', 'username', 'created_at']

class InvoiceSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'client_name', 'client_email', 'amount', 'status', 'status_display', 'issue_date', 'due_date', 'created_by_username', 'created_at']