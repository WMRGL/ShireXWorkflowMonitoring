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

    def get(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # Retrieve URL parameters from kwargs
            labNumber = kwargs.get("labNumber")
            indication = kwargs.get("indication")

            _sample = self.dataServices.GetSample(labNumber)

            # Ensure safe extraction of data
            _sampleItem = _sample[0] if _sample else {}

            _indicationReportBills = self.dataServices.GetSampleIndicationReportBill(labNumber)
            _tests = self.dataServices.GetSampleTests(labNumber)
            _worksheetResults = self.dataServices.GetSampleWorksheetResults(labNumber, indication)

            _context = {
                "Title": self.title,
                "labNumber": labNumber,
                "sampleItem": _sampleItem,
                "indicationReportBills": _indicationReportBills,
                "tests": _tests,
                "worksheetResults": _worksheetResults,
                "backURL": "StartPage",
            }

            return render(request, self.template_name, _context)

        except Exception as ex:
            _context = {
                "Title": self.title,
                "errorMessage": f"SampleForm.get: {ex}"
            }
            return render(request, self.template_name, _context)
