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

                #_worksheetList = ["", ]
                #_testResultList = ["", ]

                _worksheetListString = ""

                for _wsRow in _wsResults:
                    # For each worksheet/test/result
                    _worksheet = _wsRow['WORKSHEET']
                    _worksheetFirstCheck = _wsRow['FIRST_RESULT_BY']
                    _worksheetSecondCheck = _wsRow['SECOND_RESULT_BY']
                    _test = _wsRow['TEST']
                    _result = _wsRow['RESULT']
                    _highlightColour = _wsRow['HighlightColour']

                    _worksheetColour = "green"

                    if _worksheetSecondCheck == None or _worksheetSecondCheck == "":
                        _worksheetColour = "orange"
                    else:
                        if _worksheetFirstCheck == None or _worksheetFirstCheck == "":
                            _worksheetColour = "red"

                    if _highlightColour == None:
                        _highlightColour = "black"

                    _row['WORKSHEET_OUTSTANDING'] = "no"

                    if (_result == None) or (_result == ''):
                        _row['RESULTS_OUTSTANDING'] = "yes"
                        _result = ""

                    _worksheetListString =  _worksheetListString + "<span style='color: " + _worksheetColour + "'>" + _worksheet + " / " + "</span><span style='color: " + _highlightColour + "'>" + _test + ': ' + _result + "<span><br><br>"
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

                #_worksheetList.remove("")
                #_testResultList.remove("")

                #_worksheetListString = ''.join(_worksheetList)
                #_testResultListString = ''.join(_testResultList)

                #_row['WORKSHEETS'] = _worksheetListString + " / " + _testResultListString


                #Remove the last set of <br><br>
                _len = len(_worksheetListString)

                _wsListString = _worksheetListString[0:(_len - 8)]

                _row['WORKSHEETS'] = _wsListString

            _previousLabNumber = _labNumber

        return _pageOfWorkflowCases

    def GetListOfSurnamesFromWorkflowCases(self, _workflowCases):
        #An extension routine for the various workflow search routines
        _previousLabNumber = ""

        _lastnameList = ["", ]

        for _row in _workflowCases:
            _lastname = _row['LASTNAME']

            try:
                _lastnameList.index(_lastname)
            except:
                _lastnameList.append(_lastname)

        _sortedListOfLastNames = sorted(_lastnameList)

        return _sortedListOfLastNames