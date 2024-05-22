# Add any classes or functions that are commonly used, but which are not
# workflow based.

from datetime import datetime
from enum import Enum

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from ShireXWorkflowMonitoring.apps import ShireXWorkflowMonitoringConfig


# Class for handling login functionality - MW
class Login(TemplateView):
    # Set the template to be used for the login view - MW
    template_name = "Login.html"
    # Set the page title using the app's configuration - MW
    title = ShireXWorkflowMonitoringConfig.title

    # Handle GET requests - Display the login form - MW
    def get(self, pRequest):
        _request = pRequest
        _context = {
            "Title": self.title,
        }
        return render(_request, self.template_name, _context)

    # Handle POST requests - Process login data - MW
    def post(self, pRequest):
        _request = pRequest
        try:
            # Extract username and password from the request - MW
            _username = _request.POST["txtUsername"]
            _password = _request.POST["txtPassword"]

            # Authenticate the user - MW
            user = authenticate(_request, username=_username, password=_password)

            if user is not None:
                # If authentication is successful, log the user in and redirect to the start page - MW
                login(_request, user)

                return HttpResponseRedirect(reverse('StartPage'))
            else:
                # If authentication fails, show an error message - MW
                # Otherwise, return with failure message

                _context = {
                    "Title": self.title,
                    "error_message": "The username or password are not valid",
                }

                return render(_request, self.template_name, _context)

        except Exception as ex:
            # Handle any exceptions and show an error message - MW
            # Redisplay the login screen
            _context = {
                "Title": self.title,
                "error_message": "The username or password are not valid with error message " + str(ex)
            }

            return render(_request, self.template_name, _context)


# Class for the Start page view - MW
class Start(TemplateView):

    template_name = "Start.html"

    # Handle GET requests - Show the Start page only if user is authenticated - MW
    def get(self, pRequest):
        _request = pRequest

        if not _request.user.is_authenticated:
            # Redirect unauthenticated users to the login page - MW
            return HttpResponseRedirect(reverse('LoginPage'))
        else:
            _context = None

            return render(_request, self.template_name, _context)


# Class for the AllocateComplete page view - MW
class AllocateComplete(TemplateView):

    template_name = "AllocateComplete.html"

    # Handle GET requests - Show this page only if user is authenticated - MW
    def get(self, pRequest):
        _request = pRequest

        if not _request.user.is_authenticated:
            # Redirect unauthenticated users to the login page - MW
            return HttpResponseRedirect(reverse('LoginPage'))
        else:
            _context = None
            return render(_request, self.template_name, _context)



# Class for handling user logout functionality - MW
class Authenticate:
    def DoLogout(pRequest):
        _request = pRequest
        # Log the user out and redirect to the login page - MW
        logout(_request)
        return HttpResponseRedirect(reverse('LoginPage'))

class enumDataType(Enum):
    String = "string",
    Integer = "integer",
    Float = "float",
    Datetime = "datetime",
    Boolean = "boolean"

# Class for utility functions used across the application - MW
class UtilityFunctions:
# Function to get a request parameter value from a GET request and convert it to the specified data type - MW
    def GetRequestKey(self, pRequest, pKeyName, pDataType):
        _request = pRequest
        _keyName = pKeyName
        _dataType = pDataType

        # Loop through all keys in the GET request - MW
        for _key in _request.GET:
            # Convert the string value to the specified data type - mW
            if _key == _keyName:
                _strVal = _request.GET[_key]
                # This try catch block is usd to prevent the "can only concatenate str(not "NoneType") to str" error - MW
                try:
                    if _dataType == enumDataType.Datetime:
                        return datetime.strptime(_strVal, '%Y-%m-%d')
                        # IMPORTANT The format string is different to a template filter and is specific!

                    if _dataType == enumDataType.Integer:
                        return int(_strVal)

                    if _dataType == enumDataType.Float:
                        return float(_strVal)

                    if _dataType == enumDataType.Boolean:
                        if _strVal.upper() == "TRUE":
                            return True
                        if _strVal.upper() == "FALSE":
                            return False
                    # Return the converted value - MW
                    return _strVal
                # Return the value "None" rather than a blank string - MW
                except ValueError:
                    return None

        # Return an empty string if the key is not found - MW
        return None

    # Similar function for POST requests - MW
    def PostRequestKey(self, pRequest, pKeyName, pDataType):
        _request = pRequest
        _keyName = pKeyName
        _dataType = pDataType

        # Loop through all keys in the POST request - MW
        for _key in _request.POST:
            if _key == _keyName:
                _strVal = _request.POST[_key]
                try:

                    if _dataType == enumDataType.Datetime:
                        return datetime.strptime(_strVal, '%Y-%m-%d')
                        # IMPORTANT The format string is different to a template filter and is specific!

                    if _dataType == enumDataType.Integer:
                        return int(_strVal)

                    if _dataType == enumDataType.Float:
                        return float(_strVal)

                    if _dataType == enumDataType.Boolean:
                        if _strVal.upper() == "TRUE":
                            return True
                        if _strVal.upper() == "FALSE":
                            return False
                    return _strVal

                except ValueError:
                    return "None"

        return ""

    # Function to convert SQL cursor results to a list of dictionaries for easier access
    def ConvertCursorListToDict(self, pCursor):
        _cursor = pCursor
        # Return all rows from a cursor as a dictionary (rows) of dictionary (columns)
        # Get column names from the cursor description - MW
        columns = [col[0] for col in _cursor.description]
        # Convert each row in the cursor to a dictionary and return as a list - MW
        return [
            dict(zip(columns, row))
            for row in _cursor.fetchall()
        ]