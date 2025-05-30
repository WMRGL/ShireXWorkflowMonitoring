import logging
from django.db import connection
from ShireXWorkflowMonitoring.CommonFunctionality import UtilityFunctions

class ShireData:
    utilities = UtilityFunctions()
    logger = logging.getLogger(__name__)

    def GetDNAWorkflowCases(self, pIndicationCategory1, pIndicationCategory2, pWorkFlow, pDateFrom, pDateTo, pReportStatus, pPriority,
                            pDiseaseIndicationCode1, pDiseaseIndicationCode2, pDiseaseIndicationCode3, pReasonCode1,
                            pReasonCode2, pReasonCode3, pUsername, pSurname, pLabNumber, pRefKey, pNoResultStatus):
        try:
            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXGetDNAWorkflowCases(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
                                "%s, %s, %s, %s, %s)}",
                                (pIndicationCategory1, pIndicationCategory2, pWorkFlow, pDateFrom, pDateTo, pReportStatus,
                                 pPriority, pDiseaseIndicationCode1, pDiseaseIndicationCode2, pDiseaseIndicationCode3,
                                 pReasonCode1, pReasonCode2, pReasonCode3, pUsername, pSurname, pLabNumber, pRefKey,
                                 pNoResultStatus))

                _workflowCases = self.utilities.ConvertCursorListToDict(_cursor)
                return _workflowCases
        except Exception as e:
            self.logger.error("An error occurred in GetDNAWorkflowCases: %s", e)
            return []

    def GetSampleIndicationReportBill(self, pLabNumber):
        try:
            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXGetSampleIndicationReportBill(%s)}", (pLabNumber,))
                _results = self.utilities.ConvertCursorListToDict(_cursor)
                return _results
        except Exception as e:
            self.logger.error("An error occurred in GetSampleIndicationReportBill: %s", e)
            return []

    def GetSampleWorksheetResults(self, pLabNumber, pIndication):
        try:
            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXGetSampleWorksheetResults(%s,%s)}", (pLabNumber, pIndication))
                _results = self.utilities.ConvertCursorListToDict(_cursor)
                return _results
        except Exception as e:
            self.logger.error("An error occurred in GetSampleWorksheetResults: %s", e)
            return []

    def GetSampleExtracts(self, pLabNumber):
        try:
            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXGetSampleExtractsheetResults(%s)}", (pLabNumber,))
                _results = self.utilities.ConvertCursorListToDict(_cursor)
                return _results
        except Exception as e:
            self.logger.error("An error occurred in GetSampleExtracts: %s", e)
            return []

    def SetAllocatedToForDNA(self, pLabNumber, pStaffCode):
        try:
            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXSetAllocatedToForDNA(%s,%s)}", (pLabNumber, pStaffCode))
                return 1
        except Exception as e:
            self.logger.error("An error occurred in SetAllocatedToForDNA: %s", e)
            return 0

    def GetSample(self, pLabNumber):
        try:
            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXGetSample(%s)}", (pLabNumber,))
                _results = self.utilities.ConvertCursorListToDict(_cursor)
                return _results
        except Exception as e:
            self.logger.error("An error occurred in GetSample: %s", e)
            return []

    def GetReportStatus(self):
        try:
            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXGetReportStatus()}")
                _results = self.utilities.ConvertCursorListToDict(_cursor)
                return _results
        except Exception as e:
            self.logger.error("An error occurred in GetReportStatus: %s", e)
            return []

    def GetDNAPriority(self):
        try:
            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXGetDNAPriority()}")
                _results = self.utilities.ConvertCursorListToDict(_cursor)
                return _results
        except Exception as e:
            self.logger.error("An error occurred in GetDNAPriority: %s", e)
            return []

    def UserHasPermission(self, pUsername, pPermissionCode):
        try:
            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXUserHasPermission(%s, %s)}", (pUsername, pPermissionCode))
                _results = self.utilities.ConvertCursorListToDict(_cursor)
                return len(_results) > 0
        except Exception as e:
            self.logger.error("An error occurred in UserHasPermission: %s", e)
            return False

    def GetDNADiseaseIndication(self, pIndicationCategory1, pIndicationCategory2, pWorkFlow):
        try:
            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXGetDNADiseaseIndication(%s,%s,%s)}",
                                (pIndicationCategory1, pIndicationCategory2, pWorkFlow))
                _results = self.utilities.ConvertCursorListToDict(_cursor)
                return _results
        except Exception as e:
            self.logger.error("An error occurred in GetDNADiseaseIndication: %s", e)
            return []

    def GetDNAReasonForDiseaseIndication(self, pDiseaseCode1, pDiseaseCode2, pDiseaseCode3):
        try:
            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXGetDNAReasonForDiseaseIndication(%s, %s, %s)}",
                                (pDiseaseCode1, pDiseaseCode2, pDiseaseCode3))
                _results = self.utilities.ConvertCursorListToDict(_cursor)
                return _results
        except Exception as e:
            self.logger.error("An error occurred in GetDNAReasonForDiseaseIndication: %s", e)
            return []

    def GetSampleTestsNotAllocatedToWorksheet(self, pLabNumber, pIndication):
        try:
            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXGetSampleTestsNotAllocatedToWorksheet(%s,%s)}", (pLabNumber, pIndication))
                _results = self.utilities.ConvertCursorListToDict(_cursor)
                return _results
        except Exception as e:
            self.logger.error("An error occurred in GetSampleTestsNotAllocatedToWorksheet: %s", e)
            return []

    def GetSampleTests(self, pLabNumber):
        try:
            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXGetSampleTests(%s)}", (pLabNumber,))
                _results = self.utilities.ConvertCursorListToDict(_cursor)
                return _results
        except Exception as e:
            self.logger.error("An error occurred in GetSampleTests: %s", e)
            return []

    def GetDNARefKey(self, pDiseaseCode1, pDiseaseCode2, pDiseaseCode3):
        try:
            with connection.cursor() as _cursor:
                _cursor.execute("{CALL dbo.uspShireXGetDNARefKey(%s, %s, %s)}",
                                (pDiseaseCode1, pDiseaseCode2, pDiseaseCode3))
                _results = self.utilities.ConvertCursorListToDict(_cursor)
                return _results
        except Exception as e:
            self.logger.error("An error occurred in GetDNARefKey: %s", e)
            return []