from django.shortcuts import render, redirect, get_object_or_404
from .models import Member, HealthLog
from .forms import MemberForm, HealthLogForm,PaymentForm
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, F, ExpressionWrapper, fields, OuterRef, Subquery, Max
from django.contrib import messages
from datetime import date, timedelta
from .models import Payment
from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods


def is_admin(user):
    return user.is_staff


def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('member_list')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'registration/login.html')


@login_required
@user_passes_test(is_admin)
def export_member_pdf(request):
    members = Member.objects.all()
    html = render_to_string('member_pdf.html', {'members': members})
    pdf = HTML(string=html).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="members_report.pdf"'
    return response

def check_due_dates(request):
    upcoming_payments = Payment.objects.filter(due_date__lte=date.today())
    for payment in upcoming_payments:
        payment.update_status
        message=f"Payment due for {payment.member.name} on {payment.due_date}"
        messages.warning(request,message)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def edit_member(request,id):
    member = get_object_or_404(Member, pk=id)
 
    if request.method == 'POST':
        # Update member details based on form submission
        member.name = request.POST.get('name', member.name)
        member.contact_number = request.POST.get('contact_number', member.contact_number)
        join_date = request.POST.get('join_date')
        member.join_date = join_date if join_date else member.join_date

        # Update age by adjusting the date of birth
        age = request.POST.get('age')
        if age:
            member.date_of_birth = date.today().replace(year=date.today().year - int(age))
        
        if 'profile_photo' in request.FILES:
            member.profile_photo = request.FILES['profile_photo']
        
        member.save()
        messages.success(request, 'Member details updated successfully!')
        return redirect('member_list')

    return render(request, 'edit_member.html', {'member': member})


def member_list(request):
    # check_due_dates(request)
    
    # Fetch all members
    members = Member.objects.all()
    
    # Get query parameters for search, sort, and filters
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort_by', 'join_date')
    gender_filter = request.GET.get('gender')
    status_filter = request.GET.get('status')


    # Calculate age based on birthdate
    members = members.annotate(
        age=ExpressionWrapper(
            date.today().year - F('birthdate__year'),
            output_field=fields.IntegerField()
        )
    )
    
    # Search by name or contact number
    if search_query:
        members = members.filter(Q(name__icontains=search_query) | Q(contact_number__icontains=search_query))
    
    # Filter by gender
    if gender_filter:
        members = members.filter(gender=gender_filter)
    
    # Filter by payment status (Paid/Unpaid)
    latest_payment_status = Payment.objects.filter(member=OuterRef('pk')).order_by('-due_date').values('status')[:1]

    if status_filter == 'Paid':
        members = members.annotate(latest_status=Subquery(latest_payment_status)).filter(latest_status='Paid')
    elif status_filter == 'Unpaid':
        members = members.annotate(latest_status=Subquery(latest_payment_status)).filter(latest_status='Unpaid')

    # Sorting
    if sort_by == 'name':
        members = members.order_by('name')
    elif sort_by == 'age':
        members = members.order_by('age')
    else:
        members = members.order_by('-join_date')  # Default sort by join_date (newest first)
    
    return render(request, 'member_list.html', {'members': members, 'search_query': search_query, 'sort_by': sort_by, 'gender_filter': gender_filter, 'status_filter': status_filter})

@login_required
@user_passes_test(is_admin)
def register_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'member_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def member_health(request, id):
    member = get_object_or_404(Member, id=id)
    health_logs = HealthLog.objects.filter(member=member).order_by('-date_logged')

    if request.method == 'POST':
        form = HealthLogForm(request.POST)
        if form.is_valid():
            health_log = form.save(commit=False)
            health_log.member = member
            health_log.save()
            return redirect('member_health', id=member.id)
    else:
        form = HealthLogForm()

    return render(request, 'member_health.html', {
        'member': member,
        'health_logs': health_logs,
        'form': form
    })


@login_required
@user_passes_test(is_admin)
def payment_history(request, id):
    member = get_object_or_404(Member, id=id)
    payments = Payment.objects.filter(member=member).order_by('-date_paid')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.member = member
            payment.save()
            return redirect('payment_history', id=member.id)
    else:
        form = PaymentForm(initial={'member': member})

    return render(request, 'payment_history.html', {'member': member, 'payments': payments, 'form': form})
