from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView

from ShireXWorkflowMonitoring import CommonFunctionality
from ShireXWorkflowMonitoring import HaemOncologyFunctionality
from ShireXWorkflowMonitoring import SampleFunctionality

app_name = "ShireXWorkflowMonitoringApplication"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', CommonFunctionality.Login.as_view(), name="LoginPage"),
    path('', CommonFunctionality.Start.as_view(), name="StartPage"),
    path('logout/', CommonFunctionality.Authenticate.DoLogout, name="LogoutSystem"),
    path('HO/BMT/', HaemOncologyFunctionality.BMTSearch.as_view(), name="HaemOncBMTSearch"),
    path('HO/MPN/', HaemOncologyFunctionality.MPNSearch.as_view(), name="HaemOncMPNSearch"),
    path('HO/D-AML/', HaemOncologyFunctionality.DAMLSearch.as_view(), name="HaemOncDAMLSearch"),
    path('HO/R-AML/', HaemOncologyFunctionality.RAMLSearch.as_view(), name="HaemOncRAMLSearch"),
    path('HO/AMLOdds/', HaemOncologyFunctionality.AMLOddsSearch.as_view(), name="HaemOncAMLOddsSearch"),
    path('HO/BREAK/', HaemOncologyFunctionality.BreakSearch.as_view(), name="HaemOncBreakSearch"),
    path('HO/SNPArrayAnalysis/', HaemOncologyFunctionality.SNPSearch.as_view(), name="HaemOncSNPSearch"),
    path('HO/WGS/', HaemOncologyFunctionality.WGSSearch.as_view(), name="HaemOncWGSSearch"),
    path('HO/MDS/', HaemOncologyFunctionality.MDSSearch.as_view(), name="HaemOncMDSSearch"),
    path('HO/ALL/', HaemOncologyFunctionality.ALLSearch.as_view(), name="HaemOncALLSearch"),
    path('HO/CLL/', HaemOncologyFunctionality.CLLSearch.as_view(), name="HaemOncCLLSearch"),
    path('HO/D-HCL/', HaemOncologyFunctionality.DHCLSearch.as_view(), name="HaemOncDHCLSearch"),
    path('HO/D-ONC/', HaemOncologyFunctionality.DONCSearch.as_view(), name="HaemOncDONCSearch"),
    path('HO/D-CS/', HaemOncologyFunctionality.DCSSearch.as_view(), name="HaemOncDCSSearch"),
    path('HO/R-BCR/', HaemOncologyFunctionality.RBCRSearch.as_view(), name="HaemOncRBCRSearch"),
    path('HO/FAL/', HaemOncologyFunctionality.FALSearch.as_view(), name="HaemOncFALSearch"),
    path('HO/Everything/', HaemOncologyFunctionality.EverythingSearch.as_view(), name="HaemOncEverythingSearch"),
    path('HO/Allocate/<str:_labNumber>/<str:_workflowName>/', HaemOncologyFunctionality.SetAllocatedToForDNA.as_view(), name="HaemOncSetAllocatedTo"),
    path('Sample/<str:_labNumber>/<str:_workflowName>/', SampleFunctionality.SampleForm.as_view(), name="SampleForm"),
    path('HO/Allocate/<str:_labNumber>/<str:_workflowName>/AllocateComplete/', TemplateView.as_view(template_name='AllocateComplete.html'), name="AllocateComplete"),
]