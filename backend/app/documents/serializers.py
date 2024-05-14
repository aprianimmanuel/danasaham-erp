from rest_framework import serializers
from core.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = [
            'created_date',
            'document_id',
            'created_by',
            'updated_by',
            'updated_at']


class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['document_id']
        extra_kwargs = {
            'document_file': {
                'required': False
            },
            'created_by': {
                'write_only': True,
                'default': serializers.CurrentUserDefault()
            },
            'updated_by': {
                'write_only': True,
                'default': serializers.CurrentUserDefault()
            }
        }

    def create(self, validated_data):
        """
        Create and return a new `Document` instance, given the validated data.
        """
        # Additional custom creation logic can be placed here.
        return Document.objects.create(**validated_data)

    def to_representation(self, instance):
        """
        Optionally, modify the way the data is presented.
        This can include presenting a full URL to the uploaded file or adding additional read-only fields.
        """
        representation = super().to_representation(instance)
        # Example of how to modify the file field representation:
        if instance.document_file:
            representation['document_file'] = instance.document_file.url
        return representation
