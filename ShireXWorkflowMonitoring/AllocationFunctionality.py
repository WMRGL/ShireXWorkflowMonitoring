# Add Haem Onc specific classes in this file
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from ShireXWorkflowMonitoring.apps import ShireXWorkflowMonitoringConfig
from ShireXWorkflowMonitoring.CommonFunctionality import UtilityFunctions
from ShireXWorkflowMonitoring.CommonFunctionality import enumDataType
from ShireXWorkflowMonitoring.DataServices import ShireData
from ShireXWorkflowMonitoring.models import STAFF


class SetAllocatedToForDNA(TemplateView):
    template_name = "SetAllocatedToForDNA.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()

    def get(self, request, labNumber, workflowName):  # 🔥 Match `urls.py`
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('LoginPage'))

        try:
            staff = self._get_staff(request)
            isSupervisor, staffList = self._get_supervisor_info(request, workflowName)
            cancelURL = self._get_cancel_url(workflowName)

            context = self._build_context(labNumber, staffList, staff, isSupervisor, workflowName, cancelURL)
            return render(request, self.template_name, context)

        except Exception as ex:
            return self._handle_exception(labNumber, ex)

    def post(self, request, labNumber, workflowName):  # 🔥 Match `urls.py`
        try:
            staffCode = self.utilities.PostRequestKey(request, "ddlStaffCode", enumDataType.String)
            retVal = self.dataServices.SetAllocatedToForDNA(labNumber, staffCode)

            if retVal != 1:
                return self._handle_db_error(labNumber)  # Refactored method - MW

            urlName = reverse("AllocateComplete", kwargs={"labNumber": labNumber, "workflowName": workflowName})
            return HttpResponseRedirect(urlName)

        except Exception as ex:
            return self._handle_exception(labNumber, ex)  # Refactored method - MW

    # Private methods start here - MW

    def _get_staff(self, pRequest):
        _request = pRequest
        #Retrieve staff details from the database - MW
        _staffQuery = STAFF.objects.filter(LOGON_NAME = _request.user.username, EMPLOYMENT_END_DATE__isnull=True)
        if not _staffQuery.exists():
            raise ValueError("Staff code not found from the username")
        return _staffQuery.first()

    def _get_supervisor_info(self, pRequest, pWorkflowName):
        _request = pRequest
        _workflowName = pWorkflowName

        #Determine if user is a supervisor and get staff list if so - MW
        _permissionName = "Is" + _workflowName + "Supervisor"
        _hasPermission = self.dataServices.UserHasPermission(_request.user.username, _permissionName)
        return ("Y" if _hasPermission else "N", STAFF.objects.all() if _hasPermission else None)

    def _get_cancel_url(self, pWorkflowName):
        _workflowName = pWorkflowName

        #Determine the cancel URL based on the workflow name - MW
        return _workflowName + "Search" if _workflowName in ('WGS', 'SC') else "HaemOnc" + _workflowName + "Search"

    def _build_context(self, pLabNumber, pStaffList, pStaff, pIsSupervisor, pWorkflowName, pCancelURL):
        #Build context for rendering the template - MW#
        _labNumber = pLabNumber
        _staffList = pStaffList
        _staff = pStaff
        _isSupervisor = pIsSupervisor
        _workflowName = pWorkflowName
        _cancelURL = pCancelURL

        return {
            "labNumber": _labNumber,
            "staffList": _staffList,
            "staff": _staff,
            "isSupervisor": _isSupervisor,
            "workflowName": _workflowName,
            "cancelURL": _cancelURL,
        }

    def _handle_exception(self, pLabNumber, pEx):
        _labNumber = pLabNumber
        _ex = pEx
        #Handle exceptions and return appropriate context - MW
        return render(self.template_name, {"labNumber": _labNumber, "errorMessage": str(_ex)})

    def _handle_db_error(self, pLabNumber):
        _labNumber = pLabNumber

        #Handle database errors specifically - MW
        _context = {
            "labNumber": _labNumber,
            "errorMessage": "Failed to set the Allocated to column at the database server.",
        }
        return render(self.template_name, _context)


