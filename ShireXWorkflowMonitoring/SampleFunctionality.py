from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.urls import reverse
from django.views.generic import TemplateView
from ShireXWorkflowMonitoring.apps import ShireXWorkflowMonitoringConfig
from ShireXWorkflowMonitoring.CommonFunctionality import UtilityFunctions
from ShireXWorkflowMonitoring.DataServices import ShireData

class SampleForm(TemplateView):
    template_name = "SampleForm.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()

    def get(self, request, _labNumber):

        try:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            _indicationReportBills = self.dataServices.GetSampleIndicationReportBill(_labNumber)

            _worksheetResults = self.dataServices.GetSampleWorksheetResults(_labNumber)

            _context = {
                "Title": self.title,
                "labNumber": _labNumber,
                "indicationReportBills" : _indicationReportBills,
                "worksheetResults" : _worksheetResults,
            }

            return render(request, self.template_name, _context)

        except Exception as ex:
            _context = {
                "Title": self.title,
                "errorMessage": "SampleForm.get : " + str(ex)
            }

            return render(request, self.template_name, _context)
