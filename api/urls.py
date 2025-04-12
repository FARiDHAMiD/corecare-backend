from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'doctors', DoctorProfileViewSet)
router.register(r'patients', PatientProfileViewSet)
router.register(r'reporttypes', ReportTypeViewSet)
router.register(r'labreports', LabReportViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'previsitquestions', PreVisitQuestionViewSet)
router.register(r'previsitreports', PreVisitReportViewSet)



urlpatterns = [
    path('', include(router.urls)),

    # Authentication jwt
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("signup/", RegisterView.as_view(), name="register"),
    # path("patient/", PatientProfileViewSet.as_view(), name="patient-profile"),
    # path("doctor/", DoctorProfileViewSet.as_view(), name="doctor-profile"),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Doctors Custom Requests
    path('doctors/department/<int:department_id>/', DoctorProfileViewSet.doctors_by_department, name='doctors-by-department'),


    # LabReports Custom Requests
    path('lab-reports/type/<int:report_type_id>/', LabReportViewSet.lab_reports_by_type, name='lab-reports-by-type'),
    path('patients/<int:patient_id>/lab-reports/', LabReportViewSet.upload_lab_report, name='upload_lab_report'),
    path('labreports/patient/<int:patient_id>/', LabReportViewSet.get_patient_lab_reports, name='get_patient_lab_reports'),


    # Appointements Custom Requests
    # path('appointments/patient/', AppointmentViewSet.patient_appointments, name='patient-appointments'),
    path('appointments/patient/<int:patient_id>/', AppointmentViewSet.patient_appointments, name='patient-appointments-admin'),

]