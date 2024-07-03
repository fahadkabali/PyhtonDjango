from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

class EmailBackend(BaseBackend):
    model = get_user_model()
    def authenticate(
        self, request = None, email=None, password=None):
        try:
            user = self.model.objects.get(email=email)
        except self.model.DoesNotExist:
            return None
        if self.model.check_password(password) and user is not None:
            return user

    def get_user(self, user_id):
        try:
            return self.model.objects.get(pk=user_id)
        except self.model.DoesNotExist:
            return None