from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, fullname, organisation_name, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            fullname=fullname,
            organisation_name=organisation_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, fullname, organisation_name, password):
        user = self.create_user(
            username=username,
            email=email,
            fullname=fullname,
            organisation_name=organisation_name,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):

    GENDER = [("M", "Male"), ("F", "Female")]

    username = models.CharField(max_length=20, unique=True)
    fullname = models.CharField(max_length=100)
    organisation_name = models.CharField(max_length=100)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField()
    address = models.TextField()
    # fcm_token = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

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
