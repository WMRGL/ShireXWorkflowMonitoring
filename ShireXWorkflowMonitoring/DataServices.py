from ShireXWorkflowMonitoring.CommonFunctionality import UtilityFunctions
from ShireXWorkflowMonitoring.CommonFunctionality import enumDataType
from django.db import connection

class ShireData():

    utilities = UtilityFunctions()

    def GetDNAWorkflowCases(self, _dateFrom, _dateTo):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetDNAWorkflowCases(%s, %s, %s)}", ('ONCOLOGY BMT', _dateFrom, _dateTo))

            _workflowCases = self.utilities.ConvertCursorListToDict(_cursor)

            return _workflowCases

    def GetSampleIndicationReportBill(self, _LabNumber):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSampleIndicationReportBill(%s)}", (_LabNumber,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    def GetSampleWorksheetResults(self, _LabNumber):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSampleWorksheetResults(%s)}", (_LabNumber,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    def SetAllocatedToForDNA(self, _LabNumber, _StaffCode):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXSetAllocatedToForDNA(%s,%s)}", (_LabNumber, _StaffCode, ))

            return 1