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

    def get(self, request, _labNumber, _indication):

        try:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            _sample = self.dataServices.GetSample(_labNumber)

            # Because the template cannot handle the list of dictionary that is
            # _sample, we have to extract the dictionary in _sampleItem
            _sampleItem = _sample[0]

            _indicationReportBills = self.dataServices.GetSampleIndicationReportBill(_labNumber)

            _tests = self.dataServices.GetSampleTests(_labNumber)

            _worksheetResults = self.dataServices.GetSampleWorksheetResults(_labNumber, _indication)

            # if _workflowName == 'WGS':
            #    _backURL = _workflowName + "Search"
            # else:
            #    _backURL = "HaemOnc" + _workflowName + "Search"
            _backURL = "StartPage"

            _context = {
                "Title": self.title,
                "labNumber": _labNumber,
                "sampleItem": _sampleItem,
                "indicationReportBills": _indicationReportBills,
                "tests": _tests,
                "worksheetResults": _worksheetResults,
                "backURL": _backURL,
            }

            return render(request, self.template_name, _context)

        except Exception as ex:
            _context = {
                "Title": self.title,
                "errorMessage": "SampleForm.get : " + str(ex)
            }

            return render(request, self.template_name, _context)
