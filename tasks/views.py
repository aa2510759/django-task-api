from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from .models import Task
from .serializers import (
    UserRegistrationSerializer, 
    UserResponseSerializer,
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer
)

User = get_user_model()


# ============ Authentication Endpoints ============

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user - equivalent to /register endpoint
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        response_serializer = UserResponseSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login and get JWT tokens - equivalent to /token endpoint
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'detail': 'Username and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'detail': 'Incorrect username or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
        'token_type': 'bearer'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request, user_id):
    """
    Get user by ID - equivalent to /users/{user_id} endpoint
    """
    try:
        user = User.objects.get(id=user_id)
        serializer = UserResponseSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response(
            {'detail': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )


# ============ Task Endpoints ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    """
    Create a new task - equivalent to POST /tasks endpoint
    """
    serializer = TaskCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        # Automatically assign current user as owner
        task = serializer.save(owner=request.user)
        response_serializer = TaskSerializer(task)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tasks(request):
    """
    Get all tasks for current user - equivalent to GET /tasks endpoint
    """
    tasks = Task.objects.filter(owner=request.user)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_task(request, task_id):
    """
    Get a specific task - equivalent to GET /tasks/{task_id} endpoint
    """
    try:
        task = Task.objects.get(id=task_id, owner=request.user)
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    except Task.DoesNotExist:
        return Response(
            {'detail': 'Task not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_task(request, task_id):
    """
    Update a task - equivalent to PUT /tasks/{task_id} endpoint
    """
    try:
        task = Task.objects.get(id=task_id, owner=request.user)
    except Task.DoesNotExist:
        return Response(
            {'detail': 'Task not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # partial=True allows partial updates
    serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        response_serializer = TaskSerializer(task)
        return Response(response_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request, task_id):
    """
    Delete a task - equivalent to DELETE /tasks/{task_id} endpoint
    """
    try:
        task = Task.objects.get(id=task_id, owner=request.user)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Task.DoesNotExist:
        return Response(
            {'detail': 'Task not found'},
            status=status.HTTP_404_NOT_FOUND
        )