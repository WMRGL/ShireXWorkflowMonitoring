#Add any classes or functions that are commonly used, but which are not
#workflow based.

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.urls import reverse
from django.views.generic import TemplateView
from ShireXWorkflowMonitoring.apps import ShireXWorkflowMonitoringConfig
from datetime import datetime
from enum import Enum

class Login(TemplateView):

    template_name = "Login.html"
    title = ShireXWorkflowMonitoringConfig.title

    def get(self, request):
        _context = {
            "Title": self.title,
        }
        return render(request, self.template_name, _context)

    def post(self, request):
        try:
            _username = request.POST["txtUsername"]
            _password = request.POST["txtPassword"]

            user = authenticate(request, username=_username, password=_password)

            if user is not None:
                login(request, user)

                return HttpResponseRedirect(reverse('StartPage'))
            else:
                #Otherwise, return with failure message

                _context = {
                    "Title": self.title,
                    "error_message": "The username or password are not valid",
                }

                return render(request, self.template_name, _context)

        except Exception as ex:
            # Redisplay the login screen
            _context = {
                "Title": self.title,
                "error_message": "The username or password are not valid with error message " + str(ex)
            }

            return render(request, self.template_name, _context)

class Start(TemplateView):

    template_name = "Start.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('LoginPage'))
        else:
            _context = None
            return render(request, self.template_name, _context)

class Authenticate():
    def DoLogout(request):
        logout(request)

        return HttpResponseRedirect(reverse('LoginPage'))

class enumDataType(Enum):
    String="string",
    Integer="integer",
    Float="float",
    Datetime="datetime",
    Boolean="boolean"

class UtilityFunctions():
    def GetRequestKey(self, request, keyName, dataType):
        for _key in request.GET:
            if _key == keyName:

                _strVal = request.GET[_key]

                if dataType == enumDataType.Datetime:
                    return datetime.strptime(_strVal, '%Y-%m-%d')  # IMPORTANT..The format string is different to a template filter and is specific!

                if dataType == enumDataType.Integer:
                    return int(_strVal)

                if dataType == enumDataType.Float:
                    return float(_strVal)

                if dataType == enumDataType.Boolean:
                    if _strVal.upper() == "TRUE":
                        return True
                    if _strVal.upper() == "FALSE":
                        return False
                return _strVal

        return ""

    def ConvertCursorListToDict(self, cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

