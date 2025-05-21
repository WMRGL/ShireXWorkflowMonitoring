from ShireXWorkflowMonitoring.DataServices import ShireData

# Define the Worksheet class to handle operations related to worksheets in workflow cases - MW
class Worksheet:
    # Initialize the dataServices attribute with an instance of ShireData for database interactions - MW
    def __init__(self):
        self.dataServices = ShireData()

    # Method to add worksheet test results to each workflow case page - MW
    def AddWorksheetTestResultsToWorkflowCases(self, pPageOfWorkflowCases):
        _pageOfWorkflowCases = pPageOfWorkflowCases
        # Loop through each row in the provided page of workflow cases - MW
        for row in _pageOfWorkflowCases:
            labNumber = row['LABNO'] # Retrieve lab number from the row - MW
            indication = row['DISEASE_CODE'] # Retrieve disease code (indication) from the row - MW
            wsResults = self.dataServices.GetSampleWorksheetResults(labNumber, indication) # Retrieve worksheet results for the current lab number and indication - MW
            worksheetListString = self.CompileWorksheetListString(wsResults) # Compile a string of worksheet results - MW
            row['WORKSHEETS'] = worksheetListString # Assign the strinSg to the 'WORKSHEETS' key in the row - MW
        return _pageOfWorkflowCases # Return the modified page of workflow cases - MW

    # Method to compile worksheet list string from worksheet results - MW
    def CompileWorksheetListString(self, pWsResults):
        _wsResults = pWsResults
        worksheetListString = "" # Initialize an empty string to store worksheet information - MW
        for wsRow in _wsResults:
            # Extract and process worksheet details - MW
            worksheet, worksheetColour = self.ProcessWorksheetDetails(wsRow)
            test, result, highlightColour = self.ProcessTestResultDetails(wsRow)
            # Assemble the worksheet information string with HTML styling - MW
            worksheetListString += "<span style='color: " + worksheetColour + "'>" + worksheet + \
                                   " / </span><span style='color: " + highlightColour + "'>" + \
                                   test + ': ' + result + "</span><br><br>"
        return worksheetListString # Return the final assembled string - MW

    # Method to process worksheet details and determine the colouring logic - MW
    def ProcessWorksheetDetails(self, pWsRow):
        _wsRow = pWsRow

        worksheet = _wsRow.get('WORKSHEET', '')
        firstCheck = _wsRow.get('FIRST_RESULT_BY', '')
        secondCheck = _wsRow.get('FIRST_RESULT_CHECKED_BY', '')
        worksheetColour = "green" if secondCheck else "orange" if firstCheck else "red"
        return worksheet, worksheetColour

    # Method to process test and result details, handling missing data - MW
    def ProcessTestResultDetails(self, pWsRow):
        _wsRow = pWsRow

        test = _wsRow.get('TEST', 'Missing Test Data')
        result = _wsRow.get('RESULT', 'unknown result') if _wsRow.get('RESULT') else ''
        highlightColour = _wsRow.get('HighlightColour', 'black') if _wsRow.get('HighlightColour') else ''
        return test, result, highlightColour

        # Method to extract a list of surnames from the given workflow cases - MW
    def GetListOfSurnamesFromWorkflowCases(self, pWorkflowCases):
        _workflowCases = pWorkflowCases

        lastnameSet = set()  # Use a set for unique entries - MW
        for row in _workflowCases:
            lastname = row.get('LASTNAME', '')  # Extract the last name from the row - MW
            lastnameSet.add(lastname)  # Add to the set for uniqueness - MW
        sortedLastNames = sorted(list(lastnameSet))  # Convert to a sorted list - MW
        return sortedLastNames  # Return the sorted list of unique last names - MW

    # Method to add tests without worksheets to workflow cases - MW
    def AddTestsWithNoWorksheetsToWorkflowCases(self, pPageOfWorkflowCases):
        _pageOfWorkflowCases = pPageOfWorkflowCases

        for row in _pageOfWorkflowCases:
            labNumber = row['LABNO']
            indication = row['DISEASE_CODE']
            testsNoWorksheet = self.dataServices.GetSampleTestsNotAllocatedToWorksheet(labNumber, indication)  # Retrieve tests not allocated to worksheets - MW
            if testsNoWorksheet:
                noWsString = self.CompileTestsNoWorksheetString(testsNoWorksheet)  # Compile a string of tests without worksheets - MW
                existingWsString = row.get('WORKSHEETS', '')
                row['WORKSHEETS'] = existingWsString + noWsString if existingWsString else noWsString  # Append or assign the string to the 'WORKSHEETS' key - MW
        return _pageOfWorkflowCases  # Return the modified page of workflow cases - MW

    # Helper method to compile a string of tests that are not allocated to any worksheet - MW
    def CompileTestsNoWorksheetString(self, pTestsNoWorksheet):
        _testsNoWorksheet = pTestsNoWorksheet

        noWsString = "<span>Tests not allocated to w/s: "
        for item in _testsNoWorksheet:
            testName = item.get("TEST", "Unknown Test")
            noWsString += testName + ", "
        noWsString = noWsString.rstrip(", ") + "</span>"  # Remove trailing comma and add closing tag - MW
        return noWsString  # Return the compiled string - MW

    # Method to convert empty strings in the 'WORKSHEETS' column to None - MW
    def ConvertWorksheetsColumnEmptyStringToNone(self, pPageOfWorkflowCases):
        _pageOfWorkflowCases = pPageOfWorkflowCases

        for row in _pageOfWorkflowCases:
            if not row.get('WORKSHEETS'):  # Check if 'WORKSHEETS' is empty or None - MW
                row['WORKSHEETS'] = None  # Set 'WORKSHEETS' to None - MW
        return _pageOfWorkflowCases  # Return the modified page of workflow cases - MW



