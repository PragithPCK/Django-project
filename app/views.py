from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, PackageForm
from .models import Package, Booking, Profile, Contact
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
import razorpay
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

def home(request):
    packages = Package.objects.filter(is_approved=True)
    return render(request, 'home.html', {'packages': packages})

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            # Check role from Profile
            role = user.profile.role
            if role == 'vendor':
                return redirect('vendor_dashboard')
            else:
                return redirect('user_dashboard')

        else:
            return render(request, 'registration/login.html', {"error": "Invalid credentials"})

    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def user_dashboard(request):
    packages = Package.objects.filter(is_approved=True)
    return render(request, 'user_dashboard.html', {'packages': packages})

@login_required
def vendor_dashboard(request):
    packages = Package.objects.filter(vendor=request.user)
    return render(request, 'vendor_dashboard.html', {'packages': packages})

@login_required
def add_package(request):
    if request.method == "POST":
        form = PackageForm(request.POST,request.FILES)
        if form.is_valid():
            package = form.save(commit=False)
            package.vendor = request.user
            package.save()
            return redirect('vendor_dashboard')
    else:
        form = PackageForm()
    return render(request, 'add_package.html', {'form': form})

@login_required
def edit_package(request, pk):
    pkg = get_object_or_404(Package, pk=pk)
    if request.method == "POST":
        form = PackageForm(request.POST, instance=pkg)
        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')
    else:
        form = PackageForm(instance=pkg)
    return render(request, 'edit_package.html', {'form': form})

def package_detail(request, pk):
    package = get_object_or_404(Package, pk=pk)
    return render(request, 'package_detail.html', {'package': package})

@login_required
def make_payment(request, package_id):
    package = get_object_or_404(Package, id=package_id, is_approved=True)

    if request.method == "POST":
        try:
            print("RAZORPAY_KEY_ID:", settings.RAZORPAY_KEY_ID)
            print("RAZORPAY_SECRET_KEY:", settings.RAZORPAY_SECRET_KEY)

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

            payment = client.order.create({
                "amount": int(package.price * 100),
                "currency": "INR",
                "payment_capture": "1"
            })

            # Store the order in session to use in confirmation
            request.session['razorpay_order_id'] = payment['id']
            request.session['package_id'] = package.id

            return render(request, "payment.html", {
                "payment": payment,
                "package": package,
                "razorpay_key": settings.RAZORPAY_KEY_ID
            })

        except razorpay.errors.BadRequestError as e:
            print("Razorpay BadRequestError:", str(e))
            return HttpResponse(f"Payment failed: {str(e)}", status=400)
        except Exception as e:
            print("Unexpected Razorpay Error:", str(e))
            return HttpResponse(f"Internal error: {str(e)}", status=500)

    return render(request, "payment.html", {
        "package": package,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    })

def contact_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        contact = Contact(name=name, email=email, message=message)
        contact.save()
        messages.success(request, 'Your message has been sent!')

        return redirect('login')
        # You can process/store/send the data here
    return render(request, 'contact.html')


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        # Extract data from Razorpay's POST request
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Create dict for signature verification
        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        # Razorpay client instance
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

        try:
            # Verify the signature using Razorpay utility
            client.utility.verify_payment_signature(params_dict)

            # If signature is valid, update your database
            package_id = request.session.get('package_id')
            user = request.user

            if package_id and user.is_authenticated:
                package = Package.objects.get(id=package_id)
                Booking.objects.create(
                    user=user,
                    package=package,
                    payment_id=razorpay_payment_id,
                    payment_status="Success"
                )
                return HttpResponse("Payment successful and booking saved.")
            else:
                return HttpResponseBadRequest("Invalid session or user not authenticated.")

        except razorpay.errors.SignatureVerificationError:
            return HttpResponseBadRequest("Signature verification failed.")
    else:
        return HttpResponseBadRequest("Invalid request method.")


    
