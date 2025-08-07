from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from .models import User, Project

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)
        return value

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'created_at', 'owner']
        
    def validate_title(self, value):
        """
        Vérifie que le titre comporte au moins 5 caractères.
        """
        if len(value) < 5:
            raise serializers.ValidationError("Le titre doit contenir au moins 5 caractères.")
        return value
    def validate_description(self, value):
        """
        Vérifie plusieurs règles pour le champ description :
        1. Ne doit pas contenir de mots interdits.
        """
        forbidden_words = ["spam", "fake"]
        for word in forbidden_words:
            if word in value.lower(): # .lower() pour une recherche insensible à la casse
                raise serializers.ValidationError(
                    f"Le mot '{word}' est interdit dans le contenu."
                )
        return value
