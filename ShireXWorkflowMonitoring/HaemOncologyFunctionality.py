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
from django.core.paginator import EmptyPage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from datetime import datetime, timedelta

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.utils.http import urlencode
from django.views.generic import TemplateView
from datetime import datetime, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class BMTSearch(TemplateView):
    template_name = "BMTSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return redirect("LoginPage")

            # Default filter values
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

            # Extract search filters and pagination parameters
            _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or (datetime.today() - timedelta(days=60))
            _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or (datetime.today() + timedelta(days=30))
            _itemsPerPage = int(request.GET.get("items_per_page", 20))
            page = request.GET.get("page", 1)

            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            # Extract additional filters
            _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or _reportStatus
            _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
            _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or _diseaseIndicationCode1
            _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or _diseaseIndicationCode2
            _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or _reasonForDiseaseIndication1
            _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
            _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or _labNumber
            _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or _noResultStatus

            # Retrieve data
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                'ONCOLOGY BMT', '', 'BMT', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, "", _reasonForDiseaseIndication1,
                "", "", request.user.username, _lastName, _labNumber, _RefKey, _noResultStatus
            )

            # Apply data transformations
            _totalWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_totalWorkflowCases)
            _totalWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_totalWorkflowCases)

            # Fetch reasons for dropdowns
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, ""
            ) or []

            # Add descriptions if missing
            _reasonsForDiseaseIndications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""), "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
                for reason in _reasonsForDiseaseIndications
            ]

            # Paginate results
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                paginated_cases = paginator.page(page)
            except PageNotAnInteger:
                paginated_cases = paginator.page(1)
            except EmptyPage:
                paginated_cases = paginator.page(paginator.num_pages)

            # Context for rendering
            context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": paginated_cases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": self.dataServices.GetReportStatus(),
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": self.dataServices.GetDNAPriority(),
                "criteriaPriority": _priority,
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('ONCOLOGY BMT', '', 'BMT'),
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases),
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "searchCount": len(_totalWorkflowCases),
                "page_obj": paginated_cases,
            }
            return render(request, self.template_name, context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": f"BMTSearch.get : {ex}"
            }
            return render(request, self.template_name, context)




class MPNSearch(TemplateView):
    template_name = "MPNSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            # Redirect if user is not authenticated
            if not request.user.is_authenticated:
                return redirect("LoginPage")

            # Default filter values
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
            _showAlerts = False
            _noResultStatus = 0

            # Extract search filters and pagination parameters
            _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or (datetime.today() - timedelta(days=60))
            _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or (datetime.today() + timedelta(days=30))
            _itemsPerPage = int(request.GET.get("items_per_page", 20))  # Default to 20 items per page
            page = request.GET.get("page", 1)

            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            # Extract additional filters
            _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or _reportStatus
            _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
            _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or _diseaseIndicationCode1
            _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or _diseaseIndicationCode2
            _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or _reasonForDiseaseIndication1
            _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
            _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or _labNumber
            _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or _noResultStatus

            # Retrieve workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'MPN', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, "", "",
                request.user.username, _lastName, _labNumber, _RefKey, _noResultStatus
            )

            # Apply data transformations
            _totalWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_totalWorkflowCases)
            _totalWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_totalWorkflowCases)

            # Fetch reasons for dropdowns
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3
            ) or []

            # Add descriptions if missing
            _reasonsForDiseaseIndications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""), "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
                for reason in _reasonsForDiseaseIndications
            ]

            # Paginate results
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                paginated_cases = paginator.page(page)
            except PageNotAnInteger:
                paginated_cases = paginator.page(1)
            except EmptyPage:
                paginated_cases = paginator.page(paginator.num_pages)

            # Prepare query parameters for pagination links
            query_params = request.GET.copy()
            query_params.pop("page", None)
            base_query_string = urlencode(query_params)

            # Context for rendering
            context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": paginated_cases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": self.dataServices.GetReportStatus(),
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": self.dataServices.GetDNAPriority(),
                "criteriaPriority": _priority,
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'MPN'),
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases),
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": len(_totalWorkflowCases),
                "page_obj": paginated_cases,
                "base_query_string": base_query_string,
            }

            return render(request, self.template_name, context)

        except Exception as ex:
            print(f"Error in MPNSearch.get: {ex}")
            context = {
                "Title": self.title,
                "errorMessage": f"MPNSearch.get : {ex}"
            }
            return render(request, self.template_name, context)

