from ShireXWorkflowMonitoring.CommonFunctionality import UtilityFunctions
from ShireXWorkflowMonitoring.CommonFunctionality import enumDataType
from django.db import connection

# Define the ShireData class to handle data retrieval and manipulation for the ShireXWorkflowMonitoring application - MW
class ShireData:
    # Instantiate the UtilityFunctions class for utility methods - MW
    utilities = UtilityFunctions()

    # Method to retrieve DNA workflow cases from the database based on various criteria - MW
    def GetDNAWorkflowCases(self, _indicationCategory1, _indicationCategory2, _workFlow, _dateFrom, _dateTo, _reportStatus, _priority,
                            _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonCode1,
                            _reasonCode2, _reasonCode3, _username, _surname, _labNumber, _RefKey, _NoResultStatus):
        # Using a database cursor to execute a stored procedure - MW
        with connection.cursor() as _cursor:
            # Execute the stored procedure with provided parameters - MW
            _cursor.execute("{CALL dbo.uspShireXGetDNAWorkflowCases(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
                            "%s, %s, %s, %s, %s)}", (_indicationCategory1, _indicationCategory2, _workFlow, _dateFrom, _dateTo, _reportStatus,
                                                     _priority, _diseaseIndicationCode1, _diseaseIndicationCode2,
                                                     _diseaseIndicationCode3, _reasonCode1, _reasonCode2, _reasonCode3,
                                                     _username, _surname, _labNumber, _RefKey, _NoResultStatus))

            # Convert the cursor result to a list of dictionaries for easier manipulation - MW
            _workflowCases = self.utilities.ConvertCursorListToDict(_cursor)

            # Return the workflow cases - MW
            return _workflowCases

    # Method to retrieve sample indication, report, and billing information from the database - MW
    def GetSampleIndicationReportBill(self, _LabNumber):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSampleIndicationReportBill(%s)}", (_LabNumber,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    # Method to retrieve worksheet results for a sample based on lab number and indication - MW
    def GetSampleWorksheetResults(self, _LabNumber, _indication):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSampleWorksheetResults(%s,%s)}", (_LabNumber, _indication,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    # Method to retrieve extract sheet results for a sample based on lab number - MW
    def GetSampleExtracts(self, _LabNumber):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSampleExtractsheetResults(%s)}", (_LabNumber,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    # Method to set the 'AllocatedTo' field for a DNA sample in the database - MW
    def SetAllocatedToForDNA(self, _LabNumber, _StaffCode):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXSetAllocatedToForDNA(%s,%s)}", (_LabNumber, _StaffCode, ))

            return 1

    # Method to retrieve sample information from the database based on lab number - MW
    def GetSample(self, _LabNumber):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSample(%s)}", (_LabNumber,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    # Method to retrieve report status options from the database - MW
    def GetReportStatus(self):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetReportStatus()}")

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    # Method to retrieve DNA priority options from the database - MW
    def GetDNAPriority(self):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetDNAPriority()}")

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    # Method to check if a user has a specific permission - MW
    def UserHasPermission(self, _username, _permissionCode):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXUserHasPermission(%s, %s)}", (_username, _permissionCode))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            _retVal = False
            if _results.__len__() > 0:
                _retVal = True

            return _retVal

    # Method to retrieve disease indications for DNA testing - MW
    def GetDNADiseaseIndication(self, _indicationCategory1, _indicationCategory2, _workFlow):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetDNADiseaseIndication(%s,%s,%s)}", (_indicationCategory1, _indicationCategory2, _workFlow))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    # Method to retrieve reasons for disease indications in DNA testing - MW
    def GetDNAReasonForDiseaseIndication(self, _diseaseCode1, _diseaseCode2, _diseaseCode3):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetDNAReasonForDiseaseIndication(%s, %s, %s)}", (
                _diseaseCode1, _diseaseCode2, _diseaseCode3))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    # Method to retrieve tests not allocated to a worksheet for a sample - MW
    def GetSampleTestsNotAllocatedToWorksheet(self, _LabNumber, _indication):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSampleTestsNotAllocatedToWorksheet(%s,%s)}", (_LabNumber, _indication,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    # Method to retrieve all tests for a sample from the database - MW
    def GetSampleTests(self, _LabNumber):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSampleTests(%s)}", (_LabNumber,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    # Method to retrieve DNA reference keys based on disease codes - MW
    def GetDNARefKey(self, _diseaseCode1, _diseaseCode2, _diseaseCode3):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetDNARefKey(%s, %s, %s)}", (
                _diseaseCode1, _diseaseCode2, _diseaseCode3))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results