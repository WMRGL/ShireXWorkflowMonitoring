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
            try:
                _itemsPerPage = int(request.GET.get("ddlCriteriaItemsPerPage", 20))
                if _itemsPerPage not in [20, 40, 50, 100]:  # Validate allowed values
                    _itemsPerPage = 20
            except ValueError:
                _itemsPerPage = 20

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
                "workflowCases": paginated_cases,  # Use this consistently in the template
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
                "page_obj": paginated_cases,  # Optionally remove if not needed
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
            _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or (
                        datetime.today() - timedelta(days=60))
            _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or (
                        datetime.today() + timedelta(days=30))


            # Retrieve the current page number
            page = request.GET.get("page", 1)
            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            # Extract additional filters
            _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus",
                                                         enumDataType.String) or _reportStatus
            _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
            _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1",
                                                                   enumDataType.String) or _diseaseIndicationCode1
            _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2",
                                                                   enumDataType.String) or _diseaseIndicationCode2
            _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or _diseaseIndicationCode3
            _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request,
                                                                        "ddlCriteriaReasonForDiseaseIndication1",
                                                                        enumDataType.String) or _reasonForDiseaseIndication1
            _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                                                                        "ddlCriteriaReasonForDiseaseIndication2",
                                                                        enumDataType.String) or _reasonForDiseaseIndication2
            _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                                                                        "ddlCriteriaReasonForDiseaseIndication3",
                                                                        enumDataType.String) or _reasonForDiseaseIndication3
            _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
            _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber",
                                                      enumDataType.String) or _labNumber
            _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult",
                                                           enumDataType.Integer) or _noResultStatus

            # Retrieve workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'MPN', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3,
                request.user.username, _lastName, _labNumber, _RefKey, _noResultStatus
            )

            # Apply data transformations
            _totalWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_totalWorkflowCases)
            _totalWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_totalWorkflowCases)

            # Validate and retrieve the number of items per page
            try:
                _itemsPerPage = int(request.GET.get("ddlCriteriaItemsPerPage", 20))
                if _itemsPerPage == -1:
                    _itemsPerPage = len(_totalWorkflowCases)
                elif _itemsPerPage not in [20, 40, 50, 100]:  # Allowed values
                    _itemsPerPage = 20
            except ValueError:
                _itemsPerPage = 20

            # Fetch reasons for dropdowns
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3
            ) or []

            # Add descriptions if missing
            _reasonsForDiseaseIndications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""),
                 "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
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
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "CriteriaReasonForDiseaseIndication3": _reasonForDiseaseIndication3,
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



            # Retrieve the current page number
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

            # Retrieve filtered workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'DAML', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3,
                request.user.username, _lastName, _labNumber, _RefKey, _noResultStatus
            )

            # Validate and retrieve the number of items per page
            try:
                _itemsPerPage = int(request.GET.get("ddlCriteriaItemsPerPage", 20))
                if _itemsPerPage == -1:
                    _itemsPerPage = len(_totalWorkflowCases)
                elif _itemsPerPage not in [20, 40, 50, 100]:  # Allowed values
                    _itemsPerPage = 20
            except ValueError:
                _itemsPerPage = 20

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

            # Validate and retrieve the number of items per page
            try:
                _itemsPerPage = int(request.GET.get("ddlCriteriaItemsPerPage", 20))
                if _itemsPerPage not in [20, 40, 50, 100]:  # Allowed values for items per page
                    _itemsPerPage = 20
            except ValueError:
                _itemsPerPage = 20

            # Retrieve the current page number
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

            # Retrieve the current page number
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

            # Validate and retrieve the number of items per page
            try:
                _itemsPerPage = int(request.GET.get("ddlCriteriaItemsPerPage", 20))
                if _itemsPerPage == -1:
                    _itemsPerPage = len(_totalWorkflowCases)
                elif _itemsPerPage not in [20, 40, 50, 100]:  # Allowed values
                    _itemsPerPage = 20
            except ValueError:
                _itemsPerPage = 20

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
    worksheetHelper = Worksheet()
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            is_postback = request.GET.__len__() > 0

            _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or ""  # Allow empty status
            _priority = ""
            _diseaseIndicationCode1 = ""
            _diseaseIndicationCode2 = ""
            _diseaseIndicationCode3 = ""
            _reasonForDiseaseIndication1 = "SNP Array Analysis"
            _lastName = ""
            _labNumber = ""
            _RefKey = ""
            _noResultStatus = 0

            _dateFrom = datetime.today() - timedelta(days=60)
            _dateTo = datetime.today() + timedelta(days=30)


            page = request.GET.get("page", 1)
            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1

            if is_postback:
                try:
                    _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or _dateFrom
                    _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or _dateTo
                    _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or _priority
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or _diseaseIndicationCode1
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or _diseaseIndicationCode2
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or _diseaseIndicationCode3
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or ""
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or _labNumber
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or _noResultStatus
                except Exception as e:
                    _dateFrom = datetime.today() - timedelta(days=60)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _itemsPerPage = 20

            # Fetch SNP workflow cases using corrected parameters
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'SNP', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, "", "",
                request.user.username, _lastName, _labNumber, _RefKey, _noResultStatus
            )

            # Process workflow cases
            _totalWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_totalWorkflowCases)
            _totalWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_totalWorkflowCases)
            _totalWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_totalWorkflowCases)

            # Validate and retrieve the number of items per page
            try:
                _itemsPerPage = int(request.GET.get("ddlCriteriaItemsPerPage", 20))
                if _itemsPerPage == -1:
                    _itemsPerPage = len(_totalWorkflowCases)
                elif _itemsPerPage not in [20, 40, 50, 100]:  # Allowed values
                    _itemsPerPage = 20
            except ValueError:
                _itemsPerPage = 20

            _searchCount = len(_totalWorkflowCases)
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                _pageOfWorkflowCases = paginator.page(page)
            except (EmptyPage, PageNotAnInteger):
                _pageOfWorkflowCases = paginator.page(1)

            query_params = request.GET.copy()
            query_params.pop("page", None)
            base_query_string = urlencode(query_params)

            context = {
                "criteriaDateFrom": _dateFrom,
                "criteriaDateTo": _dateTo,
                "Title": self.title,
                "workflowCases": _pageOfWorkflowCases,
                "itemsPerPage": _itemsPerPage,
                "criteriaReportStatuses": self.dataServices.GetReportStatus(),
                "criteriaReportStatus": _reportStatus,
                "criteriaPriorities": self.dataServices.GetDNAPriority(),
                "criteriaPriority": _priority,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'SNP'),
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": _searchCount,
                "page_obj": _pageOfWorkflowCases,
                "base_query_string": base_query_string,
            }

            return render(request, self.template_name, context)

        except Exception as ex:
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
            _lastName = ""
            _noResultStatus = 0
            _refKey = ""
            _labNumber = ""  # Added Lab Number filter

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
            _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or _lastName
            _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or _labNumber  # Retrieve Lab Number
            _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or _noResultStatus

            # Pagination logic
            try:
                page = int(page)
                if page < 1:
                    page = 1
            except ValueError:
                page = 1
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'ALL', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3,
                request.user.username, _lastName, _labNumber, _refKey, _noResultStatus  # Removed _noResultStatus filter
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
                "criteriaLabnumber": _labNumber,  # Added Lab Number to context
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

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.http import urlencode

