import uuid
from rest_framework import serializers
from app.config.core.models import Document
from django.utils import timezone


class DocumentSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(required=True)
    description = serializers.CharField(allow_blank=True, required=False)
    document_file = serializers.FileField(required=False)
    document_file_type = serializers.CharField(required=False)
    document_type = serializers.CharField(required=True)
    created_date = serializers.DateTimeField(
        default=timezone.now,
        read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    document_id = serializers.CharField(default=uuid.uuid4)

    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = [
            'created_date',
            'document_id',
            'updated_at',
            'created_by',
            'updated_by'
        ]
        extra_kwargs = {
            'created_by': {
                'default': serializers.CurrentUserDefault()
            },
            'updated_by': {
                'default': serializers.CurrentUserDefault()
            }
        }

    def create(self, validated_data):
        """
        Create and return a new `Document` instance,
        given the validated data.
        """
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Document` instance,
        given the validated data.
        """
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """
        Modify the way data is presented,
        including URLs for files and handling any custom representations.
        """
        representation = super().to_representation(instance)
        if instance.document_file:
            representation['document_file'] = instance.document_file.url
        return representation
