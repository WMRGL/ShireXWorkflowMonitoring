from ShireXWorkflowMonitoring.DataServices import ShireData


class Worksheet():
    dataServices = ShireData()

    def AddWorksheetTestResultsToWorkflowCases(self, _pageOfWorkflowCases):
        #An extension routine for the various workflow search routines
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
