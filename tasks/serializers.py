from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Task

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration - equivalent to UserCreate schema
    """
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        # Django automatically hashes passwords with create_user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for user responses - equivalent to UserResponse schema
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class TaskSerializer(serializers.ModelSerializer):
    """
    Full Task serializer - equivalent to TaskResponse schema
    """
    owner = UserResponseSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'due_date', 
            'completed', 'created_at', 'updated_at', 'owner'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner']


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating tasks - equivalent to TaskCreate schema
    """
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date']


class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating tasks - equivalent to TaskUpdate schema
    All fields optional for partial updates
    """
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'completed']
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'due_date': {'required': False},
            'completed': {'required': False},
        }