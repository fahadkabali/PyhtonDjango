
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from CSAT import settings
from .forms import LoginForm, SignUpForm
from django.urls import reverse_lazy
from . tokens import generate_token
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
# from . models import Profile
# from . forms import ProfilePictureForm
from django.conf import settings
# from .models import User




def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            fullname = form.cleaned_data.get("fullname")
            organisation_name = form.cleaned_data.get("organisation_name")
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password1 = form.cleaned_data.get("password1")
            password2 = form.cleaned_data.get("password2")

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists! Please try a different username.")
                return redirect('register')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists! Please use a different email address.")
                return redirect('register')

            if len(username) > 15:
                messages.error(request, "Username must be under 15 characters.")
                return redirect('register')

            if password1 != password2:
                messages.error(request, "Passwords do not match.")
                return redirect('register')

            if not username.isalnum():
                messages.error(request, "Username must be alphanumeric.")
                return redirect('register')

            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password1, fullname=fullname, organisation_name=organisation_name)
            user.is_active = False
            user.save()

            # Send email confirmation
            subject = "Welcome to Login!!"
            message = f"Hello {user.username}!! \nWelcome!! \nThank you for visiting our website.\nWe have also sent you a confirmation email, please confirm your email address.\n\nThanking You"
            from_email = settings.EMAIL_HOST_USER
            to_list = [user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)

            # Email Address Confirmation Email
            current_site = get_current_site(request)
            email_subject = "Confirm your Email for Login!!"
            message2 = render_to_string('email_confirmation.html', {
                'name': user.username,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user)
            })
            email = EmailMessage(
                email_subject,
                message2,
                from_email,
                to_list,
            )
            email.send(fail_silently=True)

            messages.success(request, "Your Account has been created successfully!! Please check your email to confirm your email address in order to activate your account.")
            return redirect("/login/")
        else:
            messages.error(request, 'Form is not valid')
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('login')
    else:
        return render(request, 'accounts/activation_failed.html')
    

# def register_user(request):
#     msg = None
#     success = False

#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             email = form.cleaned_data.get("email")
#             raw_password = form.cleaned_data.get("password1")
#             user = authenticate(email=email, password=raw_password)

#             msg = 'User created - please <a href="/login">login</a>.'
#             success = True

#             return redirect("/login/")

#         else:
#             msg = 'Form is not valid'
#     else:
#         form = SignUpForm()

#     return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})

# def activate(request,uidb64,token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         myuser = User.objects.get(pk=uid)
#     except (TypeError,ValueError,OverflowError,User.DoesNotExist):
#         myuser = None

#     if myuser is not None and generate_token.check_token(myuser,token):
#         myuser.is_active = True
#         # user.profile.signup_confirmation = True
#         myuser.save()
#         login(request,myuser)
#         messages.success(request, "Your Account has been activated!!")
#         return redirect('login')
#     else:
#         return render(request,'accounts/activation_failed.html')
    

def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                username=user.username
                return redirect("/")
            else:
                messages.error(request,'Invalid credentials')
                return redirect("login")
        else:
            messages.error(request,'Error validating the form')
            return redirect("login")

    return render(request, "accounts/login.html", {"form": form, "msg": msg})

def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login/")