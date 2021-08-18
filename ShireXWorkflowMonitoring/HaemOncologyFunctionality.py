#Add Haem Onc specific classes in this file
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.urls import reverse
from django.views.generic import TemplateView
from ShireXWorkflowMonitoring.apps import ShireXWorkflowMonitoringConfig
from datetime import datetime
from datetime import timedelta
from ShireXWorkflowMonitoring.CommonFunctionality import UtilityFunctions
from ShireXWorkflowMonitoring.CommonFunctionality import enumDataType
from django.db import connection

class BMTSearch(TemplateView):
    template_name = "BMTSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            #Otherwise
            if request.GET.__len__() == 0:
                _isPostBack = False
            else:
                _isPostBack = True

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=365)
                _dateTo = datetime.today() + timedelta(days=7)
                #_pageNumber = 1
            else:
                _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime)
                _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime)
                # _pageNumber = self.utilities.GetRequestKey(request, "txtPageNumber", enumDataType.Integer)

            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXGetDNAWorkflowCases(%s, %s, %s)}", ('ONCOLOGY BMT', _dateFrom, _dateTo))
                _workflowCases = self.utilities.ConvertCursorListToDict(_cursor)

            _context = {
                "criteriaDateFrom" : _dateFrom,
                "criteriaDateTo" : _dateTo,
                "Title": self.title,
                "workflowCases": _workflowCases,
            }
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "BMTSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)


