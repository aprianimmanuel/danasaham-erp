from rest_framework import serializers
from core.models import dttotDoc
from django.contrib.auth import get_user_model
from core.models import dttotDoc, User
from documents.serializers import DocumentCreateSerializer, DocumentSerializer


class DttotDocSerializer(serializers.ModelSerializer):
    input_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        default=serializers.CurrentUserDefault()
    )
    document = DocumentCreateSerializer()

    class Meta:
        model = dttotDoc
        fields = '__all__'
        read_only_fields = ('dttot_id',)

    def create(self, validated_data):
        """
        Custom create method for creating a new dttotDoc instance from validated data.
        """
        document_data = validated_data.pop('document')
        document = DocumentCreateSerializer().create(DocumentCreateSerializer(), validated_data=document_data)
        dttot_doc = dttotDoc.objects.create(document=document, **validated_data)
        return dttot_doc

    def to_representation(self, instance):
        """
        Custom method to modify the output to display user email instead of user_id.
        """
        representation = super().to_representation(instance)
        representation['document'] = DocumentSerializer(instance.document).data
        return representation