class DAMLSearch(TemplateView):  # AML & MDS
    template_name = "D-AMLSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            # Redirect to login if the user is not authenticated
            if not request.user.is_authenticated:
                return redirect("LoginPage")

            # Default filter values
            _reportStatus = "NOTFINAL"
            _priority = ""
            _diseaseIndicationCode1 = ""
            _diseaseIndicationCode2 = ""
            _diseaseIndicationCode3 = ""
            _diseaseIndicationCode4 = ""
            _reasonForDiseaseIndication1 = ""
            _reasonForDiseaseIndication2 = ""
            _reasonForDiseaseIndication3 = ""
            _lastName = ""
            _labNumber = ""
            _RefKey = ""
            _noResultStatus = 0  # Default value for "Workflow" dropdown

            # Extract search filters and pagination parameters
            _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or (datetime.today() - timedelta(days=60))
            _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or (datetime.today() + timedelta(days=30))
            _itemsPerPage = int(request.GET.get("items_per_page", 20))  # Default to 20 items per page
            page = request.GET.get("page", 1)

            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            # Extract additional filters from the request
            _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or _reportStatus
            _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
            _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or _diseaseIndicationCode1
            _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or _diseaseIndicationCode2
            _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or _diseaseIndicationCode3
            _diseaseIndicationCode4 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication4", enumDataType.String) or _diseaseIndicationCode4
            _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or _reasonForDiseaseIndication1
            _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
            _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or _labNumber

            # Update for "Workflow" dropdown
            _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or _noResultStatus

            print(f"Filters applied: _dateFrom={_dateFrom}, _dateTo={_dateTo}, _itemsPerPage={_itemsPerPage}, page={page}, _noResultStatus={_noResultStatus}")

            # Retrieve filtered workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'DAML', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3,
                request.user.username, _lastName, _labNumber, _RefKey, _noResultStatus
            )

            # Apply data transformations
            _totalWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_totalWorkflowCases)
            _totalWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_totalWorkflowCases)

            # Fetch reasons for dropdowns
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3
            ) or []

            # Add descriptions if missing
            _reasonsForDiseaseIndications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""), "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
                for reason in _reasonsForDiseaseIndications
            ]

            # Paginate results
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                paginated_cases = paginator.page(page)
            except PageNotAnInteger:
                paginated_cases = paginator.page(1)
            except EmptyPage:
                paginated_cases = paginator.page(paginator.num_pages)

            # Prepare query parameters for pagination links
            query_params = request.GET.copy()
            query_params.pop("page", None)
            base_query_string = urlencode(query_params)

            # Context for rendering
            context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": paginated_cases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": self.dataServices.GetReportStatus(),
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": self.dataServices.GetDNAPriority(),
                "criteriaPriority": _priority,
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'DAML'),
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaDiseaseIndication4": _diseaseIndicationCode4,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases),
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": len(_totalWorkflowCases),
                "page_obj": paginated_cases,
                "base_query_string": base_query_string,
            }

            return render(request, self.template_name, context)

        except Exception as ex:
            print(f"Error in DAMLSearch.get: {ex}")
            context = {
                "Title": self.title,
                "errorMessage": f"DAMLSearch.get : {ex}"
            }
            return render(request, self.template_name, context)


class CytoSearch(TemplateView):  # AML & MDS
    template_name = "CytoSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            # Redirect to login if the user is not authenticated
            if not request.user.is_authenticated:
                return redirect("LoginPage")

            # Default filter values
            _reportStatus = "NOTFINAL"
            _priority = ""
            _diseaseIndicationCode1 = ""
            _diseaseIndicationCode2 = ""
            _diseaseIndicationCode3 = ""
            _diseaseIndicationCode4 = ""
            _reasonForDiseaseIndication1 = ""
            _reasonForDiseaseIndication2 = ""
            _reasonForDiseaseIndication3 = ""
            _lastName = ""
            _labNumber = ""
            _RefKey = ""
            _noResultStatus = 0

            # Extract search filters and pagination parameters
            _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or (datetime.today() - timedelta(days=60))
            _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or (datetime.today() + timedelta(days=30))
            _itemsPerPage = int(request.GET.get("items_per_page", 20))  # Default to 20 items per page
            page = request.GET.get("page", 1)

            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            # Extract additional filters from the request
            _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or _reportStatus
            _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
            _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or _diseaseIndicationCode1
            _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or _diseaseIndicationCode2
            _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or _diseaseIndicationCode3
            _diseaseIndicationCode4 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication4", enumDataType.String) or _diseaseIndicationCode4
            _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or _reasonForDiseaseIndication1
            _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
            _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or _labNumber

            _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or _noResultStatus

            print(f"Filters applied: _dateFrom={_dateFrom}, _dateTo={_dateTo}, _itemsPerPage={_itemsPerPage}, page={page}")

            # Retrieve filtered workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'CYTO', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3,
                request.user.username, _lastName, _labNumber, _RefKey, _noResultStatus
            )


            # Paginate results
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                paginated_cases = paginator.page(page)
            except PageNotAnInteger:
                paginated_cases = paginator.page(1)
            except EmptyPage:
                paginated_cases = paginator.page(paginator.num_pages)

            # Add additional data to cases
            paginated_cases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(paginated_cases)
            paginated_cases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(paginated_cases)
            paginated_cases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(paginated_cases)
            paginated_cases = self.extractsheetHelper.AddExtractsToWorkflowCases(paginated_cases)

            # Prepare query parameters for pagination links
            query_params = request.GET.copy()
            query_params.pop("page", None)
            base_query_string = urlencode(query_params)

            # Context for rendering
            context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": paginated_cases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": self.dataServices.GetReportStatus(),
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": self.dataServices.GetDNAPriority(),
                "criteriaPriority": _priority,
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'DAML'),
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaDiseaseIndication4": _diseaseIndicationCode4,
                "criteriaReasonsForDiseaseIndications": self.dataServices.GetDNAReasonForDiseaseIndication(
                    _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3),
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases),
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": len(_totalWorkflowCases),
                "page_obj": paginated_cases,
                "base_query_string": base_query_string,
            }

            return render(request, self.template_name, context)

        except Exception as ex:
            print(f"Error in DAMLSearch.get: {ex}")
            context = {
                "Title": self.title,
                "errorMessage": f"DAMLSearch.get : {ex}"
            }
            return render(request, self.template_name, context)



