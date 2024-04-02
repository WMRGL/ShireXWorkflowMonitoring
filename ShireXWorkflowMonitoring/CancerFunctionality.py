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

            try:
                _totalWorkflowCases2 = self.dataServices.GetDNAWorkflowCases(
                    '2012_SOLID_CANCER', '2012_RARE_DIS', 'SC', _dateFrom, _dateTo, _reportStatus, _priority,
                    _diseaseIndicationCode1,
                    _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                    _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, request.user.username, _lastName,
                    _labNumber, _RefKey, _noResultStatus)
                _workflowCases2 = Paginator(_totalWorkflowCases2, _itemsPerPage)
                _pageOfWorkflowCases2 = _workflowCases2.page(_pageNumber)
                #_comment = self.dataServices.GetComment(_labNumber, _pageOfWorkflowCases2)
                #_value2 = self.dataServices.GetValue2(_labNumber, _pageOfWorkflowCases2)
                #_value1 = self.dataServices.GetValue1(_labNumber, _pageOfWorkflowCases2)
                #_result = self.dataServices.GetResults(_labNumber, _pageOfWorkflowCases2)

            except AttributeError:
                _pageOfWorkflowCases2 = None


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
                #"result": _result,
                #"value1": _value1,
                #"comments": _comment,
                #"value2": _value2,
            }
            #print(_result)
            #print(_comment)
            #print(_value1)
            # Render the template with the context data - MW
            return render(request, self.template_name, _context)

        except Exception as ex:
            # Handle any exceptions during processing and prepare an error message - MW
            context = {
                "Title": self.title,
                "errorMessage": "SCSearch.get : " + str(ex)
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
                "errorMessage": "WGSSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)



"""
class BaseSearchView(TemplateView):
    
    #Base class for search views, containing shared logic - MW
    
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()
    extractsheetHelper = ExtractSheet()

    def get_search_parameters(self, request, default_date_range=60, is_postback=False):

        #Extracts and returns search parameters from the request - MW
        date_from = datetime.today() - timedelta(days=default_date_range)
        date_to = datetime.today() + timedelta(days=30)
        report_status = "NOTFINAL"
        priority = ""
        disease_indication_codes = ["", "", ""]
        reason_for_disease_indications = ["", "", ""]
        last_name = ""
        lab_number = ""
        ref_key = ""
        no_result_status = 0

        if is_postback:
            try:
                # Extract search parameters from the request - MW
                date_from = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime, default=date_from)
                date_to = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime, default=date_to)
                page_number = self.utilities.GetRequestKey(request, "txtPageNumber", enumDataType.Integer, default=1)
                items_per_page = self.utilities.GetRequestKey(request, "ddlCriteriaItemsPerPage", enumDataType.Integer, default=20)
                report_status = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String, default=report_status)
                priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String, default=priority)

                for i in range(1, 4):
                    disease_indication_codes[i-1] = self.utilities.GetRequestKey(request, f"ddlCriteriaDiseaseIndication{i}", enumDataType.String, default="")
                    reason_for_disease_indications[i-1] = self.utilities.GetRequestKey(request, f"ddlCriteriaReasonForDiseaseIndication{i}", enumDataType.String, default="")

                last_name = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String, default="")
                lab_number = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String, default="")
                ref_key = self.utilities.GetRequestKey(request, "ddlCriteriaRefKey", enumDataType.String, default="")
                no_result_status = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer, default=0)

            except Exception as ex:
                # Handle exceptions in extracting parameters - MW
                # Log the exception if necessary
                pass

        return (date_from, date_to, report_status, priority, disease_indication_codes, reason_for_disease_indications, last_name, lab_number, ref_key, no_result_status)

    def prepare_context(self, request, workflow_cases, search_params):

        #Prepares and returns the context for rendering the template - MW
        report_statuses = self.dataServices.GetReportStatus()
        priorities = self.dataServices.GetDNAPriority()
        disease_indications = self.dataServices.GetDNADiseaseIndication(*search_params[4])
        reasons_for_disease_indications = self.dataServices.GetDNAReasonForDiseaseIndication(*search_params[5])
        ref_keys = self.dataServices.GetDNARefKey(*search_params[4])

        return {
            "criteriaDateFrom": search_params[0],
            "criteriaDateTo": search_params[1],
            "Title": self.title,
            "workflowCases": workflow_cases,
            "itemsPerPage": search_params[9],
            "criteriaReportStatuses": report_statuses,
            "criteriaReportStatus": search_params[2],
            "criteriaPriorities": priorities,
            "criteriaPriority": search_params[3],
            "criteriaDiseaseIndications": disease_indications,
            "criteriaDiseaseIndication1": search_params[4][0],
            "criteriaDiseaseIndication2": search_params[4][1],
            "criteriaDiseaseIndication3": search_params[4][2],
            "criteriaReasonsForDiseaseIndications": reasons_for_disease_indications,
            "criteriaReasonForDiseaseIndication1": search_params[5][0],
            "criteriaReasonForDiseaseIndication2": search_params[5][1],
            "criteriaReasonForDiseaseIndication3": search_params[5][2],
            "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(workflow_cases),
            "criteriaSurname": search_params[6],
            "criteriaLabnumber": search_params[7],
            "criteriaRefKey": search_params[8],
            "criteriaRefKeys": ref_keys,
            "searchCount": len(workflow_cases),
        }

    # Other shared methods can be added here - MW

class SolidCancerSearch(BaseSearchView):
    template_name = "SolidCancerSearch.html"
    title = ShireXWorkflowMonitoringConfig.title

    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('LoginPage'))

        is_postback = request.GET.__len__() > 0
        search_params = self.get_search_parameters(request, is_postback=is_postback)

        # Fetch workflow cases based on search parameters - MW
        workflow_cases = self.dataServices.GetDNAWorkflowCases(
            '2012_SOLID_CANCER', '2012_RARE_DIS', 'SC', *search_params[:8])

        # Process workflow cases with worksheet and extractsheet helpers - MW
        workflow_cases = self.process_workflow_cases(workflow_cases)

        context = self.prepare_context(request, workflow_cases, search_params)
        return render(request, self.template_name, context)

    # Similar structure for WGSSearch, reusing shared methods from BaseSearchView - MW
    def prepare_context(self, request, workflow_cases, search_params):

        #Prepares and returns the context for rendering the template - MW
        report_statuses = self.dataServices.GetReportStatus()
        priorities = self.dataServices.GetDNAPriority()
        disease_indications = self.dataServices.GetDNADiseaseIndication(*search_params[4])
        reasons_for_disease_indications = self.dataServices.GetDNAReasonForDiseaseIndication(*search_params[5])
        ref_keys = self.dataServices.GetDNARefKey(*search_params[4])

        return {
            "criteriaDateFrom": search_params[0],
            "criteriaDateTo": search_params[1],
            "Title": self.title,
            "workflowCases": workflow_cases,
            "itemsPerPage": search_params[9],
            "criteriaReportStatuses": report_statuses,
            "criteriaReportStatus": search_params[2],
            "criteriaPriorities": priorities,
            "criteriaPriority": search_params[3],
            "criteriaDiseaseIndications": disease_indications,
            "criteriaDiseaseIndication1": search_params[4][0],
            "criteriaDiseaseIndication2": search_params[4][1],
            "criteriaDiseaseIndication3": search_params[4][2],
            "criteriaReasonsForDiseaseIndications": reasons_for_disease_indications,
            "criteriaReasonForDiseaseIndication1": search_params[5][0],
            "criteriaReasonForDiseaseIndication2": search_params[5][1],
            "criteriaReasonForDiseaseIndication3": search_params[5][2],
            "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(workflow_cases),
            "criteriaSurname": search_params[6],
            "criteriaLabnumber": search_params[7],
            "criteriaRefKey": search_params[8],
            "criteriaRefKeys": ref_keys,
            "searchCount": len(workflow_cases),
        }

    # Other shared methods can be added here - MW

class WGSSearch(BaseSearchView):
    template_name = "WGSSearch.html"
    title = ShireXWorkflowMonitoringConfig.title

    def get(self, request):
        workflow_cases = self.dataServices.GetDNAWorkflowCases(
            '2012_SOLID_CANCER', '2012_RARE_DIS', 'SC', *search_params[:8])

        # Process workflow cases with worksheet and extractsheet helpers - MW
        workflow_cases = self.process_workflow_cases(workflow_cases)

        context = self.prepare_context(request, workflow_cases, search_params)
        return render(request, self.template_name, context)

    def prepare_context(self, request, workflow_cases, search_params):
        # Prepares and returns the context for rendering the template - MW
        report_statuses = self.dataServices.GetReportStatus()
        priorities = self.dataServices.GetDNAPriority()
        disease_indications = self.dataServices.GetDNADiseaseIndication(*search_params[4])
        reasons_for_disease_indications = self.dataServices.GetDNAReasonForDiseaseIndication(*search_params[5])
        ref_keys = self.dataServices.GetDNARefKey(*search_params[4])

        return {
            "criteriaDateFrom": search_params[0],
            "criteriaDateTo": search_params[1],
            "Title": self.title,
            "workflowCases": workflow_cases,
            "itemsPerPage": search_params[9],
            "criteriaReportStatuses": report_statuses,
            "criteriaReportStatus": search_params[2],
            "criteriaPriorities": priorities,
            "criteriaPriority": search_params[3],
            "criteriaDiseaseIndications": disease_indications,
            "criteriaDiseaseIndication1": search_params[4][0],
            "criteriaDiseaseIndication2": search_params[4][1],
            "criteriaDiseaseIndication3": search_params[4][2],
            "criteriaReasonsForDiseaseIndications": reasons_for_disease_indications,
            "criteriaReasonForDiseaseIndication1": search_params[5][0],
            "criteriaReasonForDiseaseIndication2": search_params[5][1],
            "criteriaReasonForDiseaseIndication3": search_params[5][2],
            "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(workflow_cases),
            "criteriaSurname": search_params[6],
            "criteriaLabnumber": search_params[7],
            "criteriaRefKey": search_params[8],
            "criteriaRefKeys": ref_keys,
            "searchCount": len(workflow_cases),}
"""