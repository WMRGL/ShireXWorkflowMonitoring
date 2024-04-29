from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib import messages

from .models import STAFF


class ShireBackend(BaseBackend):
    def authenticate(self, pRequest, pUsername=None, pPassword=None):
        _request = pRequest
        _username = pUsername
        _password = pPassword
        _isUserPasswordValid = False

        # Make sure the username and password are both provided
        if _username is None or _password is None:
            return None

        try:
            userValidObj = STAFF.objects.filter(LOGON_NAME = _username, EMPLOYMENT_END_DATE__isnull=True)

            if userValidObj is None:
                return None

            for item in userValidObj:
                # Do the password check separate, because the SQL server comparison
                # is not case-sensitive.  Whereas the code below is!

                if item.PASSWORD == _password:
                    _isUserPasswordValid = True

            if userValidObj.__len__() > 1:
                if _isUserPasswordValid:
                    _errTxt = ' the password is correct for one of them.'
                else:
                    _errTxt = ' the password is incorrect for both of them.'

#               raise ValueError(ShireBackend.authenticate : The system found two active user staff records' + _errTxt)
                raise ValueError('Multiple users')

        except ValueError:
            messages.error(_request, 'There are multiple active user staff records with that username, ' +
                           _errTxt + ' Please see the system administrator.')
            return None

        except Exception:
            return None

        # The following logic is predicated on each user being replicated in
        # the standard Django structure (the User model class)

        if _isUserPasswordValid:
            try:
                # Try to find the user record in the auth_user table
                user = User.objects.get(username = _username)
            except User.DoesNotExist:
                # If not found create a new user. There's no need to set a password
                user = User(username = _username)
                user.is_staff = True
                user.is_superuser = True
                user.save()
            return user

        # Otherwise
        return None

    def get_user(self, pUserId):
        _userId = pUserId
        try:
            return User.objects.get(pk = _userId)
        except User.DoesNotExist:
            return None
