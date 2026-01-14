import pytest
from django.contrib.auth import get_user_model
from tasks.models import Task
from tasks.serializers import (
    UserRegistrationSerializer,
    UserResponseSerializer,
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer
)
from datetime import datetime, timedelta, timezone

User = get_user_model()


@pytest.mark.django_db
class TestUserSerializers:
    """Tests for user serializers"""
    
    def test_user_registration_serializer(self):
        """Test user registration serializer"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'testpass123'
        }
        
        serializer = UserRegistrationSerializer(data=data)
        
        assert serializer.is_valid()
        user = serializer.save()
        
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.check_password('testpass123')
    
    def test_user_registration_password_too_short(self):
        """Test registration fails with short password"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'short'
        }
        
        serializer = UserRegistrationSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
    
    def test_user_response_serializer(self):
        """Test user response serializer"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        serializer = UserResponseSerializer(user)
        
        assert serializer.data['username'] == 'testuser'
        assert serializer.data['email'] == 'test@example.com'
        assert 'password' not in serializer.data
        assert 'id' in serializer.data


@pytest.mark.django_db
class TestTaskSerializers:
    """Tests for task serializers"""
    
    def test_task_serializer(self):
        """Test full task serializer"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            owner=user
        )
        
        serializer = TaskSerializer(task)
        
        assert serializer.data['title'] == 'Test Task'
        assert serializer.data['description'] == 'Test Description'
        assert serializer.data['owner']['username'] == 'testuser'
        assert 'id' in serializer.data
        assert 'created_at' in serializer.data
        assert 'updated_at' in serializer.data
    
    def test_task_create_serializer(self):
        """Test task creation serializer"""
        data = {
            'title': 'New Task',
            'description': 'Task description'
        }
        
        serializer = TaskCreateSerializer(data=data)
        
        assert serializer.is_valid()
        assert serializer.validated_data['title'] == 'New Task'
    
    def test_task_create_serializer_missing_title(self):
        """Test task creation fails without title"""
        data = {'description': 'Task description'}
        
        serializer = TaskCreateSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'title' in serializer.errors
    
    def test_task_update_serializer_partial(self):
        """Test partial task update"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        task = Task.objects.create(
            title='Old Title',
            description='Old Description',
            owner=user
        )
        
        # Only update completed field
        data = {'completed': True}
        serializer = TaskUpdateSerializer(task, data=data, partial=True)
        
        assert serializer.is_valid()
        updated_task = serializer.save()
        
        assert updated_task.completed is True
        assert updated_task.title == 'Old Title'  # Unchanged