class BreakSearch(TemplateView):
    template_name = "BreakSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            # Redirect to login if the user is not authenticated
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # Default filter values
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

            # Extract search filters and pagination parameters
            _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or (datetime.today() - timedelta(days=60))
            _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or (datetime.today() + timedelta(days=30))
            _itemsPerPage = int(request.GET.get("items_per_page", 20))  # Default to 20 items per page
            page = request.GET.get("page", 1)

            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            # Extract additional filters from the request
            _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or _reportStatus
            _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
            _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or _diseaseIndicationCode1
            _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or _diseaseIndicationCode2
            _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or _diseaseIndicationCode3
            _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or _reasonForDiseaseIndication1
            _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
            _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or _labNumber
            _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or _noResultStatus

            print(f"Filters applied: _dateFrom={_dateFrom}, _dateTo={_dateTo}, _itemsPerPage={_itemsPerPage}, page={page}")

            # Retrieve filtered workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'BREAK', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3,
                request.user.username, _lastName, _labNumber, _RefKey, _noResultStatus
            )

            print(f"Total workflow cases retrieved: {len(_totalWorkflowCases)}")

            # Apply data transformations
            _totalWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_totalWorkflowCases)
            _totalWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_totalWorkflowCases)

            # Fetch reasons for dropdowns
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3
            ) or []

            # Add descriptions if missing
            _reasonsForDiseaseIndications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""), "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
                for reason in _reasonsForDiseaseIndications
            ]

            # Paginate results
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                paginated_cases = paginator.page(page)
            except PageNotAnInteger:
                paginated_cases = paginator.page(1)
            except EmptyPage:
                paginated_cases = paginator.page(paginator.num_pages)

            # Prepare query parameters for pagination links
            query_params = request.GET.copy()
            query_params.pop("page", None)
            base_query_string = urlencode(query_params)

            # Context for rendering
            context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": paginated_cases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": self.dataServices.GetReportStatus(),
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": self.dataServices.GetDNAPriority(),
                "criteriaPriority": _priority,
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'BREAK'),
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaReasonForDiseaseIndication3": _reasonForDiseaseIndication3,
                "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases),
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": len(_totalWorkflowCases),
                "page_obj": paginated_cases,
                "base_query_string": base_query_string,
            }

            return render(request, self.template_name, context)

        except Exception as ex:
            print(f"Error in BreakSearch.get: {ex}")
            context = {
                "Title": self.title,
                "errorMessage": f"BreakSearch.get : {ex}"
            }
            return render(request, self.template_name, context)

class RAMLSearch(TemplateView):
    template_name = "R-AMLSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            # Redirect to login page if the user is not authenticated
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # Initialize default filters
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

            # Get pagination and filter parameters
            _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or (datetime.today() - timedelta(days=60))
            _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or (datetime.today() + timedelta(days=30))
            _itemsPerPage = int(request.GET.get("items_per_page", 20))  # Default to 20 items per page
            page = request.GET.get("page", 1)

            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            # Retrieve additional filters from the request
            _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or _reportStatus
            _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
            _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or _diseaseIndicationCode1
            _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or _diseaseIndicationCode2
            _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or _diseaseIndicationCode3
            _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or _reasonForDiseaseIndication1
            _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String) or _reasonForDiseaseIndication2
            _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String) or _reasonForDiseaseIndication3
            _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
            _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or _labNumber
            _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or _noResultStatus

            # Retrieve workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'RAML', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3,
                request.user.username, _lastName, _labNumber, _RefKey, _noResultStatus
            )

            # Apply data transformations
            _totalWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_totalWorkflowCases)
            _totalWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_totalWorkflowCases)

            # Fetch reasons for dropdowns
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3
            ) or []

            # Add descriptions if missing
            _reasonsForDiseaseIndications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""), "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
                for reason in _reasonsForDiseaseIndications
            ]

            # Paginate results
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                paginated_cases = paginator.page(page)
            except PageNotAnInteger:
                paginated_cases = paginator.page(1)
            except EmptyPage:
                paginated_cases = paginator.page(paginator.num_pages)

            # Prepare query parameters for pagination links
            query_params = request.GET.copy()
            query_params.pop("page", None)  # Remove 'page' parameter to construct the base query string
            base_query_string = urlencode(query_params)

            # Context for rendering
            context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": paginated_cases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": self.dataServices.GetReportStatus(),
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": self.dataServices.GetDNAPriority(),
                "criteriaPriority": _priority,
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'RAML'),
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaReasonForDiseaseIndication3": _reasonForDiseaseIndication3,
                "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases),
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": len(_totalWorkflowCases),
                "page_obj": paginated_cases,
                "base_query_string": base_query_string,
            }

            return render(request, self.template_name, context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": f"RAMLSearch.get : {ex}"
            }
            return render(request, self.template_name, context)

