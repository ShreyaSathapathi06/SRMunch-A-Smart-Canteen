from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

# ------------------------
# SIGNUP
# ------------------------
def student_signup(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        full_name = request.POST.get("full_name", "").strip()

        # SRM email validation
        if not email.endswith("@srmist.edu.in"):
            request.session["signup_error"] = "Only @srmist.edu.in email allowed"
            return redirect("student_signup")

        # Password length check
        if len(password) < 8:
            request.session["signup_error"] = "Password must be at least 8 characters"
            return redirect("student_signup")

        # Password match
        if password != confirm_password:
            request.session["signup_error"] = "Passwords do not match"
            return redirect("student_signup")

        # Check if user exists
        if User.objects.filter(username=email).exists():
            request.session["signup_error"] = "Email already registered"
            return redirect("student_signup")

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        user.studentprofile.full_name = request.POST.get("full_name", "")
        user.studentprofile.save()


        return redirect("student_login")

    # GET → pop error from session
    error = request.session.pop("signup_error", None)
    return render(request, "accounts/signup.html", {"error": error})



# ------------------------
# LOGIN
# ------------------------
def student_login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        # SRM email validation
        if not email.endswith("@srmist.edu.in"):
            request.session["login_error"] = "Only @srmist.edu.in email allowed"
            return redirect("student_login")

        # Password length check
        if len(password) < 8:
            request.session["login_error"] = "Password must be at least 8 characters"
            return redirect("student_login")

        # Authenticate
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect("menu")  # Replace with actual home page
        else:
            request.session["login_error"] = "Invalid email or password"
            return redirect("student_login")

    error = request.session.pop("login_error", None)
    return render(request, "accounts/login.html", {"error": error})


# ------------------------
# LOGOUT
# ------------------------
def student_logout(request):
    logout(request)
    return redirect("student_login")


# ------------------------
# SET NEW PASSWORD
# ------------------------
def set_new_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return redirect("student_login")

    if request.method == "POST":
        new_password = request.POST.get("new_password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        if new_password != confirm_password:
            return render(request, "accounts/password_reset_confirm.html", {"error": "Passwords do not match"})

        if len(new_password) < 8:
            return render(request, "accounts/password_reset_confirm.html", {"error": "Password must be at least 8 characters"})

        # Save password
        user.set_password(new_password)
        user.save()
        return redirect("student_login")

    return render(request, "accounts/password_reset_confirm.html")
from django.contrib.auth.decorators import login_required
from .models import StudentProfile
from .forms import StudentProfileForm

@login_required
def edit_profile(request):
    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        form = StudentProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )
        if form.is_valid():
            form.save()
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {
        'form': form,
        'profile': profile
    })
