#Add Haem Onc specific classes in this file
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render

from django.urls import reverse
from django.views.generic import TemplateView
from ShireXWorkflowMonitoring.apps import ShireXWorkflowMonitoringConfig
from datetime import datetime
from datetime import timedelta
from ShireXWorkflowMonitoring.CommonFunctionality import UtilityFunctions
from ShireXWorkflowMonitoring.CommonFunctionality import enumDataType
from ShireXWorkflowMonitoring.DataServices import ShireData
from ShireXWorkflowMonitoring.models import STAFF
from django.core.paginator import Paginator
from ShireXWorkflowMonitoring.WorksheetFunctionality import Worksheet

class BMTSearch(TemplateView):
    template_name = "BMTSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()       #Composition, instead of inheritance

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            #If logged in determine if a postback, before extracting the search filters
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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(request, "ddlCriteriaItemsPerPage", enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    #If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=30)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            #_totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('ONCOLOGY BMT', '', '', '', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, request.user.username, _lastName, _labNumber, _noResultStatus)
            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('ONCOLOGY BMT', 'BMT', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, request.user.username, _lastName, _labNumber, _noResultStatus)

            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            #For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            #Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('ONCOLOGY BMT', 'BMT')

            #_reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(_diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3)
            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication('BMT','','')

            _context = {
                "criteriaDateFrom" : _dateFrom,
                "criteriaDateTo" : _dateTo,
                "Title": self.title,
                "workflowCases": _pageOfWorkflowCases,
                "itemsPerPage" : _itemsPerPage,
                "criteriaReportStatuses" : _reportStatuses,
                "criteriaReportStatus" : _reportStatus,
                "criteriaPriorities" : _priorities,
                "criteriaPriority" : _priority,
                "criteriaDiseaseIndications": _diseaseIndications,
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaReasonForDiseaseIndication3": _reasonForDiseaseIndication3,
                "criteriaSurnames": _listOfSurnames,
                "criteriaSurname" : _lastName,
                "criteriaLabnumber" : _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": _searchCount,
            }
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "BMTSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class MPNSearch(TemplateView):
    template_name = "MPNSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()       #Composition, instead of inheritance

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            #If logged in determine if a postback, before extracting the search filters
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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(request, "ddlCriteriaItemsPerPage", enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    #If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', 'MPN', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, request.user.username, _lastName, _labNumber, _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            #For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            #Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', 'MPN')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(_diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3)

            _context = {
                "criteriaDateFrom" : _dateFrom,
                "criteriaDateTo" : _dateTo,
                "Title": self.title,
                "workflowCases": _pageOfWorkflowCases,
                "itemsPerPage" : _itemsPerPage,
                "criteriaReportStatuses" : _reportStatuses,
                "criteriaReportStatus" : _reportStatus,
                "criteriaPriorities" : _priorities,
                "criteriaPriority" : _priority,
                "criteriaDiseaseIndications": _diseaseIndications,
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaReasonForDiseaseIndication3": _reasonForDiseaseIndication3,
                "criteriaSurnames": _listOfSurnames,
                "criteriaSurname" : _lastName,
                "criteriaLabnumber" : _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": _searchCount,
            }
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "MPNSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class DAMLSearch(TemplateView):
    template_name = "D-AMLSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()       #Composition, instead of inheritance

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            #If logged in determine if a postback, before extracting the search filters
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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(request, "ddlCriteriaItemsPerPage", enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    #If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', 'D-AML', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, request.user.username, _lastName, _labNumber, _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            #For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            #Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', 'D-AML')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(_diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3)

            _context = {
                "criteriaDateFrom" : _dateFrom,
                "criteriaDateTo" : _dateTo,
                "Title": self.title,
                "workflowCases": _pageOfWorkflowCases,
                "itemsPerPage" : _itemsPerPage,
                "criteriaReportStatuses" : _reportStatuses,
                "criteriaReportStatus" : _reportStatus,
                "criteriaPriorities" : _priorities,
                "criteriaPriority" : _priority,
                "criteriaDiseaseIndications": _diseaseIndications,
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaReasonForDiseaseIndication3": _reasonForDiseaseIndication3,
                "criteriaSurnames": _listOfSurnames,
                "criteriaSurname" : _lastName,
                "criteriaLabnumber" : _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": _searchCount,
            }
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "DAMLSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class BreakSearch(TemplateView):
    template_name = "BreakSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance

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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
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
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication1",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication2",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication3",
                                                                                enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', 'BREAK', _dateFrom, _dateTo,
                                                                        _reportStatus, _priority,
                                                                        _diseaseIndicationCode1,
                                                                        _diseaseIndicationCode2,
                                                                        _diseaseIndicationCode3,
                                                                        _reasonForDiseaseIndication1,
                                                                        _reasonForDiseaseIndication2,
                                                                        _reasonForDiseaseIndication3,
                                                                        request.user.username, _lastName, _labNumber,
                                                                        _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', 'BREAK')

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
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "BreakSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class MDSSearch(TemplateView):
    template_name = "MDSSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance

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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
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
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication1",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication2",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication3",
                                                                                enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', 'MDS', _dateFrom, _dateTo,
                                                                        _reportStatus, _priority,
                                                                        _diseaseIndicationCode1,
                                                                        _diseaseIndicationCode2,
                                                                        _diseaseIndicationCode3,
                                                                        _reasonForDiseaseIndication1,
                                                                        _reasonForDiseaseIndication2,
                                                                        _reasonForDiseaseIndication3,
                                                                        request.user.username, _lastName, _labNumber,
                                                                        _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', 'MDS')

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
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "MDSSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class RAMLSearch(TemplateView):
    template_name = "R-AMLSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance

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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
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
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication1",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication2",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication3",
                                                                                enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', 'R-AML', _dateFrom, _dateTo,
                                                                        _reportStatus, _priority,
                                                                        _diseaseIndicationCode1,
                                                                        _diseaseIndicationCode2,
                                                                        _diseaseIndicationCode3,
                                                                        _reasonForDiseaseIndication1,
                                                                        _reasonForDiseaseIndication2,
                                                                        _reasonForDiseaseIndication3,
                                                                        request.user.username, _lastName, _labNumber,
                                                                        _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', 'R-AML')

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
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "RAMLSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class AMLOddsSearch(TemplateView):
    template_name = "AMLOddsSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance

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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
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
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication1",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication2",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication3",
                                                                                enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', 'AML Odds', _dateFrom, _dateTo,
                                                                        _reportStatus, _priority,
                                                                        _diseaseIndicationCode1,
                                                                        _diseaseIndicationCode2,
                                                                        _diseaseIndicationCode3,
                                                                        _reasonForDiseaseIndication1,
                                                                        _reasonForDiseaseIndication2,
                                                                        _reasonForDiseaseIndication3,
                                                                        request.user.username, _lastName, _labNumber,
                                                                        _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', 'AML Odds')

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
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "AMLOddsSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class SNPSearch(TemplateView):
    template_name = "SNPSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance

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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
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
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication1",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication2",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication3",
                                                                                enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', 'SNP', _dateFrom, _dateTo,
                                                                        _reportStatus, _priority,
                                                                        _diseaseIndicationCode1,
                                                                        _diseaseIndicationCode2,
                                                                        _diseaseIndicationCode3,
                                                                        _reasonForDiseaseIndication1,
                                                                        _reasonForDiseaseIndication2,
                                                                        _reasonForDiseaseIndication3,
                                                                        request.user.username, _lastName, _labNumber,
                                                                        _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', 'SNP')

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
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "SNPSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class WGSSearch(TemplateView):
    template_name = "WGSSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance

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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
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
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication1",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication2",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication3",
                                                                                enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_OTHER', 'WGS', _dateFrom, _dateTo,
                                                                        _reportStatus, _priority,
                                                                        _diseaseIndicationCode1,
                                                                        _diseaseIndicationCode2,
                                                                        _diseaseIndicationCode3,
                                                                        _reasonForDiseaseIndication1,
                                                                        _reasonForDiseaseIndication2,
                                                                        _reasonForDiseaseIndication3,
                                                                        request.user.username, _lastName, _labNumber,
                                                                        _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_OTHER', 'WGS')

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
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "WGSSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class ALLSearch(TemplateView):
    template_name = "ALLSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance

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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
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
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication1",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication2",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication3",
                                                                                enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', 'ALL', _dateFrom, _dateTo,
                                                                        _reportStatus, _priority,
                                                                        _diseaseIndicationCode1,
                                                                        _diseaseIndicationCode2,
                                                                        _diseaseIndicationCode3,
                                                                        _reasonForDiseaseIndication1,
                                                                        _reasonForDiseaseIndication2,
                                                                        _reasonForDiseaseIndication3,
                                                                        request.user.username, _lastName, _labNumber,
                                                                        _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', 'ALL')

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
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "ALLSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class CLLSearch(TemplateView):
    template_name = "CLLSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance

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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
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
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication1",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication2",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication3",
                                                                                enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', 'CLL', _dateFrom, _dateTo,
                                                                        _reportStatus, _priority,
                                                                        _diseaseIndicationCode1,
                                                                        _diseaseIndicationCode2,
                                                                        _diseaseIndicationCode3,
                                                                        _reasonForDiseaseIndication1,
                                                                        _reasonForDiseaseIndication2,
                                                                        _reasonForDiseaseIndication3,
                                                                        request.user.username, _lastName, _labNumber,
                                                                        _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', 'CLL')

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
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "CLLSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class DHCLSearch(TemplateView):
    template_name = "D-HCLSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance

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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
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
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication1",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication2",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication3",
                                                                                enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', 'D-HCL', _dateFrom, _dateTo,
                                                                        _reportStatus, _priority,
                                                                        _diseaseIndicationCode1,
                                                                        _diseaseIndicationCode2,
                                                                        _diseaseIndicationCode3,
                                                                        _reasonForDiseaseIndication1,
                                                                        _reasonForDiseaseIndication2,
                                                                        _reasonForDiseaseIndication3,
                                                                        request.user.username, _lastName, _labNumber,
                                                                        _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', 'D-HCL')

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
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "DHCLSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class DONCSearch(TemplateView):
    template_name = "D-ONCSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance

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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
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
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication1",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication2",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication3",
                                                                                enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', 'D-ONC', _dateFrom, _dateTo,
                                                                        _reportStatus, _priority,
                                                                        _diseaseIndicationCode1,
                                                                        _diseaseIndicationCode2,
                                                                        _diseaseIndicationCode3,
                                                                        _reasonForDiseaseIndication1,
                                                                        _reasonForDiseaseIndication2,
                                                                        _reasonForDiseaseIndication3,
                                                                        request.user.username, _lastName, _labNumber,
                                                                        _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', 'D-ONC')

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
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "DONCSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class DCSSearch(TemplateView):
    template_name = "D-CSSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance

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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
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
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication1",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication2",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication3",
                                                                                enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', 'D-CS', _dateFrom, _dateTo,
                                                                        _reportStatus, _priority,
                                                                        _diseaseIndicationCode1,
                                                                        _diseaseIndicationCode2,
                                                                        _diseaseIndicationCode3,
                                                                        _reasonForDiseaseIndication1,
                                                                        _reasonForDiseaseIndication2,
                                                                        _reasonForDiseaseIndication3,
                                                                        request.user.username, _lastName, _labNumber,
                                                                        _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', 'D-CS')

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
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "DCSSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class RBCRSearch(TemplateView):
    template_name = "R-BCRSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance

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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
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
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication1",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication2",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication3",
                                                                                enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', 'R-BCR', _dateFrom, _dateTo,
                                                                        _reportStatus, _priority,
                                                                        _diseaseIndicationCode1,
                                                                        _diseaseIndicationCode2,
                                                                        _diseaseIndicationCode3,
                                                                        _reasonForDiseaseIndication1,
                                                                        _reasonForDiseaseIndication2,
                                                                        _reasonForDiseaseIndication3,
                                                                        request.user.username, _lastName, _labNumber,
                                                                        _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', 'R-BCR')

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
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "RBCRSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class FALSearch(TemplateView):
    template_name = "FALSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()       #Composition, instead of inheritance

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            #If logged in determine if a postback, before extracting the search filters
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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
                _pageNumber = 1
                _itemsPerPage = 20
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime)
                    _pageNumber = self.utilities.GetRequestKey(request, "txtPageNumber", enumDataType.Integer)
                    _itemsPerPage = self.utilities.GetRequestKey(request, "ddlCriteriaItemsPerPage", enumDataType.Integer)
                    _reportStatus = self.utilities.GetRequestKey(request, "ddlCriteriaStatus", enumDataType.String)
                    _priority = self.utilities.GetRequestKey(request, "ddlCriteriaPriority", enumDataType.String)
                    _diseaseIndicationCode1 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication1", enumDataType.String)
                    _diseaseIndicationCode2 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication2", enumDataType.String)
                    _diseaseIndicationCode3 = self.utilities.GetRequestKey(request, "ddlCriteriaDiseaseIndication3", enumDataType.String)
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication1", enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication2", enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request, "ddlCriteriaReasonForDiseaseIndication3", enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    #If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', 'FAL', _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonForDiseaseIndication1, _reasonForDiseaseIndication2, _reasonForDiseaseIndication3, request.user.username, _lastName, _labNumber, _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            #For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            #Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', 'FAL')

            _reasonsForDiseaseIndications = self.dataServices.GetDNAReasonForDiseaseIndication(_diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3)

            _context = {
                "criteriaDateFrom" : _dateFrom,
                "criteriaDateTo" : _dateTo,
                "Title": self.title,
                "workflowCases": _pageOfWorkflowCases,
                "itemsPerPage" : _itemsPerPage,
                "criteriaReportStatuses" : _reportStatuses,
                "criteriaReportStatus" : _reportStatus,
                "criteriaPriorities" : _priorities,
                "criteriaPriority" : _priority,
                "criteriaDiseaseIndications": _diseaseIndications,
                "criteriaDiseaseIndication1": _diseaseIndicationCode1,
                "criteriaDiseaseIndication2": _diseaseIndicationCode2,
                "criteriaDiseaseIndication3": _diseaseIndicationCode3,
                "criteriaReasonsForDiseaseIndications": _reasonsForDiseaseIndications,
                "criteriaReasonForDiseaseIndication1": _reasonForDiseaseIndication1,
                "criteriaReasonForDiseaseIndication2": _reasonForDiseaseIndication2,
                "criteriaReasonForDiseaseIndication3": _reasonForDiseaseIndication3,
                "criteriaSurnames": _listOfSurnames,
                "criteriaSurname" : _lastName,
                "criteriaLabnumber" : _labNumber,
                "criteriaNoResult": _noResultStatus,
                "searchCount": _searchCount,
            }
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "FALSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class EverythingSearch(TemplateView):
    template_name = "EverythingSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()
    worksheetHelper = Worksheet()  # Composition, instead of inheritance

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
            _noResultStatus = 0
            _searchCount = 0

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=30)
                _dateTo = datetime.today() + timedelta(days=30)
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
                    _reasonForDiseaseIndication1 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication1",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication2 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication2",
                                                                                enumDataType.String)
                    _reasonForDiseaseIndication3 = self.utilities.GetRequestKey(request,
                                                                                "ddlCriteriaReasonForDiseaseIndication3",
                                                                                enumDataType.String)
                    _lastName = self.utilities.GetRequestKey(request, "txtCriteriaLastname", enumDataType.String)
                    _labNumber = self.utilities.GetRequestKey(request, "txtCriteriaLabnumber", enumDataType.String)
                    _noResultStatus = self.utilities.GetRequestKey(request, "ddlCriteriaNoResult", enumDataType.Integer)
                except Exception as ex:
                    # If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=30)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _totalWorkflowCases = self.dataServices.GetDNAWorkflowCases('2012_HAEM_ONC', '', _dateFrom, _dateTo,
                                                                        _reportStatus, _priority,
                                                                        _diseaseIndicationCode1,
                                                                        _diseaseIndicationCode2,
                                                                        _diseaseIndicationCode3,
                                                                        _reasonForDiseaseIndication1,
                                                                        _reasonForDiseaseIndication2,
                                                                        _reasonForDiseaseIndication3,
                                                                        request.user.username, _lastName, _labNumber,
                                                                        _noResultStatus)
            _listOfSurnames = self.worksheetHelper.GetListOfSurnamesFromWorkflowCases(_totalWorkflowCases)

            _searchCount = _totalWorkflowCases.__len__()

            _workflowCases = Paginator(_totalWorkflowCases, _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            # For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.worksheetHelper.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.AddTestsWithNoWorksheetsToWorkflowCases(_pageOfWorkflowCases)

            _pageOfWorkflowCases = self.worksheetHelper.ConvertWorksheetsColumnEmptyStringToNone(_pageOfWorkflowCases)

            # Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

            _diseaseIndications = self.dataServices.GetDNADiseaseIndication('2012_HAEM_ONC', '')

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
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "EverythingSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

class SetAllocatedToForDNA(TemplateView):
    #This class may need to be moved to the CommonFunctionality module
    template_name = "SetAllocatedToForDNA.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()

    def get(self, request, _labNumber, _workflowName):

        try:

            _staffList = None
            _staff = None

            _staffQuery = STAFF.objects.filter(LOGON_NAME=request.user.username, EMPLOYMENT_END_DATE__isnull=True)

            if _staffQuery == None or _staffQuery.__len__() == 0:
                _context = {
                    "labNumber": _labNumber,
                    "errorMessage": "The system cannot find the staff code from the username"
                }
                return render(request, self.template_name, _context)
            else:
                #Convert the queryset, which should only have one record
                #to a single instance of the Staff record
                for _item in _staffQuery:
                    _staff = _item

            _isSupervisor = "N"

            _permissionName = "Is" + _workflowName + "Supervisor"

            _hasPermission = self.dataServices.UserHasPermission(request.user.username, _permissionName)

            if _hasPermission:
                _isSupervisor = "Y"
                _staffList = STAFF.objects.all

            _cancelURL = "HaemOnc" + _workflowName + "Search"

            _context = {
                "labNumber" : _labNumber,
                "staffList" : _staffList,
                "staff" : _staff,
                "isSupervisor" : _isSupervisor,
                "workflowName" : _workflowName,
                "cancelURL" : _cancelURL,
            }

            return render(request, self.template_name, _context)

        except Exception as ex:
            _context = {
                "labNumber" : _labNumber,
                "errorMessage": str(ex),
            }

            return render(request, self.template_name, _context)

    def post(self, request, _labNumber, _workflowName):

        try:

            _staffCode = self.utilities.PostRequestKey(request, "ddlStaffCode", enumDataType.String)

            _retVal = self.dataServices.SetAllocatedToForDNA(_labNumber, _staffCode)

            if _retVal != 1:
                _context = {
                    "labNumber": _labNumber,
                    "errorMessage": "The system attempted to set the Allocated to column for you, but failed at the database server.",
                }
                return render(request, self.template_name, _context)

            _urlName = "HaemOnc" + _workflowName + "Search"

            return HttpResponseRedirect(reverse(_urlName))


        except Exception as ex:
            _context = {
                "labNumber" : _labNumber,
                "errorMessage": str(ex),
            }

            return render(request, self.template_name, _context)



