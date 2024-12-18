from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from ShireXWorkflowMonitoring.apps import ShireXWorkflowMonitoringConfig
from datetime import datetime, timedelta
from ShireXWorkflowMonitoring.CommonFunctionality import UtilityFunctions, enumDataType
from ShireXWorkflowMonitoring.DataServices import ShireData
from ShireXWorkflowMonitoring.WorksheetFunctionality import Worksheet, ExtractSheet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
import logging
from datetime import datetime, timedelta

# Add Haem Onc specific classes in this file
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import datetime, timedelta
import logging

from urllib.parse import urlencode


class SolidCancerSearch(TemplateView):
    template_name = "SolidCancerSearch.html"
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
                '2012_SOLID_CANCER', '2012_RARE_DIS', 'SC', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3,
                _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3,
                request.user.username, "", "", "", 0
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
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('2012_SOLID_CANCER', '', 'SC'),
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
            print(f"ERROR: Exception in SolidCancerSearch.get - {ex}")
            context = {
                "Title": self.title,
                "errorMessage": f"SolidCancerSearch.get : {ex}"
            }
            return render(request, self.template_name, context)

class WGSSearch(TemplateView):
    template_name = "WGSSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse("LoginPage"))

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

            # Retrieve search filters and pagination parameters
            _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime) or (datetime.today() - timedelta(days=60))
            _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime) or (datetime.today() + timedelta(days=30))
            _itemsPerPage = int(request.GET.get("ddlCriteriaItemsPerPage", 20))  # Default to 20 items per page
            _pageNumber = int(request.GET.get("page", 1))

            # Fetch filters from request
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

            # Fetch workflow cases
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_SOLID_CANCER', '2012_OTHER', 'WGS', _dateFrom, _dateTo, _reportStatus, _priority,
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

            # Fetch additional data for filters
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(_diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3) or []

            # Add descriptions if missing
            _reasonsForDiseaseIndications = [
                {"REASON_CODE": reason.get("REASON_CODE", ""), "REASON_DESCRIPTION": reason.get("REASON_DESCRIPTION", reason.get("REASON_CODE", ""))}
                for reason in _reasonsForDiseaseIndications
            ]

            _refKeys = self.dataServices.GetDNARefKey(_diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3)

            # Pagination logic
            paginator = Paginator(_totalWorkflowCases, _itemsPerPage)
            try:
                _pageOfWorkflowCases = paginator.page(_pageNumber)
            except PageNotAnInteger:
                _pageOfWorkflowCases = paginator.page(1)
            except EmptyPage:
                _pageOfWorkflowCases = paginator.page(paginator.num_pages)

            # Prepare query string for pagination
            query_params = request.GET.copy()
            query_params.pop("page", None)  # Exclude 'page' from query string
            base_query_string = urlencode(query_params)

            # Prepare context
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
                "criteriaDiseaseIndications": self.dataServices.GetDNADiseaseIndication('2012_SOLID_CANCER', '2012_OTHER', 'WGS'),
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaReasonForDiseaseIndication3": _reasonForDiseaseIndication3,
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaRefKey": _refKey,
                "criteriaRefKeys": _refKeys,
                "criteriaSurnames": self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases),
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": len(_totalWorkflowCases),
                "page_obj": _pageOfWorkflowCases,
                "base_query_string": base_query_string,
            }

            return render(request, self.template_name, context)

        except Exception as ex:
            logger = logging.getLogger(__name__)
            logger.error(f"WGSSearch.get: {ex}")
            return render(request, self.template_name, {"Title": self.title, "errorMessage": f"WGSSearch.get : {ex}"})

