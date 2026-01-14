import pytest
from django.contrib.auth import get_user_model
from tasks.models import Task
from datetime import datetime, timedelta, timezone

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model"""
    
    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        assert user.is_staff
        assert user.is_superuser
    
    def test_user_str(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        assert str(user) == 'testuser'


@pytest.mark.django_db
class TestTaskModel:
    """Tests for Task model"""
    
    def test_create_task(self):
        """Test creating a task"""
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
        
        assert task.title == 'Test Task'
        assert task.description == 'Test Description'
        assert task.owner == user
        assert not task.completed
        assert task.created_at is not None
        assert task.updated_at is not None
    
    def test_task_with_due_date(self):
        """Test creating a task with due date"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        due_date = datetime.now(timezone.utc) + timedelta(days=1)
        task = Task.objects.create(
            title='Test Task',
            due_date=due_date,
            owner=user
        )
        
        assert task.due_date == due_date
    
    def test_task_str(self):
        """Test task string representation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        task = Task.objects.create(
            title='My Task',
            owner=user
        )
        
        assert str(task) == 'My Task'
    
    def test_task_ordering(self):
        """Test tasks are ordered by created_at descending"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        task1 = Task.objects.create(title='Task 1', owner=user)
        task2 = Task.objects.create(title='Task 2', owner=user)
        
        tasks = Task.objects.all()
        
        assert tasks[0] == task2  # Most recent first
        assert tasks[1] == task1