from django.urls import path
from . import views

urlpatterns = [
    path('', views.member_list, name='member_list'),
    
    path('register/', views.register_member, name='register_member'),
    # path('health-log/', views.health_log, name='health_log'),
    path('health-log/<int:id>/', views.member_health, name='member_health'),
    path('payment/<int:id>/', views.payment_history, name='payment_history'),
    path('export-pdf/', views.export_member_pdf, name='export_member_pdf'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
