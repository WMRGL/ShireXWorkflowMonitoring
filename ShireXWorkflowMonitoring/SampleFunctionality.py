from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.urls import reverse
from django.views.generic import TemplateView
from ShireXWorkflowMonitoring.apps import ShireXWorkflowMonitoringConfig
from ShireXWorkflowMonitoring.CommonFunctionality import UtilityFunctions
from ShireXWorkflowMonitoring.DataServices import ShireData

# Define the SampleForm class, inheriting from TemplateView, to handle requests for the sample form page - MW
class SampleForm(TemplateView):
    template_name = "SampleForm.html"# Template file to be used for rendering the sample form page - MW
    title = ShireXWorkflowMonitoringConfig.title# Title of the page, obtained from app's configuration - MW
    utilities = UtilityFunctions()# Utility functions instance - MW
    dataServices = ShireData()# Data services instance for database interactions - MW

    # Method to handle HTTP GET requests for the sample form - MW
    def get(self, request, _labNumber, _indication):

        try:
            # Redirect unauthenticated users to the login page - MW
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            _sample = self.dataServices.GetSample(_labNumber)

            # Because the template cannot handle the list of dictionary that is
            # _sample, we have to extract the dictionary in _sampleItem
            # Retrieve sample details using the lab number from the database - MW
            _sampleItem = _sample[0]

            # Retrieve indication, report, and billing information for the sample - MW
            _indicationReportBills = self.dataServices.GetSampleIndicationReportBill(_labNumber)

            # Retrieve test details for the sample - MW
            _tests = self.dataServices.GetSampleTests(_labNumber)

            # Retrieve worksheet results for the sample based on lab number and indication - MW
            _worksheetResults = self.dataServices.GetSampleWorksheetResults(_labNumber, _indication)

            # if _workflowName == 'WGS':
            #    _backURL = _workflowName + "Search"
            # else:
            #    _backURL = "HaemOnc" + _workflowName + "Search"
            # Define the back URL; default set to 'StartPage' (could be modified for specific workflow navigation) - MW
            _backURL = "StartPage"

            # Context dictionary containing data to be passed to the template - MW
            _context = {
                "Title": self.title,
                "labNumber": _labNumber,
                "sampleItem": _sampleItem,
                "indicationReportBills": _indicationReportBills,
                "tests": _tests,
                "worksheetResults": _worksheetResults,
                "backURL": _backURL,
            }

            # Render and return the sample form page with the context data - MW
            return render(request, self.template_name, _context)

        except Exception as ex:
            # Handle exceptions and render the error message - MW
            _context = {
                "Title": self.title,
                "errorMessage": "SampleForm.get : " + str(ex)
            }

            return render(request, self.template_name, _context)