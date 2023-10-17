from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView

from ShireXWorkflowMonitoring import CommonFunctionality
from ShireXWorkflowMonitoring import HaemOncologyFunctionality
from ShireXWorkflowMonitoring import CancerFunctionality
from ShireXWorkflowMonitoring import AllocationFunctionality
from ShireXWorkflowMonitoring import SampleFunctionality

app_name = "ShireXWorkflowMonitoringApplication"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', CommonFunctionality.Login.as_view(), name="LoginPage"),
    path('', CommonFunctionality.Start.as_view(), name="StartPage"),
    path('logout/', CommonFunctionality.Authenticate.DoLogout, name="LogoutSystem"),
    path('Molecular/BMT/', HaemOncologyFunctionality.BMTSearch.as_view(), name="HaemOncBMTSearch"),
    path('Molecular/MPN/', HaemOncologyFunctionality.MPNSearch.as_view(), name="HaemOncMPNSearch"),
    path('Molecular/D-AML/', HaemOncologyFunctionality.DAMLSearch.as_view(), name="HaemOncDAMLSearch"),
    path('Molecular/R-AML/', HaemOncologyFunctionality.RAMLSearch.as_view(), name="HaemOncRAMLSearch"),
    path('Molecular/RNA/', HaemOncologyFunctionality.RNASearch.as_view(), name="HaemOncRNASearch"),
    path('Molecular/BREAK/', HaemOncologyFunctionality.BreakSearch.as_view(), name="HaemOncBreakSearch"),
    path('Molecular/SNPArrayAnalysis/', HaemOncologyFunctionality.SNPSearch.as_view(), name="HaemOncSNPSearch"),
    path('Molecular/WGS/', CancerFunctionality.WGSSearch.as_view(), name="WGSSearch"),
    path('Molecular/PanHaem/', HaemOncologyFunctionality.GLHPanHaemSearch.as_view(), name="HaemOncPanHaemSearch"),
    path('Molecular/ALL/', HaemOncologyFunctionality.ALLSearch.as_view(), name="HaemOncALLSearch"),
    path('Molecular/CLL/', HaemOncologyFunctionality.CLLSearch.as_view(), name="HaemOncCLLSearch"),
    path('Molecular/R-BCR/', HaemOncologyFunctionality.RBCRSearch.as_view(), name="HaemOncRBCRSearch"),
    path('Molecular/FAL/', HaemOncologyFunctionality.FALSearch.as_view(), name="HaemOncFALSearch"),
    path('Molecular/HaemOncAll/', HaemOncologyFunctionality.HaemOncSearch.as_view(), name="HaemOncMolecularSearch"),
    path('Molecular/SolidCancer/', CancerFunctionality.SolidCancerSearch.as_view(), name="SCSearch"),
    path('Molecular/Allocate/<str:_labNumber>/<str:_workflowName>/',
         AllocationFunctionality.SetAllocatedToForDNA.as_view(), name="DNASetAllocatedTo"),
    path('Sample/<str:_labNumber>/<str:_workflowName>/<str:_indication>', SampleFunctionality.SampleForm.as_view(), name="SampleForm"),
    path('Molecular/Allocate/<str:_labNumber>/<str:_workflowName>/AllocateComplete/',
         TemplateView.as_view(template_name='AllocateComplete.html'), name="AllocateComplete"),
]
