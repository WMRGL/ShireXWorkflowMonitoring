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

    def GetDNAWorksheetResults(self, _LabNumber):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetDNAWorksheetResults(%s)}", (_LabNumber,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results