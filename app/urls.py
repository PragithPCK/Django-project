from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
     path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path("contact/", views.contact_view, name="contact"),

    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('package/add/', views.add_package, name='add_package'),
    path('package/<int:pk>/edit/', views.edit_package, name='edit_package'),
    path('package/<int:pk>/', views.package_detail, name='package_detail'),
   
    path('package/<int:package_id>/pay/', views.make_payment, name='make_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)