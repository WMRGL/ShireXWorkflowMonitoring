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

class BMTSearch(TemplateView):
    template_name = "BMTSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()

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
            _reason = ""

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=365)
                _dateTo = datetime.today() + timedelta(days=7)
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
                    _reason = self.utilities.GetRequestKey(request, "txtCriteriaReason", enumDataType.String)
                except Exception as ex:
                    #If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=7)
                    _pageNumber = 1
                    _itemsPerPage = 20

            _workflowCases = Paginator(self.dataServices.GetDNAWorkflowCases(_dateFrom, _dateTo, _reportStatus, _priority, _reason), _itemsPerPage)

            _pageOfWorkflowCases = _workflowCases.page(_pageNumber)

            #For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            _pageOfWorkflowCases = self.AddWorksheetTestResultsToWorkflowCases(_pageOfWorkflowCases)

            # _previousLabNumber = ""
            #
            # for _row in _pageOfWorkflowCases:
            #     _labNumber = _row['LABNO']
            #     _row['WORKSHEETS'] = ""
            #     _row['RESULTS_OUTSTANDING'] = "no"
            #     _row['WORKSHEET_OUTSTANDING'] = "yes"
            #
            #     if _labNumber != _previousLabNumber:
            #         #If the lab number is different, compile the worksheet/test/result information
            #         _wsResults = self.dataServices.GetSampleWorksheetResults(_labNumber)
            #
            #         _worksheetList = ["",]
            #         _testResultList = ["",]
            #
            #         for _wsRow in _wsResults:
            #             #For each worksheet/test/result
            #             _worksheet = _wsRow['WORKSHEET']
            #             _test = _wsRow['TEST']
            #             _result = _wsRow['RESULT']
            #
            #             _row['WORKSHEET_OUTSTANDING'] = "no"
            #
            #             if (_result == None) or (_result == ''):
            #                 _row['RESULTS_OUTSTANDING'] = "yes"
            #                 _result = "No result"
            #
            #             #If the worksheet is not in the list
            #             #i.e. index() fails, add it, otherwise move on
            #             try:
            #                 _worksheetList.index(_worksheet)
            #             except:
            #                 _worksheetList.append(_worksheet)
            #
            #             try:
            #                 _testResultList.append(_test + ': ' + _result)
            #             except:
            #                 #Do nothing
            #                 _stuff = 1
            #
            #         _worksheetList.remove("")
            #         _testResultList.remove("")
            #
            #         _worksheetListString = ''.join(_worksheetList)
            #         _testResultListString = ''.join(_testResultList)
            #
            #         _row['WORKSHEETS'] = _worksheetListString + " / " + _testResultListString
            #
            #     _previousLabNumber = _labNumber

            #Codes for the search criteria
            _reportStatuses = self.dataServices.GetReportStatus()

            _priorities = self.dataServices.GetDNAPriority()

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
                "criteriaReason": _reason,
            }
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "BMTSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)

    def AddWorksheetTestResultsToWorkflowCases(self, _pageOfWorkflowCases):

        _previousLabNumber = ""

        for _row in _pageOfWorkflowCases:
            _labNumber = _row['LABNO']
            _row['WORKSHEETS'] = ""
            _row['RESULTS_OUTSTANDING'] = "no"
            _row['WORKSHEET_OUTSTANDING'] = "yes"

            if _labNumber != _previousLabNumber:
                # If the lab number is different, compile the worksheet/test/result information
                _wsResults = self.dataServices.GetSampleWorksheetResults(_labNumber)

                _worksheetList = ["", ]
                _testResultList = ["", ]

                for _wsRow in _wsResults:
                    # For each worksheet/test/result
                    _worksheet = _wsRow['WORKSHEET']
                    _test = _wsRow['TEST']
                    _result = _wsRow['RESULT']

                    _row['WORKSHEET_OUTSTANDING'] = "no"

                    if (_result == None) or (_result == ''):
                        _row['RESULTS_OUTSTANDING'] = "yes"
                        _result = "No result"

                    # If the worksheet is not in the list
                    # i.e. index() fails, add it, otherwise move on
                    try:
                        _worksheetList.index(_worksheet)
                    except:
                        _worksheetList.append(_worksheet)

                    try:
                        _testResultList.append(_test + ': ' + _result)
                    except:
                        # Do nothing
                        _stuff = 1

                _worksheetList.remove("")
                _testResultList.remove("")

                _worksheetListString = ''.join(_worksheetList)
                _testResultListString = ''.join(_testResultList)

                _row['WORKSHEETS'] = _worksheetListString + " / " + _testResultListString

            _previousLabNumber = _labNumber

        return _pageOfWorkflowCases

class SetAllocatedToForDNA(TemplateView):
    template_name = "SetAllocatedToForDNA.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()

    def get(self, request, _labNumber):

        try:

            _staff = STAFF.objects.get(LOGON_NAME=request.user.username)

            if _staff == None:
                _context = {
                    "labNumber": _labNumber,
                    "errorMessage": "The system cannot find the staff code from the username"
                }
                return render(request, self.template_name, _context)

            _retVal = self.dataServices.SetAllocatedToForDNA(_labNumber, _staff.STAFF_CODE)

            if _retVal != 1:
                _context = {
                    "labNumber": _labNumber,
                    "errorMessage": "The system attempted to set the Allocated to column for you, but failed at the database server.",
                }
                return render(request, self.template_name, _context)

            _context = {
                "labNumber" : _labNumber,
            }

            return render(request, self.template_name, _context)

        except Exception as ex:
            _context = {
                "labNumber" : _labNumber,
                "errorMessage": str(ex),
            }

            return render(request, self.template_name, _context)



