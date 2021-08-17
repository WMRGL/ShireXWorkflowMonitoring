#Add Haem Onc specific classes in this file
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.urls import reverse
from django.views.generic import TemplateView
from ShireXWorkflowMonitoring.apps import ShireXWorkflowMonitoringConfig

class BMTSearch(TemplateView):
    template_name = "BMTSearch.html"
    title = ShireXWorkflowMonitoringConfig.title

    def get(self, request):
        _context = {
            "Title": self.title,
        }
        return render(request, self.template_name, _context)
