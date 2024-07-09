from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
import requests
from . import constants
from django.db import transaction
from django.contrib.auth.models import Group
from .models import Learner
from django.db.utils import IntegrityError

UserModel = get_user_model()


class GoogleSignInBackend(BaseBackend):
    """Custom Backend Server for Google auth"""
    def _get_access_token(self, code):
        """
        Return access_toke from code
        :param code: google Code from callback
        :return: User Instance
        """

        response = requests.post('https://oauth2.googleapis.com/token', data={
            "code": code,
            "client_id": constants.GOOGLE_CLIENT_ID,
            'client_secret': constants.GOOGLE_CLIENT_SECRET,
            "redirect_uri": constants.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        })
        return response.json().get('access_token')

    def get_user(self, pk):
        """Returns a user instance """
        try:
            return UserModel.objects.get(pk=pk)
        except UserModel.DoesNotExist:
            return None

    def authenticate(self, request, code=None, **kwargs):
        """
        Authentication function for Custom google token verification
        parms:
            code - Google code received form view
        """
        if code:
            access_token = self._get_access_token(code)
            if access_token:
                google_user_details = requests.get(f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}')
                print(f'Google User Details: {google_user_details.json()}')
                email = google_user_details.json().get('email')
                try:
                    user = UserModel.objects.get(username=email)
                    return user
                except UserModel.DoesNotExist:
                   return  None

class GoogleSignUpBackend(BaseBackend):
    """Custom Backend Server for Google auth signup"""
    def _get_access_token(self, code):
        response = requests.post('https://oauth2.googleapis.com/token', data={
            "code": code,
            "client_id": constants.GOOGLE_CLIENT_ID,
            'client_secret': constants.GOOGLE_CLIENT_SECRET,
            "redirect_uri": constants.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        })
        return response.json().get('access_token')

    def get_user(self, pk):
        try:
            return UserModel.objects.get(pk=pk)
        except UserModel.DoesNotExist:
            return None

    def authenticate(self, request, code=None, **kwargs):
        """Authenticates the user based on the Google authorization code."""
        if not code:
            return None

        try:
            access_token = self._get_access_token(code)
        except requests.exceptions.RequestException:  # Catch network or other errors
            return None

        google_user_details = requests.get(
            f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}'
        )

        if google_user_details.status_code != 200:
            return None  # Error fetching user details

        user_data = google_user_details.json()
        email = user_data.get('email')
        if not email:
            return None

        # Check if user with this email already exists
        if UserModel.objects.filter(email=email).exists():
            return None  # Don't proceed if the email is already registered

        try:
            with transaction.atomic():
                user = UserModel.objects.create_user(username=email, email=email)
                user.is_active = True
                user.save()

                group, _ = Group.objects.get_or_create(name='learner')
                user.groups.add(group)
                Learner.objects.create(user=user)
            return user
        except IntegrityError:
            # Handle potential unique constraint violations
            return None