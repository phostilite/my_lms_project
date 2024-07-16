from rest_framework import serializers
from courses.models import CourseDelivery, ScormCloudCourse, ScormCloudRegistration

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScormCloudCourse
        fields = '__all__'  # Adjust the fields as necessary

class CourseDeliverySerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)  # Assuming CourseDelivery has a 'course' ForeignKey to Course

    class Meta:
        model = CourseDelivery
        fields = '__all__'  # Adjust the fields as necessary, ensure 'course' is included

class ScormCloudRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScormCloudRegistration
        fields = ['registration_id']