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


class BMTSearch(TemplateView):
    template_name = "BMTSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()       # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, pRequest):
        _request = pRequest

        try:
            if not _request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            if _request.GET.__len__() == 0:
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
            _RefKey = ""
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(_request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(_request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(_request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(_request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(_request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication1",
                                                                           enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication2",
                                                                           enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication3",
                                                                           enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(_request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(_request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=60)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                'ONCOLOGY BMT', '', 'BMT', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1,
                _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, _request.user.username, _lastName,
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

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('ONCOLOGY BMT', '', 'BMT')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication('BMT', '', '')

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
            return render(_request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "BMTSearch.get : " + str(ex)
            }

            return render(_request, self.template_name, context)


class MPNSearch(TemplateView):
    template_name = "MPNSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()       # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, pRequest):
        _request = pRequest
        try:
            if not _request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            if _request.GET.__len__() == 0:
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
            _RefKey = ""
            _showAlerts = False
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(_request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(_request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(_request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(_request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(_request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication1",
                                                                           enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication2",
                                                                           enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication3",
                                                                           enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(_request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(_request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaNoResult", enumDataType.Integer)
                    _showAlerts = self.utilities.GetRequestKey(_request, "ddlAlertCriteria", enumDataType.Boolean)

                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'MPN', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1,
                _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, _request.user.username, _lastName,
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
            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'MPN')
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3)
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

            return render(_request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "MPNSearch.get : " + str(ex)
            }

            return render(_request, self.template_name, context)


class DAMLSearch(TemplateView): #AML & MDS
    template_name = "D-AMLSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()       # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, pRequest):
        _request = pRequest

        try:
            if not _request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            if _request.GET.__len__() == 0:
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
            _RefKey = ""
            _noResultStatus = 0
            _searchCount = 0
            _url = _request.get_full_path

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(_request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(_request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(_request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(_request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(_request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication1",
                                                                           enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication2",
                                                                           enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication3",
                                                                           enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(_request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(_request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaNoResult", enumDataType.Integer)

                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'DAML', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1,
                _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, _request.user.username, _lastName,
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

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'DAML')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3)

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
                "returnURL": _url,
            }
            return render(_request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "DAMLSearch.get : " + str(ex)
            }

            return render(_request, self.template_name, context)


class BreakSearch(TemplateView):
    template_name = "BreakSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, pRequest):
        _request = pRequest

        try:
            if not _request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            if _request.GET.__len__() == 0:
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
            _RefKey = ""
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(_request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(_request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(_request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(_request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(_request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication1",
                                                                           enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication2",
                                                                           enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication3",
                                                                           enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(_request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(_request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'BREAK', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1,
                _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                _reasonForDiseaseIndication2,  _reasonForDiseaseIndication3, _request.user.username, _lastName,
                _labNumber,  _RefKey, _noResultStatus)
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

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'BREAK')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(_diseaseIndicationCode1,
                                                                                               _diseaseIndicationCode2,
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
                "criteriaSurnames": _listOfSurnames,
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": _searchCount,
            }
            return render(_request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "BreakSearch.get : " + str(ex)
            }

            return render(_request, self.template_name, context)


class RAMLSearch(TemplateView):
    template_name = "R-AMLSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self,pRequest):
        _request = pRequest

        try:
            if not _request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            if _request.GET.__len__() == 0:
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
            _RefKey = ""
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(_request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(_request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(_request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(_request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(_request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication1",
                                                                           enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication2",
                                                                           enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication3",
                                                                           enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(_request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(_request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'RAML', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1,
                _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, _request.user.username, _lastName,
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

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'RAML')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3)

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
            return render(_request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "RAMLSearch.get : " + str(ex)
            }

            return render(_request, self.template_name, context)


class SNPSearch(TemplateView):
    template_name = "SNPSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, pRequest):
        _request = pRequest

        try:
            if not _request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            if _request.GET.__len__() == 0:
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
            _RefKey = ""
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(_request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(_request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(_request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(_request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(_request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication1",
                                                                           enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication2",
                                                                           enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication3",
                                                                           enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    # _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                    #                                                            "ddlCriteriaReasonForDiseaseIndication2",
                    #                                                            enumDataType.String)
                    # _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                    #                                                            "ddlCriteriaReasonForDiseaseIndication3",
                    #                                                            enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(_request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(_request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', '', 'SNP', _dateFrom, _dateTo,
                                                                        _reportStatus, _priority,
                                                                        _diseaseIndicationCode1,
                                                                        _diseaseIndicationCode2,
                                                                        _diseaseIndicationCode3,
                                                                        _reasonForDiseaseIndication1,
                                                                        _reasonForDiseaseIndication2,
                                                                        _reasonForDiseaseIndication3,
                                                                        _request.user.username, _lastName, _labNumber,
                                                                        _RefKey,
                                                                        _noResultStatus)
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

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'SNP')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(_diseaseIndicationCode1,
                                                                                               _diseaseIndicationCode2,
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
                "criteriaSurnames": _listOfSurnames,
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": _searchCount,
            }
            return render(_request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "SNPSearch.get : " + str(ex)
            }

            return render(_request, self.template_name, context)


class ALLSearch(TemplateView):
    template_name = "ALLSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, pRequest):
        _request = pRequest

        try:
            if not _request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            if _request.GET.__len__() == 0:
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
            _RefKey = ""
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(_request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(_request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(_request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(_request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(_request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication1",
                                                                           enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication2",
                                                                           enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication3",
                                                                           enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(_request, "txtCriteriaLastname", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(_request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'ALL', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1,
                _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, _request.user.username, _lastName,
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

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'ALL')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(_diseaseIndicationCode1,
                                                                                               _diseaseIndicationCode2,
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
                "criteriaSurnames": _listOfSurnames,
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": _searchCount,
            }
            return render(_request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "ALLSearch.get : " + str(ex)
            }

            return render(_request, self.template_name, context)


class CLLSearch(TemplateView): #Lymphoid
    template_name = "CLLSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, pRequest):
        _request = pRequest

        try:
            if not _request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            if _request.GET.__len__() == 0:
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
            _RefKey = ""
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(_request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(_request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(_request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(_request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(_request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication1",
                                                                           enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication2",
                                                                           enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication3",
                                                                           enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(_request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(_request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'CLL', _dateFrom, _dateTo,  _reportStatus, _priority,  _diseaseIndicationCode1,
                _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, _request.user.username, _lastName,
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

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'CLL')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(_diseaseIndicationCode1,
                                                                                               _diseaseIndicationCode2,
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
                "criteriaSurnames": _listOfSurnames,
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": _searchCount,
            }
            return render(_request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "CLLSearch.get : " + str(ex)
            }

            return render(_request, self.template_name, context)


class RBCRSearch(TemplateView):
    template_name = "R-BCRSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, pRequest):
        _request = pRequest

        try:
            if not _request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            if _request.GET.__len__() == 0:
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
            _RefKey = ""
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(_request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(_request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(_request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(_request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(_request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication1",
                                                                           enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication2",
                                                                           enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication3",
                                                                           enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(_request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(_request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'RBCR', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1,
                _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, _request.user.username, _lastName,
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

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'RBCR')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(_diseaseIndicationCode1,
                                                                                               _diseaseIndicationCode2,
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
                "criteriaSurnames": _listOfSurnames,
                "criteriaSurname": _lastName,
                "criteriaLabnumber": _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": _searchCount,
            }
            return render(_request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "RBCRSearch.get : " + str(ex)
            }

            return render(_request, self.template_name, context)


class FALSearch(TemplateView): #F-AML/F-ALL
    template_name = "FALSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()       # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, pRequest):
        _request = pRequest
        try:
            if not _request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            if _request.GET.__len__() == 0:
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
            _RefKey = ""
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(_request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(_request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(_request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(_request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(_request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaDiseaseIndication1", enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaDiseaseIndication2", enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaDiseaseIndication3", enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(_request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(_request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'FAL', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1,
                _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, _request.user.username, _lastName,
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

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'FAL')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3)

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
            return render(_request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "FALSearch.get : " + str(ex)
            }

            return render(_request, self.template_name, context)


class HaemOncSearch(TemplateView): #All Molecular
    template_name = "EverythingSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, pRequest):
        _request = pRequest

        try:
            if not _request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            if _request.GET.__len__() == 0:
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
            _RefKey = ""
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(_request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(_request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(_request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(_request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(_request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication1",
                                                                           enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication2",
                                                                           enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication3",
                                                                           enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(_request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(_request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', 'ONCOLOGY BMT', '', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1,
                _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, _request.user.username, _lastName,
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

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', '')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3)

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
            return render(_request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "EverythingSearch.get : " + str(ex)
            }

            return render(_request, self.template_name, context)


class GLHPanHaemSearch(TemplateView):
    template_name = "GLHPanHaemSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, pRequest):
        _request = pRequest

        try:
            if not _request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            if _request.GET.__len__() == 0:
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
                    _dateFrom = self.utilities.GetRequestKey(_request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(_request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(_request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(_request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(_request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication1",
                                                                           enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication2",
                                                                           enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication3",
                                                                           enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(_request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(_request, "txtCriteriaLabnumber", enumDataType.String)
                    _refKey = self.utilities.GetRequestKey(_request, "ddlCriteriaRefKey", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaNoResult", enumDataType.Integer)

                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
               '2012_HAEM_ONC', '', 'PanHaem', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1,
               _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
               _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, _request.user.username, _lastName,
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

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'PanHaem')

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
            return render(_request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "WGSSearch.get : " + str(ex)
            }

            return render(_request, self.template_name, context)


class RNASearch(TemplateView):
    template_name = "RNASearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance
    extractsheetHelper = ExtractSheet()

    def get(self, pRequest):
        _request = pRequest
        try:
            if not _request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            # If logged in determine if a postback, before extracting the search filters
            if _request.GET.__len__() == 0:
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
            _RefKey = ""
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=60)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(_request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(_request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(request, "ddlCriteriaItemsPerPage",
                                                                 enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(_request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication1",
                                                                           enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication2",
                                                                           enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(_request, "ddlCriteriaDiseaseIndication3",
                                                                           enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(
                        _request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(_request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(_request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(_request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases(
                '2012_HAEM_ONC', '', 'RNA', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1,
                _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1,
                _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, _request.user.username, _lastName,
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

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '', 'RNA')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(
                _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3)

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
            return render(_request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "RAMLSearch.get : " + str(ex)
            }

            return render(_request, self.template_name, context)