from urllib.parse import urlencode

class SNPSearch(TemplateView):
    template_name = "SNPSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            # Redirect to login page if user is not authenticated
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # Determine if the request is a postback
            is_postback = request.GET.__len__() > 0

            # Default filters
            _reportStatus = "NOTFINAL"
            _priority = ""
            _diseaseIndicationCode1 = ""
            _diseaseIndicationCode2 = ""
            _diseaseIndicationCode3 = ""
            _reasonForDiseaseIndication1 = ""
            _lastName = ""
            _labNumber = ""
            _RefKey = ""
            _noResultStatus = 0

            # Pagination and date filters
            _dateFrom = datetime.today() - timedelta(days=60)
            _dateTo = datetime.today() + timedelta(days=30)
            _itemsPerPage = int(request.GET.get("items_per_page", 20))  # Default items per page
            _pageNumber = int(request.GET.get("page", 1))  # Default to first page

            # Override filters with request values if postback
            if is_postback:
                try:
                    _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or _dateFrom
                    _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or _dateTo
                    _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or _reportStatus
                    _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or _diseaseIndicationCode1
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or _diseaseIndicationCode2
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or _diseaseIndicationCode3
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or _reasonForDiseaseIndication1
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or _labNumber
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or _noResultStatus
                except Exception as e:
                    # If any errors occur, reset to default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _itemsPerPage = -1

            # Fetch workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'SNP', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, "", "",  # Other reason codes not in use
                request.user.username, _lastName, _labNumber, _RefKey, _noResultStatus
            )

            # Process search results
            _searchCount = len(_totalWorkflowCases)
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                _pageOfWorkflowCases = paginator.page(_pageNumber)
            except (EmptyPage, PageNotAnInteger):
                _pageOfWorkflowCases = paginator.page(1)

            # Add additional workflow details
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)
            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)
            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)
            _pageOfWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_pageOfWorkflowCases)

            # Fetch criteria lists
            _reportStatuses = self.dataServices.GetReportStatus()
            _priorities = self.dataServices.GetDNAPriority()
            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'SNP')
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3
            ) or []

            # Add descriptions if missing
            _reasonsForDiseaseIndications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""), "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
                for reason in _reasonsForDiseaseIndications
            ]

            # Prepare query parameters for pagination links
            query_params = request.GET.copy()
            query_params.pop("page", None)  # Remove 'page' parameter to construct the base query string
            base_query_string = urlencode(query_params)

            # Build context for the template
            context = {
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
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": _searchCount,
                "page_obj": _pageOfWorkflowCases,
                "base_query_string": base_query_string,
            }

            return render(request, self.template_name, context)

        except Exception as ex:
            # Handle any unexpected exceptions
            context = {
                "Title": self.title,
                "errorMessage": f"SNPSearch.get : {str(ex)}"
            }
            return render(request, self.template_name, context)

class ALLSearch(TemplateView):
    template_name = "ALLSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return redirect("LoginPage")

            # Default values for filters
            _reportStatus = "NOTFINAL"
            _priority = ""
            _diseaseIndicationCode1 = ""
            _diseaseIndicationCode2 = ""
            _diseaseIndicationCode3 = ""
            _reasonForDiseaseIndication1 = ""
            _reasonForDiseaseIndication2 = ""
            _reasonForDiseaseIndication3 = ""

            # Retrieve search filters and pagination parameters
            _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or (datetime.today() - timedelta(days=60))
            _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or (datetime.today() + timedelta(days=30))
            _itemsPerPage = int(request.GET.get("ddlCriteriaItemsPerPage", 20))  # Default to 20 items per page
            page = request.GET.get("page", 1)

            # Indication Filters
            _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or _diseaseIndicationCode1
            _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or _diseaseIndicationCode2
            _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or _diseaseIndicationCode3

            # Reason Filters
            _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or _reasonForDiseaseIndication1
            _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String) or _reasonForDiseaseIndication2
            _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String) or _reasonForDiseaseIndication3

            # Additional filters
            _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
            _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or _reportStatus

            # Pagination logic
            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            # Retrieve workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'ALL', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3,
                request.user.username, "", "", "", 0
            )

            # Apply data transformations
            _totalWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_totalWorkflowCases)
            _totalWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_totalWorkflowCases)

            # Fetch indications and reasons for dropdowns
            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'ALL')
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3
            ) or []  # Ensure it defaults to an empty list if no data is returned

            # Add descriptions if missing
            _reasonsForDiseaseIndications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""), "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
                for reason in _reasonsForDiseaseIndications
            ]

            # Debug output for reasons
            print("Reasons for Disease Indications (Populated):", _reasonsForDiseaseIndications)

            # Paginate results
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                paginated_cases = paginator.page(page)
            except PageNotAnInteger:
                paginated_cases = paginator.page(1)
            except EmptyPage:
                paginated_cases = paginator.page(paginator.num_pages)

            # Prepare query parameters for pagination
            query_params = request.GET.copy()
            query_params.pop("page", None)  # Remove 'page' parameter to construct the base query string
            base_query_string = urlencode(query_params)

            # Context for rendering
            context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": paginated_cases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": self.dataServices.GetReportStatus(),
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": self.dataServices.GetDNAPriority(),
                "criteriaPriority": _priority,
                "criteriaDiseaseIndications": _diseaseIndications,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaReasonForDiseaseIndication3": _reasonForDiseaseIndication3,
                "searchCount": len(_totalWorkflowCases),
                "page_obj": paginated_cases,
                "base_query_string": base_query_string,
            }
            return render(request, self.template_name, context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": f"ALLSearch.get : {ex}"
            }
            return render(request, self.template_name, context)

