from django.shortcuts import render, redirect, get_object_or_404
from .models import Member, HealthLog
from .forms import MemberForm, HealthLogForm,PaymentForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from plyer import notification
from datetime import date, timedelta
from .models import Payment
from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required, user_passes_test


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
        # notification.notify(
        #     title='Fee Due Alert',
        #     message=message,
        #     timeout=5
        # )
        messages.warning(request,message)


def member_list(request):
    check_due_dates(request)
    members = Member.objects.all()
    return render(request, 'member_list.html', {'members': members})


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


# @login_required
# @user_passes_test(is_admin)
# def health_log(request):
#     if request.method == 'POST':
#         form = HealthLogForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('health_log')
#     else:
#         form = HealthLogForm()
    
#     health_logs = HealthLog.objects.select_related('member').all()
#     return render(request, 'health_log.html', {'form': form, 'health_logs': health_logs})


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
