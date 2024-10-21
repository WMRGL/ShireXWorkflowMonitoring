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
import logging


# Define the class SolidCancerSearch which extends TemplateView - MW
class SolidCancerSearch(TemplateView):
    template_name = "SolidCancerSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()
    extractsheetHelper = ExtractSheet()

    def get(self, request):
        # _request = pRequest
        logger = logging.getLogger(__name__)

        try:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            _isPostBack = bool(request.GET)

            # Initialize search filters with default values
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
            _worksheet = self.utilities.GetRequestKey(request, "WORKSHEET", enumDataType.String) or ""
            _probe_primer = self.utilities.GetRequestKey(request, "PROBE_PRIMER", enumDataType.String) or ""
            _lane = self.utilities.GetRequestKey(request, "LANE", enumDataType.String) or ""

            logger.info("Worksheet: %s, Probe Primer: %s, Lane: %s", _worksheet, _probe_primer, _lane)

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = -1

            else:

                try:
                    _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(request, "txtPageNumber", enumDataType.Integer) or 1
                    _itemsPerPage = self.utilities.GetRequestKey(request, "ddlCriteriaItemsPerPage", enumDataType.Integer) or -1
                    _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String) or "NOTFINAL"
                    _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String) or ""
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or ""
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or ""
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or ""
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or ""
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String) or ""
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String) or ""
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String) or ""
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String) or ""
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer) or 0
                    logger.info("DateFrom: %s, DateTo: %s, PageNumber: %d, ItemsPerPage: %d", _dateFrom, _dateTo, _pageNumber, _itemsPerPage)
                    logger.info("ReportStatus: %s, Priority: %s, LastName: %s, LabNumber: %s", _reportStatus, _priority, _lastName, _labNumber)
                except Exception as ex:
                    _dateFrom = datetime.today() - timedelta(days=60)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = -1
                    logger.error("Exception during postback processing: %s", ex)

            logger.info("Before fetching workflow cases")

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_SOLID_CANCER', '2012_RARE_DIS', 'SC', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1,
                _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, request.user.username, _lastName,
                _labNumber, _RefKey, _noResultStatus)
            logger.info("Total workflow cases fetched: %d", len(_totalWorkflowCases))

            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)
            _searchCount = len(_totalWorkflowCases)
            logger.info("List of surnames: %s", _listOfSurnames)

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)
            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)
            #_pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)
            #_pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)
            #_pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)
            #_pageOfWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_pageOfWorkflowCases)
            _reportStatuses = self.dataServices.GetReportStatus()
            _priorities = self.dataServices.GetDNAPriority()
            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_SOLID_CANCER', '2012_RARE_DIS', 'SC')
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(_diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3)

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

            return render(request, self.template_name, _context)

        except Exception as ex:
            logger.error("Exception in SolidCancerSearch.get: %s", ex)
            context = {
                "Title": self.title,
                "errorMessage": "SCSearch.get : " + str(ex) if ex is not None else "Unknown error"
            }

            return render(request, self.template_name, context)


class WGSSearch(TemplateView):
    template_name = "WGSSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()
    extractsheetHelper = ExtractSheet()

    def get(self, pRequest):
        _request = pRequest

        try:
            if not _request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            _isPostBack = bool(_request.GET)

            # Initialize search filters with default values
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
                print(_dateFrom)
                _dateTo = datetime.today() + timedelta(days=30)
                print(_dateTo)
                _pageNumber = 1
                _itemsPerPage = -1
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(_request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(_request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(_request, "txtPageNumber", enumDataType.Integer) or 1
                    _itemsPerPage = self.utilities.GetRequestKey(_request, "ddlCriteriaItemsPerPage", enumDataType.Integer) or -1
                    _reportStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaStatus", enumDataType.String) or "NOTFINAL"
                    _priority = self.utilities.GetRequestKey(_request, "ddlCriteriaPriority", enumDataType.String) or ""
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication1", enumDataType.String) or ""
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication2", enumDataType.String) or ""
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication3", enumDataType.String) or ""
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(_request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String) or ""
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(_request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String) or ""
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(_request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String) or ""
                    _lastName = self.utilities.GetRequestKey(_request, "txtCriteriaLastname", enumDataType.String) or ""
                    _labNumber = self.utilities.GetRequestKey(_request, "txtCriteriaLabnumber", enumDataType.String) or ""
                    _refKey = self.utilities.GetRequestKey(_request, "ddlCriteriaRefKey", enumDataType.String) or ""
                    _noResultStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaNoResult", enumDataType.Integer) or 0
                except Exception:
                    _dateFrom = datetime.today() - timedelta(days=60)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = -1

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_SOLID_CANCER', '2012_OTHER', 'WGS', _dateFrom, _dateTo, _reportStatus, _priority,
                _diseaseIndicationCode1,
                _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, _request.user.username, _lastName,
                _labNumber, _refKey, _noResultStatus)

            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)
            _searchCount = len(_totalWorkflowCases)

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)
            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)
            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)
            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)
            _pageOfWorkflowCases = self.extractsheetHelper.AddExtractsToWorkflowCases(_pageOfWorkflowCases)

            _reportStatuses = self.dataServices.GetReportStatus()
            _priorities = self.dataServices.GetDNAPriority()
            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_SOLID_CANCER', '2012_OTHER', 'WGS')
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(_diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3)
            _refKeys = self.dataServices.GetDNARefKey(_diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3)
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
            return render(_request, self.template_name, context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "WGSSearch.get : " + str(ex) if ex is not None else "Unknown error"
            }

            return render(_request, self.template_name, context)