class CLLSearch(TemplateView):
    template_name = "CLLSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            # Redirect to login page if user is not authenticated
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # Check if it's a postback
            is_postback = len(request.GET) > 0

            # Default filter values
            filters = {
                "reportStatus": "NOTFINAL",
                "priority": "",
                "diseaseIndicationCode1": "",
                "diseaseIndicationCode2": "",
                "diseaseIndicationCode3": "",
                "reasonForDiseaseIndication1": "",
                "reasonForDiseaseIndication2": "",
                "reasonForDiseaseIndication3": "",
                "lastName": "",
                "labNumber": "",
                "refKey": "",
                "noResultStatus": 0,
                "dateFrom": datetime.today() - timedelta(days=60),
                "dateTo": datetime.today() + timedelta(days=30),
                "pageNumber": 1,
                "itemsPerPage": 20,
            }

            # Override default filters if it's a postback
            if is_postback:
                try:
                    filters["dateFrom"] = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or filters["dateFrom"]
                    filters["dateTo"] = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or filters["dateTo"]
                    filters["pageNumber"] = self.utilities.GetRequestKey(request, "txtPageNumber", enumDataType.Integer) or filters["pageNumber"]
                    filters["itemsPerPage"] = self.utilities.GetRequestKey(request, "ddlCriteriaItemsPerPage", enumDataType.Integer) or filters["itemsPerPage"]
                    filters["reportStatus"] = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or filters["reportStatus"]
                    filters["priority"] = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or filters["priority"]
                    filters["diseaseIndicationCode1"] = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or filters["diseaseIndicationCode1"]
                    filters["diseaseIndicationCode2"] = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or filters["diseaseIndicationCode2"]
                    filters["diseaseIndicationCode3"] = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or filters["diseaseIndicationCode3"]
                    filters["reasonForDiseaseIndication1"] = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or filters["reasonForDiseaseIndication1"]
                    filters["reasonForDiseaseIndication2"] = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String) or filters["reasonForDiseaseIndication2"]
                    filters["reasonForDiseaseIndication3"] = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String) or filters["reasonForDiseaseIndication3"]
                    filters["lastName"] = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or filters["lastName"]
                    filters["labNumber"] = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or filters["labNumber"]
                    filters["noResultStatus"] = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or filters["noResultStatus"]
                except Exception as e:
                    # If there's an error, reset to default filters
                    filters["dateFrom"] = datetime.today() - timedelta(days=365)
                    filters["dateTo"] = datetime.today() + timedelta(days=30)
                    filters["pageNumber"] = 1
                    filters["itemsPerPage"] = -1

            # Fetch workflow cases
            totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'CLL',
                filters["dateFrom"], filters["dateTo"], filters["reportStatus"],
                filters["priority"], filters["diseaseIndicationCode1"], filters["diseaseIndicationCode2"],
                filters["diseaseIndicationCode3"], filters["reasonForDiseaseIndication1"],
                filters["reasonForDiseaseIndication2"], filters["reasonForDiseaseIndication3"],
                request.user.username, filters["lastName"], filters["labNumber"],
                filters["refKey"], filters["noResultStatus"]
            )

            # Paginate the results
            paginator = Paginator(totalWorkflowCases, filters["itemsPerPage"])
            try:
                page_of_workflow_cases = paginator.page(filters["pageNumber"])
            except (EmptyPage, PageNotAnInteger):
                page_of_workflow_cases = paginator.page(1)

            # Enrich workflow cases
            page_of_workflow_cases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(page_of_workflow_cases)
            page_of_workflow_cases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(page_of_workflow_cases)
            page_of_workflow_cases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(page_of_workflow_cases)
            page_of_workflow_cases = self.extractsheetHelper.AddExtractsToWorkflowCases(page_of_workflow_cases)

            # Fetch criteria lists
            report_statuses = self.dataServices.GetReportStatus()
            priorities = self.dataServices.GetDNAPriority()
            disease_indications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'CLL')
            reasons_for_disease_indications = self.dataServices.GetDNAReasonForDiseaseIndication(
                filters["diseaseIndicationCode1"], filters["diseaseIndicationCode2"], filters["diseaseIndicationCode3"]
            ) or []

            # Add descriptions if missing
            reasons_for_disease_indications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""), "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
                for reason in reasons_for_disease_indications
            ]

            # Prepare context for rendering
            context = {
                "criteriaDateFrom": filters["dateFrom"],
                "criteriaDateTo": filters["dateTo"],
                "Title": self.title,
                "workflowCases": page_of_workflow_cases,
                "itemsPerPage": filters["itemsPerPage"],
                "criteriaReportStatuses": report_statuses,
                "criteriaReportStatus": filters["reportStatus"],
                "criteriaPriorities": priorities,
                "criteriaPriority": filters["priority"],
                "criteriaDiseaseIndications": disease_indications,
                "criteriaDiseaseIndication1": filters["diseaseIndicationCode1"],
                "criteriaDiseaseIndication2": filters["diseaseIndicationCode2"],
                "criteriaDiseaseIndication3": filters["diseaseIndicationCode3"],
                "criteriaReasonsForDiseaseIndications": reasons_for_disease_indications,
                "criteriaReasonForDiseaseIndication1": filters["reasonForDiseaseIndication1"],
                "criteriaReasonForDiseaseIndication2": filters["reasonForDiseaseIndication2"],
                "criteriaReasonForDiseaseIndication3": filters["reasonForDiseaseIndication3"],
                "criteriaSurname": filters["lastName"],
                "criteriaLabnumber": filters["labNumber"],
                "criteriaNoResult": filters["noResultStatus"],
                "searchCount": len(totalWorkflowCases),
            }
            return render(request, self.template_name, context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": f"CLLSearch.get : {str(ex)}"
            }
            return render(request, self.template_name, context)

