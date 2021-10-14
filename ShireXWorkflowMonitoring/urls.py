from django.contrib import admin
from django.urls import path

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
    path('HO/Allocate/<str:_labNumber>/<str:_workflowName>/', HaemOncologyFunctionality.SetAllocatedToForDNA.as_view(), name="HaemOncSetAllocatedTo"),
    path('Sample/<str:_labNumber>/<str:_workflowName>/', SampleFunctionality.SampleForm.as_view(), name="SampleForm"),
]