# Define the ExtractSheet class with similar structured methods - MW
# The ExtractSheet class focuses on handling extract sheets with methods like AddExtractsToWorkflowCases - MW
class ExtractSheet:
    # Initialize the dataServices attribute with an instance of ShireData for database interactions - MW
    def __init__(self):
        self.dataServices = ShireData()

    # Method to add extract sheet information to each page of workflow cases - MW
    def AddExtractsToWorkflowCases(self, pPageOfWorkflowCases):
        _pageOfWorkflowCases = pPageOfWorkflowCases

        for row in _pageOfWorkflowCases:
            labNumber = row['LABNO']
            extracts = self.dataServices.GetSampleExtracts(labNumber)
            row['EXTRACTSHEETS'] = self.CompileExtractString(extracts)

            conc_values = []
            for e in extracts:
                raw_conc = e.get("CONC")
                try:
                    if raw_conc is not None and str(raw_conc).strip() != "":
                        conc_float = float(raw_conc)
                        conc_values.append(conc_float)
                except (ValueError, TypeError):
                    continue

            if row.get("CONC") in [None, "", "N/A"]:
                row["CONC"] = max(conc_values) if conc_values else "N/A"

        return _pageOfWorkflowCases

    # Helper method to compile a string representation of extract sheets from extract data - MW
    def CompileExtractString(self, pExtracts):
        _extracts = pExtracts

        extractListString = ""
        for extract in _extracts:
            # Extract necessary fields from each extract record - MW
            extractionMethod = extract.get('EXTRACTION_METHOD', 'Unknown Method')
            extractDate = extract.get('EXTRACTION_DATE', '')
            extractSheet = extract.get('EXTRACT_SHEET', '')

            # Determine the color for extract sheet based on its completion status - MW
            extractSheetColor = "green" if extractSheet else "red"

            # Format extract date if available - MW
            if extractDate:
                extractDateFormatted = extractDate.strftime("%d/%m/%Y")
            else:
                extractDateFormatted = "Date Unknown"

            # Assemble the extract information into a HTML styled string - MW
            extractListString += f"<span style='color: {extractSheetColor};'>{extractionMethod} on {extractDateFormatted}</span><br>"

        return extractListString  # Return the compiled string of extract sheet information - MW