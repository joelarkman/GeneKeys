from rest_framework import serializers
from .models import GeneKey, PanelGene, Panel


class GeneKeySerializer(serializers.ModelSerializer):
    genes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    panel = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    added_by = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    added_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S')

    checked_by = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    checked_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S')

    class Meta:
        model = GeneKey
        fields = ['key', 'genes', 'panel', 'added_by',
                  'added_at', 'checked_by', 'checked_at']


class PanelGeneSerializer(serializers.ModelSerializer):
    gene = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    panel = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    preferred_transcript = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    added_by = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    added_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S')
    
    class Meta:
        model = PanelGene
        fields = ['gene', 'preferred_transcript', 'panel','added_by','added_at']


class PanelSerializer(serializers.ModelSerializer):
    added_by = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    added_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S')

    class Meta:
        model = Panel
        fields = ['id', 'name','added_by','added_at']
