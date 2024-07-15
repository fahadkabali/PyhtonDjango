from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from PIL import Image


# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, fullname, organisation_name, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError(_('The Username field must be set'))
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            fullname=fullname,
            organisation_name=organisation_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, fullname, organisation_name, password=None,**extra_fields):
        user = self.create_user(
            username=username,
            email=email,
            fullname=fullname,
            organisation_name=organisation_name,
            password=password,
            **extra_fields
        )
        
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):

    GENDER = [("M", "Male"), ("F", "Female"), ('O', 'Other')]

    username = models.CharField(max_length=150, unique=True)
    fullname = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    organisation_name = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER, blank=True)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    avatar = models.ImageField(upload_to='profile_images/',default='default.jpg', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    fcm_token = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname', 'organisation_name', 'email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    
#Contact model
class Contact(models.Model):
    name = models.CharField(max_length=110)
    organisation_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    subject = models.CharField(max_length=200)
    message = models.TextField()

    def __str__(self):
        return self.subject
    
class Profile(models.Model):

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.avatar.path)

        if img.height > 100 or img.width > 100:
            new_img = (100, 100)
            img.thumbnail(new_img)
            img.save(self.avatar.path)
