import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from tasks.models import Task
from datetime import datetime, timedelta, timezone

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture for API client"""
    return APIClient()


@pytest.fixture
def create_user():
    """Fixture to create a user"""
    def make_user(**kwargs):
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return make_user


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Fixture for authenticated API client"""
    user = create_user()
    # Get JWT token
    response = api_client.post('/api/token/', {
        'username': 'testuser',
        'password': 'testpass123'
    })
    token = response.data['access_token']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    api_client.user = user
    return api_client


@pytest.mark.django_db
class TestAuthenticationEndpoints:
    """Tests for authentication endpoints"""
    
    def test_register_user(self, api_client):
        """Test user registration"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123'
        }
        
        response = api_client.post('/api/register/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == 'newuser'
        assert response.data['email'] == 'new@example.com'
        assert 'password' not in response.data
        assert User.objects.filter(username='newuser').exists()
    
    def test_register_duplicate_username(self, api_client, create_user):
        """Test registering with duplicate username fails"""
        create_user(username='existing')
        
        data = {
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'newpass123'
        }
        
        response = api_client.post('/api/register/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_success(self, api_client, create_user):
        """Test successful login"""
        create_user()
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/token/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data
        assert response.data['token_type'] == 'bearer'
    
    def test_login_wrong_password(self, api_client, create_user):
        """Test login with wrong password fails"""
        create_user()
        
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = api_client.post('/api/token/', data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, api_client):
        """Test login with nonexistent user fails"""
        data = {
            'username': 'nonexistent',
            'password': 'testpass123'
        }
        
        response = api_client.post('/api/token/', data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTaskEndpoints:
    """Tests for task CRUD endpoints"""
    
    def test_create_task(self, authenticated_client):
        """Test creating a task"""
        data = {
            'title': 'New Task',
            'description': 'Task description'
        }
        
        response = authenticated_client.post('/api/tasks/create/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Task'
        assert response.data['description'] == 'Task description'
        assert response.data['owner']['username'] == 'testuser'
        assert not response.data['completed']
    
    def test_create_task_with_due_date(self, authenticated_client):
        """Test creating a task with due date"""
        due_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        
        data = {
            'title': 'Task with deadline',
            'due_date': due_date
        }
        
        response = authenticated_client.post('/api/tasks/create/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['due_date'] is not None
    
    def test_create_task_requires_auth(self, api_client):
        """Test creating task without auth fails"""
        data = {'title': 'New Task'}
        
        response = api_client.post('/api/tasks/create/', data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_user_tasks(self, authenticated_client):
        """Test getting user's tasks"""
        # Create some tasks
        Task.objects.create(
            title='Task 1',
            owner=authenticated_client.user
        )
        Task.objects.create(
            title='Task 2',
            owner=authenticated_client.user
        )
        
        response = authenticated_client.get('/api/tasks/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_get_tasks_only_own(self, authenticated_client, create_user):
        """Test users only see their own tasks"""
        # Create task for authenticated user
        Task.objects.create(
            title='My Task',
            owner=authenticated_client.user
        )
        
        # Create task for different user
        other_user = create_user(username='other', email='other@example.com')
        Task.objects.create(
            title='Other Task',
            owner=other_user
        )
        
        response = authenticated_client.get('/api/tasks/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == 'My Task'
    
    def test_get_single_task(self, authenticated_client):
        """Test getting a single task"""
        task = Task.objects.create(
            title='Test Task',
            owner=authenticated_client.user
        )
        
        response = authenticated_client.get(f'/api/tasks/{task.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Task'
    
    def test_get_other_users_task_fails(self, authenticated_client, create_user):
        """Test getting another user's task fails"""
        other_user = create_user(username='other', email='other@example.com')
        task = Task.objects.create(
            title='Other Task',
            owner=other_user
        )
        
        response = authenticated_client.get(f'/api/tasks/{task.id}/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_task(self, authenticated_client):
        """Test updating a task"""
        task = Task.objects.create(
            title='Old Title',
            owner=authenticated_client.user
        )
        
        data = {
            'title': 'New Title',
            'completed': True
        }
        
        response = authenticated_client.put(
            f'/api/tasks/{task.id}/update/',
            data
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'New Title'
        assert response.data['completed'] is True
    
    def test_partial_update_task(self, authenticated_client):
        """Test partial update (PATCH)"""
        task = Task.objects.create(
            title='Task',
            description='Description',
            owner=authenticated_client.user
        )
        
        data = {'completed': True}
        
        response = authenticated_client.patch(
            f'/api/tasks/{task.id}/update/',
            data
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['completed'] is True
        assert response.data['title'] == 'Task'  # Unchanged
    
    def test_delete_task(self, authenticated_client):
        """Test deleting a task"""
        task = Task.objects.create(
            title='Task to delete',
            owner=authenticated_client.user
        )
        
        response = authenticated_client.delete(
            f'/api/tasks/{task.id}/delete/'
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task.id).exists()
    
    def test_delete_other_users_task_fails(self, authenticated_client, create_user):
        """Test deleting another user's task fails"""
        other_user = create_user(username='other', email='other@example.com')
        task = Task.objects.create(
            title='Other Task',
            owner=other_user
        )
        
        response = authenticated_client.delete(
            f'/api/tasks/{task.id}/delete/'
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Task.objects.filter(id=task.id).exists()  # Still exists