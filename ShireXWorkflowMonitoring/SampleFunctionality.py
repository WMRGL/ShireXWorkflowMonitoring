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

            _comment = self.dataServices.GetComment(_labNumber)
            _value2 = self.dataServices.GetValue2(_labNumber)
            _value1 = self.dataServices.GetValue1(_labNumber)
            _result = self.dataServices.GetResults(_labNumber)

            #Convert _comment and _value2 to strings from a dictionary to make the data readable on the web page table - MW
            _commentStr = ', '.join([str(comment['COMMENT']) for comment in _comment])
            _value2Str = ', '.join([str(value['VALUE2']) for value in _value2])


            _backURL = "StartPage"

            _context = {
                "Title": self.title,
                "labNumber": _labNumber,
                "sampleItem": _sampleItem,
                "indicationReportBills": _indicationReportBills,
                "tests": _tests,
                "worksheetResults": _worksheetResults,
                "backURL": _backURL,
                "result": _result,
                "value1": _value1,
                "comments": _commentStr,
                "value2": _value2Str,
            }

            return render(request, self.template_name, _context)

        except Exception as ex:
            _context = {
                "Title": self.title,
                "errorMessage": "SampleForm.get : " + str(ex)
            }

            return render(request, self.template_name, _context)