class RBCRSearch(TemplateView):
    template_name = "R-BCRSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return redirect("LoginPage")

            # Default values for filters
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

            # Retrieve search filters and pagination parameters
            _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or (datetime.today() - timedelta(days=60))
            _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or (datetime.today() + timedelta(days=30))
            _itemsPerPage = int(request.GET.get("items_per_page", 20))  # Default to 20 items per page
            page = request.GET.get("page", 1)

            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            # Retrieve additional filters from the request
            _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or _reportStatus
            _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
            _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or _diseaseIndicationCode1
            _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or _diseaseIndicationCode2
            _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or _diseaseIndicationCode3
            _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or _reasonForDiseaseIndication1
            _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String) or _reasonForDiseaseIndication2
            _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String) or _reasonForDiseaseIndication3
            _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
            _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or _labNumber
            _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or _noResultStatus

            # Retrieve filtered workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'RBCR', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3,
                request.user.username, _lastName, _labNumber, _RefKey, _noResultStatus
            )

            # Apply data transformations
            _totalWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_totalWorkflowCases)
            _totalWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_totalWorkflowCases)

            # Ensure no NoneType values in workflow cases
            for case in _totalWorkflowCases:
                case['DaysRemaining'] = case.get('DaysRemaining', 0)  # Default to 0 if None
                case['ActualPriorityOrder'] = case.get('ActualPriorityOrder', 0)
                case['Priority'] = case.get('Priority', "Unknown")
                case['REPORT_STATUS'] = case.get('REPORT_STATUS', "Pending")

            # Fetch reasons for dropdowns
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3
            ) or []

            # Add descriptions if missing
            _reasonsForDiseaseIndications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""), "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
                for reason in _reasonsForDiseaseIndications
            ]

            # Paginate results
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                paginated_cases = paginator.page(page)
            except PageNotAnInteger:
                paginated_cases = paginator.page(1)
            except EmptyPage:
                paginated_cases = paginator.page(paginator.num_pages)

            # Prepare query parameters for pagination
            query_params = request.GET.copy()
            query_params.pop("page", None)  # Remove 'page' parameter to construct the base query string
            base_query_string = urlencode(query_params)

            # Context for rendering
            context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": paginated_cases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": self.dataServices.GetReportStatus(),
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": self.dataServices.GetDNAPriority(),
                "criteriaPriority": _priority,
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'RBCR'),
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaReasonForDiseaseIndication3": _reasonForDiseaseIndication3,
                "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases),
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": len(_totalWorkflowCases),
                "page_obj": paginated_cases,  # Use this in the template for pagination
                "base_query_string": base_query_string,
            }
            return render(request, self.template_name, context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": f"RBCRSearch.get : {ex}"
            }
            return render(request, self.template_name, context)

