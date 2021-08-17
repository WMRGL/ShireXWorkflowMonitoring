from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import STAFF

class ShireBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        _isUserPasswordValid = False

        #Make sure the username and password are both provided
        if username==None or password==None:
            return None

        try:
            userValidObj = STAFF.objects.get(LOGON_NAME=username)

            #Do the password check separate, because the SQL server comparison
            #is not case sensitive.  Whereas the code below is!
            if userValidObj.PASSWORD == password:
                _isUserPasswordValid = True

        except Exception as ex:
            return None

        #The following logic is predicated on each user being replicated in
        #the standard Django structure (the User model class)

        if _isUserPasswordValid == True:
            try:
                #Try to find the user record in the auth_user table
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # If not found create a new user. There's no need to set a password
                user = User(username=username)
                user.is_staff = True
                user.is_superuser = True
                user.save()
            return user

        #Otherwise
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None