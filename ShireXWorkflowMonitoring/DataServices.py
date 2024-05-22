from ShireXWorkflowMonitoring.CommonFunctionality import UtilityFunctions
from ShireXWorkflowMonitoring.CommonFunctionality import enumDataType
from django.db import connection
from django.http import JsonResponse
import logging

class ShireData:

    utilities = UtilityFunctions()

    def GetDNAWorkflowCases(self, pIndicationCategory1, pIndicationCategory2, pWorkFlow, pDateFrom, pDateTo, pReportStatus, pPriority,
                            pDiseaseIndicationCode1, pDiseaseIndicationCode2, pDiseaseIndicationCode3, pReasonCode1,
                            pReasonCode2, pReasonCode3, pUsername, pSurname, pLabNumber, pRefKey, pNoResultStatus):
        logger = logging.getLogger(__name__)

        _indicationCategory1 = pIndicationCategory1
        _indicationCategory2 = pIndicationCategory2
        _workFlow = pWorkFlow
        _dateFrom = pDateFrom
        _dateTo = pDateTo
        _reportStatus = pReportStatus
        _priority = pPriority
        _diseaseIndicationCode1 = pDiseaseIndicationCode1
        _diseaseIndicationCode2 = pDiseaseIndicationCode2
        _diseaseIndicationCode3 = pDiseaseIndicationCode3
        _reasonCode1 = pReasonCode1
        _reasonCode2 = pReasonCode2
        _reasonCode3 = pReasonCode3
        _username = pUsername
        _surname = pSurname
        _labNumber = pLabNumber
        _refKey = pRefKey
        _noResultStatus = pNoResultStatus

        logger.info("Parameters for GetDNAWorkflowCases: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s",
                    _indicationCategory1, _indicationCategory2, _workFlow, _dateFrom, _dateTo, _reportStatus, _priority,
                    _diseaseIndicationCode1, _diseaseIndicationCode2, _diseaseIndicationCode3, _reasonCode1, _reasonCode2,
                    _reasonCode3, _username, _surname, _labNumber, _refKey, _noResultStatus)

        with connection.cursor() as _cursor:
            try:
                _cursor.execute("{CALL dbo.uspShireXGetDNAWorkflowCases(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
                                "%s, %s, %s, %s, %s)}", (_indicationCategory1, _indicationCategory2, _workFlow, _dateFrom, _dateTo, _reportStatus,
                                                         _priority, _diseaseIndicationCode1, _diseaseIndicationCode2,
                                                         _diseaseIndicationCode3, _reasonCode1, _reasonCode2, _reasonCode3,
                                                         _username, _surname, _labNumber, _refKey, _noResultStatus))

                _workflowCases = self.utilities.ConvertCursorListToDict(_cursor)
                return _workflowCases
            except Exception as e:
                logger.error("An error occurred in GetDNAWorkflowCases: %s", e)
                _workflowCases = []

                return _workflowCases


    def GetSampleIndicationReportBill(self, pLabNumber):
        _labNumber = pLabNumber

        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSampleIndicationReportBill(%s)}", (_labNumber,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    def GetSampleWorksheetResults(self, pLabNumber, pIndication):
        _labNumber = pLabNumber
        _indication = pIndication

        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSampleWorksheetResults(%s,%s)}", (_labNumber, _indication,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    def GetSampleExtracts(self, pLabNumber):
        _labNumber = pLabNumber
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSampleExtractsheetResults(%s)}", (_labNumber,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    def SetAllocatedToForDNA(self, pLabNumber, pStaffCode):
        _labNumber = pLabNumber
        _staffCode = pStaffCode

        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXSetAllocatedToForDNA(%s,%s)}", (_labNumber, _staffCode, ))

            return 1

    def GetSample(self, pLabNumber):
        _labNumber = pLabNumber

        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSample(%s)}", (_labNumber,))

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

    def UserHasPermission(self, pUsername, pPermissionCode):
        _username = pUsername
        _permissionCode = pPermissionCode

        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXUserHasPermission(%s, %s)}", (_username, _permissionCode))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            _retVal = False
            if _results.__len__() > 0:
                _retVal = True

            return _retVal

    def GetDNADiseaseIndication(self, pIndicationCategory1, pIndicationCategory2, pWorkFlow):
        _indicationCategory1 = pIndicationCategory1
        _indicationCategory2 = pIndicationCategory2
        _workFlow = pWorkFlow
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetDNADiseaseIndication(%s,%s,%s)}", (_indicationCategory1, _indicationCategory2, _workFlow))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    def GetDNAReasonForDiseaseIndication(self, pDiseaseCode1, pDiseaseCode2, pDiseaseCode3):
        _diseaseCode1 = pDiseaseCode1
        _diseaseCode2 = pDiseaseCode2
        _diseaseCode3 = pDiseaseCode3

        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetDNAReasonForDiseaseIndication(%s, %s, %s)}", (
                _diseaseCode1, _diseaseCode2, _diseaseCode3))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    def GetSampleTestsNotAllocatedToWorksheet(self, pLabNumber, pIndication):
        _labNumber = pLabNumber
        _indication = pIndication
        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSampleTestsNotAllocatedToWorksheet(%s,%s)}", (_labNumber, _indication,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    def GetSampleTests(self, pLabNumber):
        _labNumber = pLabNumber

        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetSampleTests(%s)}", (_labNumber,))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results

    def GetDNARefKey(self, pDiseaseCode1, pDiseaseCode2, pDiseaseCode3):
        _diseaseCode1 = pDiseaseCode1
        _diseaseCode2 = pDiseaseCode2
        _diseaseCode3 = pDiseaseCode3

        with connection.cursor() as _cursor:
            _cursor.execute("{CALL dbo.uspShireXGetDNARefKey(%s, %s, %s)}", (
                _diseaseCode1, _diseaseCode2, _diseaseCode3))

            _results = self.utilities.ConvertCursorListToDict(_cursor)

            return _results
