from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Sum
from .models import Expense, Invoice
from datetime import datetime, timedelta
import csv
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Expense, Invoice, UserProfile
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ExpenseSerializer, InvoiceSerializer

@login_required
def dashboard_home(request):
    today = datetime.today()
    start_of_month = today.replace(day=1)
    total_expenses = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_expenses = Expense.objects.filter(
        user=request.user, 
        date__gte=start_of_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_invoices = Invoice.objects.filter(created_by=request.user).count()
    pending_invoices = Invoice.objects.filter(created_by=request.user, status='SENT').count()
    recent_expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]
    recent_invoices = Invoice.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    
    context = {
        'total_expenses': total_expenses,
        'monthly_expenses': monthly_expenses,
        'total_invoices': total_invoices,
        'pending_invoices': pending_invoices,
        'recent_expenses': recent_expenses,
        'recent_invoices': recent_invoices,
    }
    return render(request, 'dashboard/home.html', context)

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard_home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'dashboard/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    context = {
        'expenses': expenses,
        'total': total,
    }
    return render(request, 'dashboard/expense_list.html', context)

@login_required
def expense_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        date = request.POST.get('date')
        description = request.POST.get('description', '')
        
        Expense.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            category=category,
            date=date,
            description=description
        )
        messages.success(request, 'Expense added successfully!')
        return redirect('expense_list')
    
    return render(request, 'dashboard/expense_form.html')

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    messages.success(request, 'Expense deleted successfully!')
    return redirect('expense_list')

@login_required
def invoice_list(request):
    invoices = Invoice.objects.filter(created_by=request.user).order_by('-created_at')
    total_amount = invoices.aggregate(Sum('amount'))['amount__sum'] or 0
    context = {
        'invoices': invoices,
        'total_amount': total_amount,
    }
    return render(request, 'dashboard/invoice_list.html', context)

@login_required
def invoice_create(request):
    if request.method == 'POST':
        invoice_number = request.POST.get('invoice_number')
        client_name = request.POST.get('client_name')
        client_email = request.POST.get('client_email')
        amount = request.POST.get('amount')
        status = request.POST.get('status')
        issue_date = request.POST.get('issue_date')
        due_date = request.POST.get('due_date')
        description = request.POST.get('description')
        
        Invoice.objects.create(
            invoice_number=invoice_number,
            client_name=client_name,
            client_email=client_email,
            amount=amount,
            status=status,
            issue_date=issue_date,
            due_date=due_date,
            description=description,
            created_by=request.user
        )
        messages.success(request, 'Invoice created successfully!')
        return redirect('invoice_list')
    
    return render(request, 'dashboard/invoice_form.html')

@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, created_by=request.user)
    invoice.delete()
    messages.success(request, 'Invoice deleted successfully!')
    return redirect('invoice_list')

@login_required
def financial_reports(request):
    from django.db.models import Count
    from datetime import date
    import json
    expense_by_category = Expense.objects.filter(user=request.user).values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    invoice_by_status = Invoice.objects.filter(created_by=request.user).values('status').annotate(
        total=Sum('amount'),
        count=Count('id')
    )
    today = date.today()
    monthly_data = []
    for i in range(5, -1, -1):
        month = today.month - i
        year = today.year
        if month <= 0:
            month += 12
            year -= 1
        
        month_expenses = Expense.objects.filter(
            user=request.user,
            date__month=month,
            date__year=year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        month_invoices = Invoice.objects.filter(
            created_by=request.user,
            issue_date__month=month,
            issue_date__year=year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        monthly_data.append({
            'month': date(year, month, 1).strftime('%b %Y'),
            'expenses': float(month_expenses),
            'invoices': float(month_invoices)
        })
    
    context = {
        'expense_by_category': expense_by_category,
        'invoice_by_status': invoice_by_status,
        'monthly_data_json': json.dumps(monthly_data),
    }
    return render(request, 'dashboard/reports.html', context)
@login_required
def export_expenses_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Title', 'Amount', 'Category', 'Date', 'Description', 'Created At'])
    
    expenses = Expense.objects.filter(user=request.user).values_list(
        'title', 'amount', 'category', 'date', 'description', 'created_at'
    )
    
    for expense in expenses:
        writer.writerow(expense)
    
    return response

@login_required
def export_invoices_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="invoices.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Invoice Number', 'Client Name', 'Client Email', 'Amount', 'Status', 'Issue Date', 'Due Date', 'Description'])
    
    invoices = Invoice.objects.filter(created_by=request.user).values_list(
        'invoice_number', 'client_name', 'client_email', 'amount', 'status', 'issue_date', 'due_date', 'description'
    )
    
    for invoice in invoices:
        writer.writerow(invoice)
    
    return response
@login_required
def user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile.department = request.POST.get('department', '')
        profile.phone = request.POST.get('phone', '')
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')
    
    context = {
        'profile': profile,
    }
    return render(request, 'dashboard/profile.html', context)

@api_view(['GET'])
def api_expenses(request):
    expenses = Expense.objects.all()
    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_invoices(request):
    invoices = Invoice.objects.all()
    serializer = InvoiceSerializer(invoices, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_dashboard_summary(request):
    from django.db.models import Sum, Count
    
    total_expenses = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_invoices = Invoice.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    
    expense_by_category = list(Expense.objects.values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ))
    
    invoice_by_status = list(Invoice.objects.values('status').annotate(
        total=Sum('amount'),
        count=Count('id')
    ))
    
    return Response({
        'total_expenses': float(total_expenses),
        'total_invoices': float(total_invoices),
        'expense_by_category': expense_by_category,
        'invoice_by_status': invoice_by_status,
    })
@login_required
def bulk_import_expenses(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('bulk_import_expenses')
        
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            success_count = 0
            error_count = 0
            
            for row in reader:
                try:
                    Expense.objects.create(
                        user=request.user,
                        title=row['title'],
                        amount=float(row['amount']),
                        category=row['category'],
                        date=row['date'],
                        description=row.get('description', '')
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Error importing row: {e}")
            
            messages.success(request, f'Successfully imported {success_count} expenses. {error_count} errors.')
            return redirect('expense_list')
            
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            return redirect('bulk_import_expenses')
    
    return render(request, 'dashboard/bulk_import_expenses.html')

@login_required
def bulk_import_invoices(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('bulk_import_invoices')
        
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            success_count = 0
            error_count = 0
            
            for row in reader:
                try:
                    Invoice.objects.create(
                        created_by=request.user,
                        invoice_number=row['invoice_number'],
                        client_name=row['client_name'],
                        client_email=row['client_email'],
                        amount=float(row['amount']),
                        status=row['status'],
                        issue_date=row['issue_date'],
                        due_date=row['due_date'],
                        description=row.get('description', '')
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Error importing row: {e}")
            
            messages.success(request, f'Successfully imported {success_count} invoices. {error_count} errors.')
            return redirect('invoice_list')
            
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            return redirect('bulk_import_invoices')
    
    return render(request, 'dashboard/bulk_import_invoices.html')