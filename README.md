# Igolo Backend Standard coding practices and project structure.

## 1. Project Structure
Organize your project structure properly to ensure maintainability and scalability.

```
project_root/
│── manage.py
│── requirements.txt
│── .env
│── .gitignore
│── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   ├── signals.py
│   │   ├── admin.py
│   │   ├── tests.py
│── core/
│   ├── middleware.py
│   ├── utils.py
│── static/
│── media/
│── templates/
│── tests/
```

## 2. Python Coding Standards

### 2.1 General Coding Conventions
- Follow **PEP 8** coding style.
- Use **snake_case** for variables and function names.
- Use **CamelCase** for class names.
- Use **4 spaces** for indentation.
- Use **meaningful names** for variables and functions.
- Follow **PEP 257** for docstrings.

### 2.2 Type Hinting
```python
from typing import List, Dict

def get_users() -> List[Dict[str, str]]:
    return [{"name": "John", "email": "john@example.com"}]
```

### 2.3 Logging
Use logging instead of print statements:
```python
import logging

logger = logging.getLogger(__name__)

logger.info("User logged in successfully.")
```

### 2.4 Exception Handling
- Always use specific exceptions.
```python
try:
    user = User.objects.get(email="test@example.com")
except User.DoesNotExist:
    logger.error("User not found")
```

## 3. Django REST Framework Best Practices

### 3.1 Models
- Define **unique constraints** when necessary.
- Use **related_name** in ForeignKey fields.
```python
from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 3.2 Serializers
```python
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
```

### 3.3 Views
Use **class-based views** over function-based views for better organization.
```python
from rest_framework.generics import ListCreateAPIView
from .models import User
from .serializers import UserSerializer

class UserListView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

### 3.4 Permissions
```python
from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
```

### 3.5 URL Routing
```python
from django.urls import path
from .views import UserListView

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
]
```

## 4. Security Best Practices
- Store **sensitive credentials** in `.env`.
- Use **django.middleware.security.SecurityMiddleware**.
- Enable **HTTPS** in production.
- Set `SECURE_HSTS_SECONDS` to enforce HSTS.
- Implement **CSRF Protection**.
- Restrict **CORS policies** with `django-cors-headers`.
- Use Django's built-in **User Model** instead of custom authentication systems.

## 5. Testing Guidelines
- Use **pytest** or Django’s `unittest`.
- Write unit tests for **models, views, and serializers**.
```python
from django.test import TestCase
from .models import User

class UserTestCase(TestCase):
    def test_user_creation(self):
        user = User.objects.create(email="test@example.com", name="Test User")
        self.assertEqual(user.email, "test@example.com")
```

## 6. Deployment Best Practices
- Use **Gunicorn** for production.
- Use **Docker** for containerization.
- Automate deployments with **CI/CD (GitHub Actions, GitLab CI)**.
- Set up **automated database migrations**.
- Monitor **performance metrics** using tools like Prometheus and Grafana.
- Enable **logging and monitoring** using tools like Sentry.

## 7. API Documentation
Use **drf-yasg** for API documentation:
```bash
pip install drf-yasg
```
```python
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
    ),
    public=True,
)
```

## 8. Performance Optimization
- Enable **query caching**.
- Optimize **database queries** using `select_related` and `prefetch_related`.
- Use **Redis** for caching.
- Implement **pagination** in API responses.
- Use **asynchronous tasks** with Celery for background processing.

