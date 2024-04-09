# Add Haem Onc specific classes in this file
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from ShireXWorkflowMonitoring.apps import ShireXWorkflowMonitoringConfig
from datetime import datetime
from datetime import timedelta
from ShireXWorkflowMonitoring.CommonFunctionality import UtilityFunctions
from ShireXWorkflowMonitoring.CommonFunctionality import enumDataType
from ShireXWorkflowMonitoring.DataServices import ShireData
from django.core.paginator import Paginator
from ShireXWorkflowMonitoring.WorksheetFunctionality import Worksheet
from ShireXWorkflowMonitoring.WorksheetFunctionality import ExtractSheet

# Define the class SolidCancerSearch which extends TemplateView - MW
class SolidCancerSearch(TemplateView):
    # Specify the HTML template name to render - MW
    template_name = "SolidCancerSearch.html"
    # Set the title using a title attribute from another config class - MW
    title = ShireXWorkflowMonitoringConfig.title
    # Initialise instances of utility and data service classes - MW
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()       # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    # Define the GET method to handle HTTP GET requests - MW
    def get(self, request):
        try:
            # Redirect unauthenticated users to the login page - MW
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            #Determine if the request is a postback (form submission) or not - MW
            _isPostBack = bool(request.GET)

            # Initialize search filters with default values - MW
            # These filters are used in querying the database - MW
            _reportStatus = "NOTFINAL"
            _priority = ""
            _diseaseIndicationCode1 = ""
            _diseaseIndicationCode2 = ""
            _diseaseIndicationCode3 = ""
            _reasonForDiseaseIndication1 = ""
            _reasonForDiseaseIndication2 = ""
            _reasonForDiseaseIndication3 = ""
            _lastName = ""
            _labNumber = ""
            _RefKey = ""
            _noResultStatus = 0
            _searchCount = 0
            _worksheet = self.utilities.GetRequestKey(request, "WORKSHEET", enumDataType.String)
            _probe_primer = self.utilities.GetRequestKey(request, "PROBE_PRIMER", enumDataType.String)
            _lane = self.utilities.GetRequestKey(request, "LANE", enumDataType.String)

            # Set default date range and pagination values for first-time page load - MW
            # Modify these values if it's a postback with user-specified filters - MW
            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                # Extract search criteria from the request if it's a postback - MW
                # Utilize utility functions for data extraction and conversion - MW
                # Handle exceptions in case of invalid input or conversion errors - MW
                try:
                    _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1",
                                                                           enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2",
                                                                           enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3",
                                                                           enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(
                        request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(
                        request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=60)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            # Query the data service for workflow cases based on the search criteria - MW
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_SOLID_CANCER', '2012_RARE_DIS', 'SC', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1,
                _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, request.user.username, _lastName,
                _labNumber, _RefKey, _noResultStatus)

            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_pageOfWorkflowCases)
            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_SOLID_CANCER', '2012_RARE_DIS', 'SC')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(_diseaseIndicationCode1,
                                                                                               _diseaseIndicationCode2,
                                                                                               _diseaseIndicationCode3)
            # Prepare the context dictionary with all the necessary data for rendering the template - MW
            # This includes the extracted and processed data, search criteria, and configuration items - MW
            _context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": _pageOfWorkflowCases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": _reportStatuses,
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": _priorities,
                "criteriaPriority": _priority,
                "criteriaDiseaseIndications": _diseaseIndications,
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaReasonForDiseaseIndication3": _reasonForDiseaseIndication3,
                "criteriaSurnames": _listOfSurnames,
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": _searchCount,
            }

            # Render the template with the context data - MW
            return render(request, self.template_name, _context)

        except Exception as ex:
            # Handle any exceptions during processing and prepare an error message - MW
            context = {
                "Title": self.title,
                "errorMessage": "SCSearch.get : " + str(ex) if ex is not None else "Unknown error"
            }

            # Render the template with error information - MW
            return render(request, self.template_name, context)

class WGSSearch(TemplateView):
    template_name = "WGSSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            if request.GET.__len__() == 0:
                _isPostBack = False
            else:
                _isPostBack = True

            _reportStatus = "NOTFINAL"
            _priority = ""
            _diseaseIndicationCode1 = ""
            _diseaseIndicationCode2 = ""
            _diseaseIndicationCode3 = ""
            _reasonForDiseaseIndication1 = ""
            _reasonForDiseaseIndication2 = ""
            _reasonForDiseaseIndication3 = ""
            _lastName = ""
            _labNumber = ""
            _refKey = ""
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=90)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1",
                                                                           enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2",
                                                                           enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3",
                                                                           enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(
                        request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(
                        request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _refKey = self.utilities.GetRequestKey(request, "ddlCriteriaRefKey", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)

                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20


            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
               '2012_SOLID_CANCER', '2012_OTHER', 'WGS', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1,
               _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
               _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, request.user.username, _lastName,
               _labNumber, _refKey, _noResultStatus)

            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_pageOfWorkflowCases)

            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_SOLID_CANCER', '2012_OTHER', 'WGS')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(_diseaseIndicationCode1,
                                                                                               _diseaseIndicationCode2,
                                                                                               _diseaseIndicationCode3)

            _refKeys = self.dataServices.GetDNARefKey(_diseaseIndicationCode1, _diseaseIndicationCode2,
                                                      _diseaseIndicationCode3)

            _context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": _pageOfWorkflowCases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": _reportStatuses,
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": _priorities,
                "criteriaPriority": _priority,
                "criteriaDiseaseIndications": _diseaseIndications,
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaReasonForDiseaseIndication3": _reasonForDiseaseIndication3,
                "criteriaRefKey": _refKey,
                "criteriaRefKeys": _refKeys,
                "criteriaSurnames": _listOfSurnames,
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": _searchCount,
            }
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "WGSSearch.get : " + str(ex) if ex is not None else "Unknown error"
            }

            return render(request, self.template_name, context)