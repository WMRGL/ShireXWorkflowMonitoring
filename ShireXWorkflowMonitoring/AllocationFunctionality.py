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

    def get(self, request, _labNumber, _workflowName):

        try:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('LoginPage'))

            _staffList = None
            _staff = None
            _staffQuery = STAFF.objects.filter(LOGON_NAME=request.user.username, EMPLOYMENT_END_DATE__isnull=True)

            if _staffQuery is None or _staffQuery.__len__() == 0:
                _context = {
                    "labNumber": _labNumber,
                    "errorMessage": "The system cannot find the staff code from the username"
                }
                return render(request, self.template_name, _context)
            else:
                # Convert the queryset, which should only have one record
                # to a single instance of the Staff record
                for _item in _staffQuery:
                    _staff = _item

            _isSupervisor = "N"
            _permissionName = "Is" + _workflowName + "Supervisor"
            _hasPermission = self.dataServices.UserHasPermission(request.user.username, _permissionName)

            if _hasPermission:
                _isSupervisor = "Y"
                _staffList = STAFF.objects.all
            if _workflowName in ('WGS', 'SC'):
                _cancelURL = _workflowName + "Search"
            else:
                _cancelURL = "HaemOnc" + _workflowName + "Search"
            _context = {
                "labNumber": _labNumber,
                "staffList": _staffList,
                "staff": _staff,
                "isSupervisor": _isSupervisor,
                "workflowName": _workflowName,
                "cancelURL": _cancelURL,
            }
            return render(request, self.template_name, _context)

        except Exception as ex:
            _context = {
                "labNumber": _labNumber,
                "errorMessage": str(ex),
            }
            return render(request, self.template_name, _context)

    def post(self, request, _labNumber, _workflowName):

        try:
            _staffCode = self.utilities.PostRequestKey(request, "ddlStaffCode", enumDataType.String)
            _retVal = self.dataServices.SetAllocatedToForDNA(_labNumber, _staffCode)

            if _retVal != 1:
                _context = {
                    "labNumber": _labNumber,
                    "errorMessage": "The system attempted to set the Allocated to column for you, "
                                    "but failed at the database server.",
                }
                return render(request, self.template_name, _context)

            # _urlName = "HaemOnc" + _workflowName + "Search"
            _urlName = "AllocateComplete"

            return HttpResponseRedirect(_urlName)

        except Exception as ex:
            _context = {
                "labNumber": _labNumber,
                "errorMessage": str(ex),
            }
            return render(request, self.template_name, _context)

class SetAllocatedToForCyto(TemplateView):  # placeholder - not yet ready for use
    template_name = "SetAllocatedToForCyto.html"
    title = ShireXWorkflowMonitoringConfig.title
    utilities = UtilityFunctions()
    dataServices = ShireData()

    def get(self, request, _labNumber, _workflowName):

        try:
            _staffList = None
            _staff = None
            _staffQuery = STAFF.objects.filter(LOGON_NAME=request.user.username, EMPLOYMENT_END_DATE__isnull=True)

            if _staffQuery is None or _staffQuery.__len__() == 0:
                _context = {
                    "labNumber": _labNumber,
                    "errorMessage": "The system cannot find the staff code from the username"
                }
                return render(request, self.template_name, _context)
            else:
                # Convert the queryset, which should only have one record
                # to a single instance of the Staff record
                for _item in _staffQuery:
                    _staff = _item

            _isSupervisor = "N"
            _permissionName = "Is" + _workflowName + "Supervisor"
            _hasPermission = self.dataServices.UserHasPermission(request.user.username, _permissionName)

            if _hasPermission:
                _isSupervisor = "Y"
                _staffList = STAFF.objects.all

            _cancelURL = "Cyto" + _workflowName + "Search"

            _context = {
                "labNumber": _labNumber,
                "staffList": _staffList,
                "staff": _staff,
                "isSupervisor": _isSupervisor,
                "workflowName": _workflowName,
                "cancelURL": _cancelURL,
            }
            return render(request, self.template_name, _context)

        except Exception as ex:
            _context = {
                "labNumber": _labNumber,
                "errorMessage": str(ex),
            }
            return render(request, self.template_name, _context)

    def post(self, request, _labNumber, _workflowName):

        try:
            _staffCode = self.utilities.PostRequestKey(request, "ddlStaffCode", enumDataType.String)
            _retVal = self.dataServices.SetAllocatedToForDNA(_labNumber, _staffCode)

            if _retVal != 1:
                _context = {
                    "labNumber": _labNumber,
                    "errorMessage": "The system attempted to set the Allocated to column for you, "
                                    "but failed at the database server.",
                }
                return render(request, self.template_name, _context)

            # _urlName = "HaemOnc" + _workflowName + "Search"
            _urlName = "AllocateComplete"

            return HttpResponseRedirect(_urlName)

        except Exception as ex:
            _context = {
                "labNumber": _labNumber,
                "errorMessage": str(ex),
            }
            return render(request, self.template_name, _context)
