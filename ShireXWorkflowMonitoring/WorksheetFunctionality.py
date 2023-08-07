from ShireXWorkflowMonitoring.DataServices import ShireData


class Worksheet:
    dataServices = ShireData()

    def AddWorksheetTestResultsToWorkflowCases(self, _pageOfWorkflowCases):
        # An extension routine for the various workflow search routines
        _previousLabNumber = ""
        _previousIndication = ""

        for _row in _pageOfWorkflowCases:
            _labNumber = _row['LABNO']
            _indication = _row['DISEASE_CODE']
            _row['WORKSHEETS'] = ""
            # _row['RESULTS_OUTSTANDING'] = "no"
            # _row['WORKSHEET_OUTSTANDING'] = "yes"

            if _labNumber != _previousLabNumber or (_labNumber == _previousLabNumber and _indication != _previousIndication):
                # If the lab number is different, compile the worksheet/test/result information
                _wsResults = self.dataServices.GetSampleWorksheetResults(_labNumber, _indication)

                # _worksheetList = ["", ]
                # _testResultList = ["", ]

                _worksheetListString = ""

                for _wsRow in _wsResults:
                    # For each worksheet/test/result
                    _worksheet = _wsRow['WORKSHEET']
                    _worksheetFirstCheck = _wsRow['FIRST_RESULT_BY']
                    _worksheetSecondCheck = _wsRow['FIRST_RESULT_CHECKED_BY']
                    if (_wsRow['TEST']) is None:
                        _test = 'Missing Test Data'
                        _result = 'unknown result'
                    else:
                        _test = _wsRow['TEST']
                        _result = _wsRow['RESULT']
                    _highlightColour = _wsRow['HighlightColour']
                    _retest = _wsRow['RETEST']

                    _worksheetColour = "green"

                    if _worksheetSecondCheck is None or _worksheetSecondCheck == "":
                        _worksheetColour = "orange"
                    else:
                        if _worksheetFirstCheck is None or _worksheetFirstCheck == "":
                            _worksheetColour = "red"

                    if _highlightColour is None:
                        _highlightColour = "black"

                    if _retest is None:
                        _retest = 0         # False

                    _reTestString = ""
                    if _retest == -1:
                        _reTestString = " (A)"

                    # _row['WORKSHEET_OUTSTANDING'] = "no"

                    if (_result is None) or (_result == ''):
                        # _row['RESULTS_OUTSTANDING'] = "yes"
                        _result = ""

                    _worksheetListString = _worksheetListString + "<span style='color: " + _worksheetColour + "'>" + \
                        _worksheet + _reTestString + " / " + "</span><span style='color: " +\
                        _highlightColour + "'>" + _test + ': ' + _result + "<span><br><br>"
                    # If the worksheet is not in the list
                    # i.e. index() fails, add it, otherwise move on
                    # try:
                    #     _worksheetList.index(_worksheet)
                    # except:
                    #     _worksheetList.append(_worksheet)
                    #
                    # try:
                    #     _testResultList.append(_test + ': ' + _result)
                    # except:
                    #     # Do nothing
                    #     _stuff = 1

                # _worksheetList.remove("")
                # _testResultList.remove("")

                # _worksheetListString = ''.join(_worksheetList)
                # _testResultListString = ''.join(_testResultList)

                # _row['WORKSHEETS'] = _worksheetListString + " / " + _testResultListString

                _wsListString = ""

                if _worksheetListString.__len__() > 0:
                    # Remove the last set of <br><br>
                    _len = len(_worksheetListString)

                    _wsListString = _worksheetListString[0:(_len - 8)]

                _row['WORKSHEETS'] = _wsListString

            _previousLabNumber = _labNumber
            _previousIndication = _indication

        return _pageOfWorkflowCases

    def GetListOfSurnamesFromWorkflowCases(self, _workflowCases):
        # An extension routine for the various workflow search routines
        _previousLabNumber = ""

        _lastnameList = ["", ]

        for _row in _workflowCases:
            _lastname = _row['LASTNAME']

            try:
                _lastnameList.index(_lastname)
            except Exception:
                _lastnameList.append(_lastname)

        _sortedListOfLastNames = sorted(_lastnameList)

        return _sortedListOfLastNames

    def AddTestsWithNoWorksheetsToWorkflowCases(self, _pageOfWorkflowCases):
        # An extension routine for the various workflow search routines
        _previousLabNumber = ""
        _previousIndication = ""

        for _row in _pageOfWorkflowCases:
            _labNumber = _row['LABNO']
            _indication = _row['DISEASE_CODE']
            _noWsString = ""

            if _labNumber != _previousLabNumber or (_labNumber == _previousLabNumber and _indication != _previousIndication):
                # If the lab number is different, compile the information
                _testsNoWorksheet = self.dataServices.GetSampleTestsNotAllocatedToWorksheet(_labNumber, _indication)

                _worksheetListString = _row['WORKSHEETS']

                if _testsNoWorksheet.__len__() > 0:
                    if _worksheetListString.__len__() > 0:
                        _noWsString = "<br><br><span>Tests not allocated to w/s: "
                    else:
                        _noWsString = "<span>Tests not allocated to w/s: "

                    for _item in _testsNoWorksheet:
                        _testName = _item["TEST"]

                        _noWsString = _noWsString + _testName + ", "

                    # Remove the last comma and close the span
                    _len = len(_noWsString)

                    _noWsString = _noWsString[0:(_len - 3)] + "</span>"

                    _row['WORKSHEETS'] = _worksheetListString + _noWsString

            _previousLabNumber = _labNumber
            _previousIndication = _indication

        return _pageOfWorkflowCases

    def ConvertWorksheetsColumnEmptyStringToNone(self, _pageOfWorkflowCases):

        for _row in _pageOfWorkflowCases:
            if _row['WORKSHEETS'] == "" or _row['WORKSHEETS'] == " ":
                _row['WORKSHEETS'] = None

        return _pageOfWorkflowCases


