from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.core.validators import EmailValidator
from django.contrib.auth.forms import PasswordChangeForm




class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control",
                'data-toggle': 'password',
                'id': 'password',
            }
        ))
    remember_me = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'custom-control-input', 'id': 'customCheckRegister'}),
        label='Remember Me',
        required=False
        )


class SignUpForm(UserCreationForm):
    fullname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Full Name",
                "class": "form-control"
            }
        ))
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    organisation_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Organisation Name",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control",
                'data-toggle': 'password',
                'id': 'password'
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control",
                'data-toggle': 'password',
                'id': 'password',
            }
        ))
    agree_to_privacy_policy = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'custom-control-input', 'id': 'customCheckRegister'}),
        label='I agree with the Privacy Policy',
        required=True
    )


    class Meta:
        model = CustomUser
        fields = ('fullname', 'username', 'organisation_name', 'email', 'password1', 'password2')


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(required=True)
    organisation_name = forms.CharField(required=True)
    address = forms.CharField(required=False)
    bio = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    profile_pic = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    def clean_email(self):
        form_email = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=form_email).exists():
                raise forms.ValidationError("The given email is already registered")
        else:  # Update
            db_email = self.Meta.model.objects.get(id=self.instance.pk).admin.email.lower()
            if db_email != form_email:  # There has been changes
                if CustomUser.objects.filter(email=form_email).exists():
                    raise forms.ValidationError("The given email is already registered")

        return form_email

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'organisation_name', 'gender', 'password', 'profile_pic', 'address', 'bio']


#form for editing and updating the user details
class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'profile_pic', 'gender', 'address', 'organisation_name', 'username', 'email', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address':forms.TextInput(attrs={'class':'form-control', 'placeholder' : 'Address'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Bio'}),
            'organisation_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Organisation Name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

class AccountDeletionForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Reason for deleting your account', 'rows': 3}), required=False)
    feedback = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Additional feedback (optional)', 'rows': 3}), required=False)
    confirm_delete = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), required=True)

class UserEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = CustomUser
        fields = CustomUserForm.Meta.fields


#contact form 
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Name'}),
            'organisation_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Organisation Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your message here...'}),
        }
#password reset form 
# class ChangePasswordForm(PasswordChangeForm):
#     class Meta:
#         model = CustomUser
#         fields = ['old_password', 'new_password1', 'new_password2']
    # old_password = forms.CharField(widget=forms.PasswordInput())
    # new_password = forms.CharField(widget=forms.PasswordInput())
    # confirm_password = forms.CharField(widget=forms.PasswordInput())

# class CustomPasswordChangeForm(PasswordChangeForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for fieldname in ['old_password', 'new_password1', 'new_password2']:
#             self.fields[fieldname].help_text = None