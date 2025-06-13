from django.contrib import admin
from .models import Package, Booking, Profile, Contact

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor', 'is_approved']
    list_editable = ['is_approved']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'payment_status', 'razorpay_order_id','booking_date')  # Customize fields as needed
    search_fields = ('name', 'package')               # Optional: adds search box
    list_filter = ('booking_date',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'message', 'email', 'created_at')  # Customize fields as needed
    search_fields = ('name', 'email')               # Optional: adds search box
    list_filter = ('created_at',) 



# Register your models here.