class AllocateCompleteView(TemplateView):
    template_name = 'AllocateComplete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['labNumber'] = self.kwargs.get('labNumber', None)
        context['workflowName'] = self.kwargs.get('workflowName', None)
        return context



class SetAllocatedToForCyto(TemplateView):
    template_name = "SetAllocatedToForCyto.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()

    def get(self, pRequest, pLabNumber, pWorkflowName):
        _request = pRequest
        _labNumber = pLabNumber
        _workflowName = pWorkflowName
        if not _request.user.is_authenticated:
            return HttpResponseRedirect(reverse('LoginPage'))

        try:
            _staff = self._get_staff(_request)
            _isSupervisor, _staffList = self._get_supervisor_info(_request, _workflowName)
            _cancelURL = self._get_cancel_url(_workflowName)  # Reuse of refactored method with different workflow - MW

            _context = self._build_context(_labNumber, _staffList, _staff, _isSupervisor, _workflowName, _cancelURL)
            return render(_request, self.template_name, _context)

        except Exception as ex:
            return self._handle_exception(_labNumber, ex)

    def post(self, pRequest, pLabNumber, pWorkflowName):
        _request = pRequest
        _labNumber = pLabNumber
        _workflowName = pWorkflowName

        try:
            _staffCode = self.utilities.PostRequestKey(_request, "ddlStaffCode", enumDataType.String)
            _retVal = self.dataServices.SetAllocatedToForCyto(_labNumber, _staffCode)  # Assuming similar method for Cyto - MW

            if _retVal != 1:
                return self._handle_db_error(_labNumber)  # Reuse of refactored method - MW

            _urlName = "AllocateComplete"
            return HttpResponseRedirect(_urlName)

        except Exception as ex:
            return self._handle_exception(_labNumber, ex)  # Reuse of refactored method - MW

    # Private methods (same as in SetAllocatedToForDNA, reused here) - MW

    def _get_staff(self, pRequest):
        _request = pRequest
        #Retrieve staff details from the database - MW
        _staffQuery = STAFF.objects.filter(LOGON_NAME = _request.user.username, EMPLOYMENT_END_DATE__isnull=True)
        if not _staffQuery.exists():
            raise ValueError("Staff code not found from the username")
        return _staffQuery.first()

    def _get_supervisor_info(self, pRequest, pWorkflowName):
        _request = pRequest
        _workflowName = pWorkflowName

        #Determine if user is a supervisor and get staff list if so - MW
        _permissionName = "Is" + _workflowName + "Supervisor"
        _hasPermission = self.dataServices.UserHasPermission(_request.user.username, _permissionName)
        return ("Y" if _hasPermission else "N", STAFF.objects.all() if _hasPermission else None)

    def _get_cancel_url(self, pWorkflowName):
        _workflowName = pWorkflowName
        #Determine the cancel URL based on the workflow name - MW
        return _workflowName + "Search" if _workflowName in ('WGS', 'SC') else "HaemOnc" + _workflowName + "Search"

    def _build_context(self, pLabNumber, pStaffList, pStaff, pIsSupervisor, pWorkflowName, pCancelURL):
        _labNumber = pLabNumber
        _staffList = pStaffList
        _staff = pStaff
        _isSupervisor = pIsSupervisor
        _workflowName = pWorkflowName
        _cancelURL = pCancelURL


        #Build context for rendering the template - MW#
        return {
            "labNumber": _labNumber,
            "staffList": _staffList,
            "staff": _staff,
            "isSupervisor": _isSupervisor,
            "workflowName": _workflowName,
            "cancelURL": _cancelURL,
        }

    def _handle_exception(self, pLabNumber,pEx):
        _labNumber = pLabNumber
        _ex = pEx
        #Handle exceptions and return appropriate context - MW
        return render(self.template_name, {"labNumber": _labNumber, "errorMessage": str(_ex)})

    def _handle_db_error(self, _labNumber):
        #Handle database errors specifically - MW
        _context = {
            "labNumber": _labNumber,
            "errorMessage": "Failed to set the Allocated to column at the database server.",
        }
        return render(self.template_name, _context)