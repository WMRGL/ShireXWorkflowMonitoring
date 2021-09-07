#Add Haem Onc specific classes in this file
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

class BMTSearch(TemplateView):
    template_name = "BMTSearch.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()

    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            #Otherwise
            if request.GET.__len__() == 0:
                _isPostBack = False
            else:
                _isPostBack = True

            if not _isPostBack:
                _dateFrom = datetime.today() - timedelta(days=365)
                _dateTo = datetime.today() + timedelta(days=7)
                #_pageNumber = 1
            else:
                try:
                    _dateFrom = self.utilities.GetRequestKey(request, "txtCriteriaDateFrom", enumDataType.Datetime)
                    _dateTo = self.utilities.GetRequestKey(request, "txtCriteriaDateTo", enumDataType.Datetime)
                    # _pageNumber = self.utilities.GetRequestKey(request, "txtPageNumber", enumDataType.Integer)
                except Exception as ex:
                    #If any errors occur return the default criteria
                    _dateFrom = datetime.today() - timedelta(days=365)
                    _dateTo = datetime.today() + timedelta(days=7)
                    # _pageNumber = 1

            # with connection.cursor() as _cursor:
            #     _cursor.execute("{CALL dbo.uspShireXGetDNAWorkflowCases(%s, %s, %s)}", ('ONCOLOGY BMT', _dateFrom, _dateTo))
            #     _workflowCases = self.utilities.ConvertCursorListToDict(_cursor)

            _workflowCases = self.dataServices.GetDNAWorkflowCases(_dateFrom, _dateTo)

            #For each Lab No/Reason/Bill line extract the worksheet summary for that Lab No
            #TODO refactor the following to a separate method, when we know what the final output is.
            _previousLabNumber = ""

            for _row in _workflowCases:
                _labNumber = _row['LABNO']
                _row['WORKSHEETS'] = ""
                _row['RESULTS_OUTSTANDING'] = "no"
                _row['WORKSHEET_OUTSTANDING'] = "yes"

                if _labNumber != _previousLabNumber:
                    #If the lab number is different, compile the worksheet/test/result information
                    _wsResults = self.dataServices.GetSampleWorksheetResults(_labNumber)

                    _worksheetList = ["",]
                    _testResultList = ["",]

                    for _wsRow in _wsResults:
                        #For each worksheet/test/result
                        _worksheet = _wsRow['WORKSHEET']
                        _test = _wsRow['TEST']
                        _result = _wsRow['RESULT']

                        _row['WORKSHEET_OUTSTANDING'] = "no"

                        if (_result == None) or (_result == ''):
                            _row['RESULTS_OUTSTANDING'] = "yes"
                            _result = "No result"

                        #If the worksheet is not in the list
                        #i.e. index() fails, add it, otherwise move on
                        try:
                            _worksheetList.index(_worksheet)
                        except:
                            _worksheetList.append(_worksheet)

                        try:
                            _testResultList.append(_test + ': ' + _result)
                        except:
                            #Do nothing
                            _stuff = 1

                    _worksheetList.remove("")
                    _testResultList.remove("")

                    _worksheetListString = ''.join(_worksheetList)
                    _testResultListString = ''.join(_testResultList)

                    _row['WORKSHEETS'] = _worksheetListString + " / " + _testResultListString

                _previousLabNumber = _labNumber

            _context = {
                "criteriaDateFrom" : _dateFrom,
                "criteriaDateTo" : _dateTo,
                "Title": self.title,
                "workflowCases": _workflowCases,
            }
            return render(request, self.template_name, _context)

        except Exception as ex:
            context = {
                "Title": self.title,
                "errorMessage": "BMTSearch.get : " + str(ex)
            }

            return render(request, self.template_name, context)