class ExtractSheet:
    dataServices = ShireData()

    def AddExtractsToWorkflowCases(self, _pageOfWorkflowCases):
        # An extension routine for the various workflow search routines
        _previousLabNumber = ""

        for _row in _pageOfWorkflowCases:

            _labNumber = _row['LABNO']
            _row['EXTRACTSHEETS'] = ""

            if _labNumber != _previousLabNumber:
                _esResults = self.dataServices.GetSampleExtracts(_labNumber)
                _extractListString = ""
                _extractDate = ""
                _extract = ""
                _extractsheet = ""

                for _esRow in _esResults:
                    _extract = _esRow['EXTRACTION_METHOD']

                    if _esRow['EXTRACTION_DATE'] is not None:
                        _extractDate = str(_esRow['EXTRACTION_DATE'].strftime("%d/%m/%Y"))[0:10]

                    if _esRow['EXTRACT_SHEET'] is not None:
                        _extractsheet = _esRow['EXTRACT_SHEET']

                    _extractsheetColour = "green"

                    if (_extractDate is None or _extractDate == ""):
                        _extractDate = ""
                        _extractsheetColour = "orange"
                    else:
                        if (_extractsheet is None or _extractsheet == ""):
                            _extractsheet = ""
                            _extractsheetColour = "red"

                    _extractListString = _extractListString + "<span style='color: " + _extractsheetColour + \
                    "'>" + _extract + "</span>" + "<span><br><br>"
                    _esListString = ""

                    if _extractListString.__len__() > 0:
                       _len = len(_extractListString)

                    _esListString = _extractListString  [0:(_len - 8)]

                    _row['EXTRACTSHEETS'] = _esListString
                    #_row['EXTRACTSHEETS'] = _extractListString

            _previousLabNumber = _labNumber

        return _pageOfWorkflowCases
