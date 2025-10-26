from django.db import models
from django.contrib.auth.models import User
class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('OFFICE', 'Office Supplies'),
        ('TRAVEL', 'Travel'),
        ('UTILITIES', 'Utilities'),
        ('SALARY', 'Salary'),
        ('MARKETING', 'Marketing'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - ₹{self.amount}"
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    issue_date = models.DateField()
    due_date = models.DateField()
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.client_name}"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('EMPLOYEE', 'Employee'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"