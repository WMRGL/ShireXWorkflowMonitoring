from ShireXWorkflowMonitoring.CommonFunctionality import UtilityFunctions
from ShireXWorkflowMonitoring.CommonFunctionality import enumDataType
from django.db import connection

class ShireData():

    utilities = UtilityFunctions()

    def GetDNAWorkflowCases(self, _indicationCategory1, _indicationDisease1, _indicationDisease2, _indicationDisease3, _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode, _reasonCode, _username, _surname):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetDNAWorkflowCases(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)}", (_indicationCategory1, _indicationDisease1, _indicationDisease2, _indicationDisease3, _dateFrom, _dateTo, _reportStatus, _priority, _diseaseIndicationCode, _reasonCode, _username, _surname))

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

    def GetSample(self, _LabNumber):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSample(%s)}", (_LabNumber,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    def GetReportStatus(self):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetReportStatus()}")

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results


    def GetDNAPriority(self):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetDNAPriority()}")

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results


    def UserHasPermission(self, _username, _permissionCode):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXUserHasPermission(%s, %s)}", (_username, _permissionCode))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            _retVal = False
            if _results.__len__() > 0:
                _retVal = True

            return _retVal

    def GetDNADiseaseIndication(self, _indicationCategory1, _indicationDisease1, _indicationDisease2, _indicationDisease3):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetDNADiseaseIndication(%s,%s,%s,%s)}", (_indicationCategory1, _indicationDisease1, _indicationDisease2, _indicationDisease3))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    def GetDNAReasonForDiseaseIndication(self, _diseaseCode):
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetDNAReasonForDiseaseIndication(%s)}", (_diseaseCode,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

