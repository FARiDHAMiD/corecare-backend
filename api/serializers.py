from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.serializers import StringRelatedField, SlugRelatedField
from .models import *

class UserSerializer(serializers.ModelSerializer):
    profile_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'

    def get_profile_id(self, obj):
            if obj.role == User.Role.DOCTOR and hasattr(obj, 'doctor_profile'):
                return obj.doctor_profile.id
            elif obj.role == User.Role.PATIENT and hasattr(obj, 'patient_profile'):
                return obj.patient_profile.id
            return None

# Sign Up
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'role')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            # role=validated_data['role']
        )
        return user

# Login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid credentials")

        tokens = RefreshToken.for_user(user)
        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            },
            "tokens": {
                "refresh": str(tokens),
                "access": str(tokens.access_token),
            },
        }
    
# Tokens for blacklist
class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class DoctorProfileSerializer(serializers.ModelSerializer):

    # first_name = serializers.CharField(source='user.first_name', read_only=True)
    # last_name = serializers.CharField(source='user.last_name', read_only=True)
    department = serializers.CharField(source='department.name', read_only=True)
    dept = serializers.IntegerField(source='department.id', read_only=True)
    # phone = serializers.CharField(source='user.phone', read_only=True)
    # dob = serializers.DateField(source='user.dob', read_only=True)
    # email = serializers.EmailField(source='user.email', read_only=True)
    user = UserSerializer()

    class Meta:
        model = DoctorProfile
        fields = '__all__'
        
class LabReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabReport
        fields = '__all__'

class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    lab_reports = LabReportSerializer(many=True, read_only=True)  # Include lab reports

    class Meta:
        model = PatientProfile
        fields = '__all__'

class ReportTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportType
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField(read_only=True)
    doctor_name = serializers.SerializerMethodField(read_only=True)
    doctor_id = serializers.SerializerMethodField(read_only=True)
    department = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'doctor', 'time', 'description', 'status',
            'patient_name', 'doctor_name', 'doctor_id', 'department'
        ]

    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"

    def get_doctor_name(self, obj):
        return f"{obj.doctor.first_name} {obj.doctor.last_name}"

    def get_doctor_id(self, obj):
        return f"{obj.doctor.doctor_profile.id}"

    def get_department(self, obj):
        return f"{obj.doctor.doctor_profile.department.name}"
        
class PreVisitQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreVisitQuestion
        fields = '__all__'

class PreVisitReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreVisitReport
        fields = '__all__'