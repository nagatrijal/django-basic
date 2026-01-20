from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# LOGIN
def user_login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'login.html')


# LOGOUT
def user_logout(request):
    logout(request)
    return redirect('login')


# SIGNUP WITH EMAIL
def signup(request):
    if request.method == 'POST':
        u = request.POST['username']
        e = request.POST['email']
        p1 = request.POST['password1']
        p2 = request.POST['password2']

        if p1 != p2:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=u).exists():
            messages.error(request, "Username already exists")
        else:
            user = User.objects.create_user(username=u, email=e, password=p1)
            user.save()

            try:
                send_mail(
                    subject="Welcome to Our App",
                    message=f"Hi {u},\n\nYour account has been created successfully.\n\nThank you!",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[e],
                    fail_silently=False,
                )
                messages.success(request, "Account created and email sent!")
            except:
                messages.warning(request, "Account created but email not sent")

            return redirect('login')

    return render(request, 'signup.html')


# DASHBOARD
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


# PROFILE
@login_required
def profile(request):
    if request.method == 'POST':
        request.user.email = request.POST.get('email')
        request.user.save()
        messages.success(request, "Email updated successfully")
    return render(request, 'profile.html')


# CHANGE PASSWORD
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully")
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


# OFFLINE SYNC API WITH MAIL
@csrf_exempt
def sync_users(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        synced = []

        for u in data:
            username = u.get("username")
            email = u.get("email")

            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password="Temp@123"
                )
                synced.append(email)

                try:
                    send_mail(
                        subject="Account Synced",
                        message=f"Hi {username},\n\nYour account was synced from offline mode.\nTemporary Password: Temp@123",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[email],
                        fail_silently=True,
                    )
                except:
                    pass

        return JsonResponse({
            "status": "success",
            "synced_users": synced
        })

    return JsonResponse({
        "message": "This endpoint only accepts POST data from React"
    })
