from rest_framework import serializers
from core.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'document_name',
            'description',
            'document_file',
            'created_date',
            'document_id',
            'document_type',
            'created_by',
            'updated_by']
        read_only_fields = [
            'created_date',
            'document_id',
            'created_by',
            'updated_by']
