from rest_framework import serializers
from core.models import dttotDoc


class DttotDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = dttotDoc
        fields = '__all__'
        read_only_fields = ('document_id',)
