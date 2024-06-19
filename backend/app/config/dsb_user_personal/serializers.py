from rest_framework import serializers
from app.config.core.models import dsb_user_personal

class DsbUserPersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = dsb_user_personal
        fields = '__all__'