class FALSearch(TemplateView):  # F-AML/F-ALL
    template_name = "FALSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return redirect("LoginPage")

            # Default filter values
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

            # Retrieve search filters and pagination parameters
            _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or (datetime.today() - timedelta(days=60))
            _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or (datetime.today() + timedelta(days=30))
            _itemsPerPage = int(request.GET.get("items_per_page", 20))  # Default to 20 items per page
            page = request.GET.get("page", 1)

            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            # Retrieve additional filters from the request
            _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or _reportStatus
            _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
            _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or _diseaseIndicationCode1
            _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or _diseaseIndicationCode2
            _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or _diseaseIndicationCode3
            _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or _reasonForDiseaseIndication1
            _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String) or _reasonForDiseaseIndication2
            _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String) or _reasonForDiseaseIndication3
            _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
            _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or _labNumber
            _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or _noResultStatus

            # Retrieve filtered workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'FAL', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3,
                request.user.username, _lastName, _labNumber, _RefKey, _noResultStatus
            )

            # Apply data transformations
            _totalWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_totalWorkflowCases)
            _totalWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_totalWorkflowCases)

            # Ensure no NoneType values in workflow cases
            for case in _totalWorkflowCases:
                case['DaysRemaining'] = case.get('DaysRemaining', 0)  # Default to 0 if None
                case['ActualPriorityOrder'] = case.get('ActualPriorityOrder', 0)
                case['Priority'] = case.get('Priority', "Unknown")
                case['REPORT_STATUS'] = case.get('REPORT_STATUS', "Pending")

            # Fetch reasons for dropdowns
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3
            ) or []

            # Add descriptions if missing
            _reasonsForDiseaseIndications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""), "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
                for reason in _reasonsForDiseaseIndications
            ]

            # Paginate results
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                paginated_cases = paginator.page(page)
            except PageNotAnInteger:
                paginated_cases = paginator.page(1)
            except EmptyPage:
                paginated_cases = paginator.page(paginator.num_pages)

            # Prepare query parameters for pagination
            query_params = request.GET.copy()
            query_params.pop("page", None)  # Remove 'page' parameter to construct the base query string
            base_query_string = urlencode(query_params)

            # Context for rendering
            context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": paginated_cases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": self.dataServices.GetReportStatus(),
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": self.dataServices.GetDNAPriority(),
                "criteriaPriority": _priority,
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'FAL'),
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaReasonForDiseaseIndication3": _reasonForDiseaseIndication3,
                "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases),
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": len(_totalWorkflowCases),
                "page_obj": paginated_cases,  # Use this in the template for pagination
                "base_query_string": base_query_string,
            }
            return render(request, self.template_name, context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": f"FALSearch.get : {ex}"
            }
            return render(request, self.template_name, context)

class HaemOncSearch(TemplateView):  # All Molecular
    template_name = "EverythingSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return redirect("LoginPage")

            # Default filter values
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

            # Retrieve filters and pagination parameters
            _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or (datetime.today() - timedelta(days=60))
            _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or (datetime.today() + timedelta(days=30))
            _itemsPerPage = int(request.GET.get("items_per_page", 20))  # Default to 20 items per page
            page = request.GET.get("page", 1)

            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            # Retrieve additional filters from the request
            _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or _reportStatus
            _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
            _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or _diseaseIndicationCode1
            _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or _diseaseIndicationCode2
            _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or _diseaseIndicationCode3
            _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or _reasonForDiseaseIndication1
            _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String) or _reasonForDiseaseIndication2
            _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String) or _reasonForDiseaseIndication3
            _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
            _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or _labNumber
            _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or _noResultStatus

            # Retrieve filtered workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', 'ONCOLOGY BMT', '', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3,
                request.user.username, _lastName, _labNumber, _RefKey, _noResultStatus
            )

            # Apply data transformations
            _totalWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_totalWorkflowCases)
            _totalWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_totalWorkflowCases)

            # Ensure no NoneType values in workflow cases
            for case in _totalWorkflowCases:
                case['DaysRemaining'] = case.get('DaysRemaining', 0)  # Default to 0 if None
                case['ActualPriorityOrder'] = case.get('ActualPriorityOrder', 0)
                case['Priority'] = case.get('Priority', "Unknown")
                case['REPORT_STATUS'] = case.get('REPORT_STATUS', "Pending")

            # Fetch reasons for dropdowns
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3
            ) or []

            # Add descriptions if missing
            _reasonsForDiseaseIndications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""), "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
                for reason in _reasonsForDiseaseIndications
            ]

            # Paginate results
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                paginated_cases = paginator.page(page)
            except PageNotAnInteger:
                paginated_cases = paginator.page(1)
            except EmptyPage:
                paginated_cases = paginator.page(paginator.num_pages)

            # Prepare query parameters for pagination
            query_params = request.GET.copy()
            query_params.pop("page", None)  # Remove 'page' parameter to construct the base query string
            base_query_string = urlencode(query_params)

            # Context for rendering
            context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": paginated_cases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": self.dataServices.GetReportStatus(),
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": self.dataServices.GetDNAPriority(),
                "criteriaPriority": _priority,
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', ''),
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaReasonForDiseaseIndication3": _reasonForDiseaseIndication3,
                "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases),
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": len(_totalWorkflowCases),
                "page_obj": paginated_cases,  # Use this in the template for pagination
                "base_query_string": base_query_string,
            }
            return render(request, self.template_name, context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": f"EverythingSearch.get : {ex}"
            }
            return render(request, self.template_name, context)

