
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from CSAT import settings
from .forms import LoginForm, SignUpForm
from django.urls import reverse, reverse_lazy
from . tokens import generate_token
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.contrib.auth.views import PasswordResetView, PasswordChangeView
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from .forms import *
from .models import *
import csv


User = get_user_model()


#registration account view
@csrf_protect
def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            fullname = form.cleaned_data.get("fullname")
            organisation_name = form.cleaned_data.get("organisation_name")
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password1 = form.cleaned_data.get("password1")
            password2 = form.cleaned_data.get("password2")
            agree_to_privacy_policy = form.cleaned_data.get("agree_to_privacy_policy")

            
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
            try:
                user = User.objects.create_user(username=username, email=email, password=password1, fullname=fullname, organisation_name=organisation_name)
                user.is_active = False
                user.save()
            except IntegrityError:
                messages.error(request, "An error occurred during registration. Please try again.")
                return redirect('register')
            
            if not agree_to_privacy_policy:
                messages.error(request, "You must agree to the Privacy Policy.")
                return redirect('register')

            subject = "Welcome to Login!!"
            message = f"Hello {user.username}!! \nWelcome!! \nThank you for visiting our website.\nWe have also sent you a confirmation email, please confirm your email address.\n\nThanking You"
            from_email = settings.EMAIL_HOST_USER
            to_list = [user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)

            current_site = get_current_site(request)
            email_subject = "Confirm your Email for Login!!"
            message2 = render_to_string('accounts/email_confirmation.html', {
                'name': user.username,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user)
            })
            email = EmailMessage(email_subject, message2, from_email, to_list)
            email.send(fail_silently=True)

            messages.success(request, "Your Account has been created successfully!! Please check your email to confirm your email address in order to activate your account.")
            return redirect("authentication:login")
        else:
            messages.error(request, 'Form is not valid')
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form})

#view for account activation
@csrf_protect
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        backend = settings.AUTHENTICATION_BACKENDS[0]
        myuser.backend = backend
        login(request, myuser, backend=backend)
        messages.success(request, "Your Account has been activated!!")
        return redirect('authentication:login')
    else:
        return render(request, 'accounts/activation_failed.html')

#login view for registered users
@csrf_protect
def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            remember_me = form.cleaned_data.get("remember_me")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                messages.error(request, 'Invalid credentials')
                return redirect("authentication:login")
        else:
            messages.error(request, 'Error validating the form')
            return redirect("authentication:login")

    return render(request, "accounts/login.html", {"form": form})

# logout view for users

@login_required
def user_logout(request):
    if request.method == 'POST':
        if 'confirm' in request.POST:
            logout(request)
            messages.success(request, "Logged out successfully!")
            return redirect('authentication:login')
        elif 'cancel' in request.POST:
            messages.info(request, "Logout cancelled.")
            return redirect('authentication:profile') 
    return render(request, 'accounts/logout_confirm.html')


# def profile_view(request):
#     user = get_object_or_404(CustomUser, pk=request.user.pk)
#     form = UserProfileForm(request.POST or None, request.FILES or None, instance=user)
#     context = {'form': form, 'page_title': 'View/Edit Profile'}

#     if request.method == 'POST':
#         try:
#             if form.is_valid():
#                 first_name = form.cleaned_data.get('first_name')
#                 last_name = form.cleaned_data.get('last_name')
#                 username = form.cleaned_data.get('username')
#                 organisation_name = form.cleaned_data.get('organisation_name')
#                 bio = form.changed_data.get('bio')
#                 # password = form.cleaned_data.get('password') or None
#                 address = form.cleaned_data.get('address')
#                 gender = form.cleaned_data.get('gender')
#                 profile_pic = request.FILES.get('profile_pic') or None
                
#                 # if password:
#                 #     user.set_password(password)
#                 if profile_pic:
#                     fs = FileSystemStorage()
#                     filename = fs.save(profile_pic.name, profile_pic)
#                     profile_pic_url = fs.url(filename)
#                     user.profile_pic = profile_pic_url

#                 user.first_name = first_name
#                 user.last_name = last_name
#                 user.username = username
#                 user.organisation_name = organisation_name
#                 user.address = address
#                 user.gender = gender
#                 user.bio = bio
#                 user.save()
                
#                 messages.success(request, "Your profile has been updated successfully!.")
#                 return redirect(reverse('authentication:profile'))
#             else:
#                 messages.error(request, "Invalid Data Provided")
#         except Exception as e:
#             messages.error(request, "Error Occurred While Updating Profile " + str(e))

#     context = {'form': form, 'user': request.user}
#     return render(request, 'accounts/profile.html', context)


#view for the profile editing and view
@csrf_protect
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('authentication:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})



#view for deleting user account
@login_required
def delete_account_view(request):
    if request.method == 'POST':
        form = AccountDeletionForm(request.POST)
        if 'confirm' in request.POST:
            user = request.user
            user.delete()
            logout(request)
            messages.success(request, "Your account has been deleted.")
            return redirect('authentication:register')
        elif 'cancel' in request.POST:
            messages.info(request, "Delete cancelled.")
            return redirect('authentication:profile') 
    else:
        form = AccountDeletionForm()

    return render(request, 'accounts/delete_account.html', {'form': form})

###########################################################################
#############################password reset################################
###########################################################################
def reset_password_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='registration/password_reset_email.html',
                subject_template_name='registration/password_reset_subject.txt',
            )
            messages.success(
                request, 
                "We've emailed you instructions for setting your password, if an account exists with the email you entered. You should receive them shortly. If you don't receive an email, please make sure you've entered the address you registered with, and check your spam folder."
            )
            return redirect('home')
    else:
        form = PasswordResetForm()

    return render(request, 'registration/password_reset.html', {'form': form})

###############################################################################
##########################password change view#################################
###############################################################################

@login_required
def change_password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("authentication:profile")
        else:
            messages.error(request, "Please correct the error(s) below. ")
    else:
        form = PasswordChangeForm(request.user)
    return render(
        request,
        "registration/change_password.html",
        {
            "form": form,
        },
    )
# def change_password_view(request):
#     if request.method == 'POST':
#         form = ChangePasswordForm(request.user, request.POST)
#         if form.is_valid():
#             try:
#                 user = form.save()
#                 update_session_auth_hash(request, user)  # Important to prevent the user from being logged out
#                 messages.success(request, 'Successfully Changed Your Password')
#                 return redirect('authentication:profile')
#             except Exception as e:
#                 messages.error(request, f'An error occurred: {str(e)}')
#     else:
#         form = ChangePasswordForm(request.user)
    
#     return render(request, 'registration/change_password.html', {'form': form})

#contact form view
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save() 
            name = form.cleaned_data['name']
            email_subject = f'New contact {form.cleaned_data["email"]}: {form.cleaned_data["subject"]}'
            organisation_name=form.cleaned_data['organisation_name']
            email_message = form.cleaned_data['message']
            EmailMessage(
               'Contact Form Submission from {}'.format(name),
               organisation_name,
               email_message,
               'fahadkabali.netfliy.app',
               ['kabalifahad@gmail.com'], 
               [],
               reply_to=[email_subject] 
           ).send()
            # send_mail(
            #     name,
            #     organisation_name,
            #     email_subject,
            #     email_message,
            #     settings.EMAIL_HOST_USER, 
            #     [settings.EMAIL_RECEIVING_USER], 
            #     fail_silently=False
            # )
            return render(request, 'contact/success.html')
    else:
        form = ContactForm() 

    context = {'form': form}
    return render(request, 'contact/contact.html', context)