class CLLSearch(TemplateView):
    template_name = "CLLSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            # Redirect if not logged in
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

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
                "itemsPerPage": 20,
            }

            # Override with GET parameters
            filters.update({
                "dateFrom": self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or filters["dateFrom"],
                "dateTo": self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or filters["dateTo"],
                "pageNumber": int(request.GET.get("page", 1)) if str(request.GET.get("page", 1)).isdigit() else 1,
                "itemsPerPage": self.utilities.GetRequestKey(request, "ddlCriteriaItemsPerPage", enumDataType.Integer) or filters["itemsPerPage"],
                "reportStatus": self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or filters["reportStatus"],
                "priority": self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or filters["priority"],
                "diseaseIndicationCode1": self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or filters["diseaseIndicationCode1"],
                "diseaseIndicationCode2": self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or filters["diseaseIndicationCode2"],
                "diseaseIndicationCode3": self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or filters["diseaseIndicationCode3"],
                "reasonForDiseaseIndication1": self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or filters["reasonForDiseaseIndication1"],
                "reasonForDiseaseIndication2": self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String) or filters["reasonForDiseaseIndication2"],
                "reasonForDiseaseIndication3": self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String) or filters["reasonForDiseaseIndication3"],
                "lastName": self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or filters["lastName"],
                "labNumber": self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or filters["labNumber"],
                "noResultStatus": self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or filters["noResultStatus"],
            })

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

            # Paginate results
            paginator = Paginator(totalWorkflowCases, filters["itemsPerPage"])
            try:
                page_obj = paginator.get_page(filters["pageNumber"])
            except (EmptyPage, PageNotAnInteger):
                page_obj = paginator.get_page(1)  # If error, fallback to page 1

            # Enrich workflow cases
            page_obj = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(page_obj)
            page_obj = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(page_obj)
            page_obj = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(page_obj)
            page_obj = self.extractsheetHelper.AddExtractsToWorkflowCases(page_obj)

            # Prepare base query string for pagination (preserving filters)
            query_params = request.GET.copy()
            query_params.pop("page", None)  # Remove `page` to avoid duplication
            query_params = {k: v for k, v in query_params.items() if v and v not in ["['']", '']}  # Remove empty values
            base_query_string = urlencode(query_params, doseq=True)  # Properly format list-based params

            # Prepare context
            context = {
                "criteriaDateFrom": filters["dateFrom"],
                "criteriaDateTo": filters["dateTo"],
                "Title": self.title,
                "workflowCases": page_obj,  # Make sure the template gets the correct pagination object
                "page_obj": page_obj,  # Ensure `page_obj` is in context
                "itemsPerPage": filters["itemsPerPage"],
                "criteriaReportStatuses": self.dataServices.GetReportStatus(),
                "criteriaReportStatus": filters["reportStatus"],
                "criteriaPriorities": self.dataServices.GetDNAPriority(),
                "criteriaPriority": filters["priority"],
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'CLL'),
                "criteriaDiseaseIndication1": filters["diseaseIndicationCode1"],
                "criteriaDiseaseIndication2": filters["diseaseIndicationCode2"],
                "criteriaDiseaseIndication3": filters["diseaseIndicationCode3"],
                "criteriaReasonsForDiseaseIndications": self.dataServices.GetDNAReasonForDiseaseIndication(
                    filters["diseaseIndicationCode1"], filters["diseaseIndicationCode2"], filters["diseaseIndicationCode3"]
                ) or [],
                "criteriaReasonForDiseaseIndication1": filters["reasonForDiseaseIndication1"],
                "criteriaReasonForDiseaseIndication2": filters["reasonForDiseaseIndication2"],
                "criteriaReasonForDiseaseIndication3": filters["reasonForDiseaseIndication3"],
                "criteriaSurname": filters["lastName"],
                "criteriaLabnumber": filters["labNumber"],
                "criteriaNoResult": filters["noResultStatus"],
                "searchCount": len(totalWorkflowCases),
                "base_query_string": base_query_string,  # Pass to template
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

            # Validate and retrieve the number of items per page
            try:
                _itemsPerPage = int(request.GET.get("ddlCriteriaItemsPerPage", 20))
                if _itemsPerPage not in [20, 40, 50, 100]:  # Allowed values
                    _itemsPerPage = 20
            except ValueError:
                _itemsPerPage = 20

            # Retrieve the current page number
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
            _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
            _noResultStatus = int(_noResultStatus) if str(_noResultStatus).isdigit() else 0  # Ensure it's an integer

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

            query_params = request.GET.copy()
            query_params.pop("page", None)  # Remove 'page' to avoid duplication
            query_params = {k: v for k, v in query_params.items() if v and v not in ["['']", '']}  # Filter out empty values
            base_query_string = urlencode(query_params, doseq=True)  # Ensure lists are formatted properly

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

            # Validate and retrieve the number of items per page
            try:
                _itemsPerPage = int(request.GET.get("ddlCriteriaItemsPerPage", 20))
                if _itemsPerPage not in [20, 40, 50, 100]:  # Allowed values
                    _itemsPerPage = 20
            except ValueError:
                _itemsPerPage = 20

            # Retrieve the current page number
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

            # Retrieve the current page number
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
            print(f"DEBUG: Filtering for last name = '{_lastName}'")
            matching_cases = [case for case in _totalWorkflowCases if case['LASTNAME'].lower() == _lastName.lower()]
            print(f"DEBUG: Found {len(matching_cases)} matching cases")

            # Validate and retrieve the number of items per page
            try:
                _itemsPerPage = int(request.GET.get("ddlCriteriaItemsPerPage", 20))
                if _itemsPerPage == -1:
                    _itemsPerPage = len(_totalWorkflowCases)
                elif _itemsPerPage not in [20, 40, 50, 100]:  # Allowed values
                    _itemsPerPage = 20
            except ValueError:
                _itemsPerPage = 20

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
                "page_obj": paginated_cases,
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

            # Validate and retrieve the number of items per page
            try:
                _itemsPerPage = int(request.GET.get("ddlCriteriaItemsPerPage", 20))
                if _itemsPerPage not in [20, 40, 50, 100]:  # Allowed values
                    _itemsPerPage = 20
            except ValueError:
                _itemsPerPage = 20

            # Retrieve the current page number
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
                "page_obj": paginated_cases,
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

            # Validate and retrieve the number of items per page
            try:
                _itemsPerPage = int(request.GET.get("ddlCriteriaItemsPerPage", 20))
                if _itemsPerPage not in [20, 40, 50, 100]:  # Allowed values
                    _itemsPerPage = 20
            except ValueError:
                _itemsPerPage = 20

            # Retrieve the current page number
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

            # **Filter cases to only include RNA_Sequencing**
            _totalWorkflowCases = [case for case in _totalWorkflowCases if case.get("REASON", "").strip() == "RNA_Sequencing"]

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