class GLHPanHaemSearch(TemplateView):  # Pan-Haem Search
    template_name = "GLHPanHaemSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return redirect("LoginPage")

            # Default filter values
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

            # Retrieve filters and pagination parameters
            _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or (datetime.today() - timedelta(days=60))
            _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or (datetime.today() + timedelta(days=90))
            _itemsPerPage = int(request.GET.get("items_per_page", 20))  # Default to 20 items per page
            page = request.GET.get("page", 1)

            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            # Retrieve additional filters from the request
            _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or _reportStatus
            _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
            _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or _diseaseIndicationCode1
            _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or _diseaseIndicationCode2
            _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or _diseaseIndicationCode3
            _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or _reasonForDiseaseIndication1
            _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String) or _reasonForDiseaseIndication2
            _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String) or _reasonForDiseaseIndication3
            _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
            _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or _labNumber
            _refKey = self.utilities.GetRequestKey(request, "ddlCriteriaRefKey", enumDataType.String) or _refKey
            _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or _noResultStatus

            # Retrieve filtered workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'PanHaem', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3,
                request.user.username, _lastName, _labNumber, _refKey, _noResultStatus
            )

            # Apply data transformations
            _totalWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_totalWorkflowCases)
            _totalWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_totalWorkflowCases)

            # Ensure no NoneType values in workflow cases
            for case in _totalWorkflowCases:
                case['DaysRemaining'] = case.get('DaysRemaining', 0)  # Default to 0 if None
                case['ActualPriorityOrder'] = case.get('ActualPriorityOrder', 0)
                case['Priority'] = case.get('Priority', "Unknown")
                case['REPORT_STATUS'] = case.get('REPORT_STATUS', "Pending")

            # Fetch reasons for dropdowns
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3
            ) or []

            # Add descriptions if missing
            _reasonsForDiseaseIndications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""), "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
                for reason in _reasonsForDiseaseIndications
            ]

            # Paginate results
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                paginated_cases = paginator.page(page)
            except PageNotAnInteger:
                paginated_cases = paginator.page(1)
            except EmptyPage:
                paginated_cases = paginator.page(paginator.num_pages)

            # Prepare query parameters for pagination
            query_params = request.GET.copy()
            query_params.pop("page", None)  # Remove 'page' parameter to construct the base query string
            base_query_string = urlencode(query_params)

            # Context for rendering
            context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": paginated_cases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": self.dataServices.GetReportStatus(),
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": self.dataServices.GetDNAPriority(),
                "criteriaPriority": _priority,
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'PanHaem'),
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaRefKey": _refKey,
                "criteriaRefKeys": self.dataServices.GetDNARefKey(_diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3),
                "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases),
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": len(_totalWorkflowCases),
                "page_obj": paginated_cases,  # Use this in the template for pagination
                "base_query_string": base_query_string,
            }
            return render(request, self.template_name, context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": f"GLHPanHaemSearch.get : {ex}"
            }
            return render(request, self.template_name, context)

class RNASearch(TemplateView):
    template_name = "RNASearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return redirect("LoginPage")

            # Default filter values
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

            # Retrieve filters and pagination parameters
            _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or (datetime.today() - timedelta(days=60))
            _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or (datetime.today() + timedelta(days=30))
            _itemsPerPage = int(request.GET.get("items_per_page", 20))  # Default to 20 items per page
            page = request.GET.get("page", 1)

            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            # Retrieve additional filters from the request
            _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or _reportStatus
            _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
            _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or _diseaseIndicationCode1
            _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or _diseaseIndicationCode2
            _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or _diseaseIndicationCode3
            _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or _reasonForDiseaseIndication1
            _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String) or _reasonForDiseaseIndication2
            _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String) or _reasonForDiseaseIndication3
            _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
            _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or _labNumber
            _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or _noResultStatus

            # Retrieve filtered workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'RNA', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3,
                request.user.username, _lastName, _labNumber, _RefKey, _noResultStatus
            )

            # Apply data transformations
            _totalWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_totalWorkflowCases)
            _totalWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_totalWorkflowCases)

            # Ensure no NoneType values in workflow cases
            for case in _totalWorkflowCases:
                case['DaysRemaining'] = case.get('DaysRemaining', 0)  # Default to 0 if None
                case['ActualPriorityOrder'] = case.get('ActualPriorityOrder', 0)
                case['Priority'] = case.get('Priority', "Unknown")
                case['REPORT_STATUS'] = case.get('REPORT_STATUS', "Pending")

            # Fetch reasons for dropdowns
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3
            ) or []

            # Add descriptions if missing
            _reasonsForDiseaseIndications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""), "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
                for reason in _reasonsForDiseaseIndications
            ]

            # Paginate results
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                paginated_cases = paginator.page(page)
            except PageNotAnInteger:
                paginated_cases = paginator.page(1)
            except EmptyPage:
                paginated_cases = paginator.page(paginator.num_pages)

            # Prepare query parameters for pagination
            query_params = request.GET.copy()
            query_params.pop("page", None)  # Remove 'page' parameter to construct the base query string
            base_query_string = urlencode(query_params)

            # Context for rendering
            context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": paginated_cases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": self.dataServices.GetReportStatus(),
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": self.dataServices.GetDNAPriority(),
                "criteriaPriority": _priority,
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'RNA'),
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases),
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": len(_totalWorkflowCases),
                "page_obj": paginated_cases,  # Use this in the template for pagination
                "base_query_string": base_query_string,
            }
            return render(request, self.template_name, context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": f"RNASearch.get : {ex}"
            }
            return render(request, self.template_name, context)
