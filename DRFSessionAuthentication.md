# Django REST Framework SessionAuthentication — Complete Step-by-Step Guide

## Table of Contents

1. [What We Are Building](#1-what-we-are-building)
2. [Prerequisites](#2-prerequisites)
3. [What Is SessionAuthentication?](#3-what-is-sessionauthentication)
4. [How Sessions Work](#4-how-sessions-work)
5. [Session vs Cookie](#5-session-vs-cookie)
6. [Create the Django Project](#6-create-the-django-project)
7. [Install Dependencies](#7-install-dependencies)
8. [Create the Django App](#8-create-the-django-app)
9. [Configure `settings.py`](#9-configure-settingspy)
10. [Configure Middleware](#10-configure-middleware)
11. [Configure DRF](#11-configure-drf)
12. [Run Migrations](#12-run-migrations)
13. [Create a User](#13-create-a-user)
14. [Create the Login API](#14-create-the-login-api)
15. [Understand `authenticate()`](#15-understand-authenticate)
16. [Understand `login()`](#16-understand-login)
17. [Create the Profile API](#17-create-the-profile-api)
18. [Create the Protected API](#18-create-the-protected-api)
19. [Create the Logout API](#19-create-the-logout-api)
20. [Create URLs](#20-create-urls)
21. [Complete `views.py`](#21-complete-viewspy)
22. [Start the Server](#22-start-the-server)
23. [Test Login](#23-test-login)
24. [What Happens During Login](#24-what-happens-during-login)
25. [Test the Protected Profile API](#25-test-the-protected-profile-api)
26. [What Happens Without Authentication](#26-what-happens-without-authentication)
27. [What Is CSRF?](#27-what-is-csrf)
28. [Why SessionAuthentication Needs CSRF Protection](#28-why-sessionauthentication-needs-csrf-protection)
29. [CSRF Token Endpoint](#29-csrf-token-endpoint)
30. [Session Cookie vs CSRF Cookie](#30-session-cookie-vs-csrf-cookie)
31. [React + Django Setup](#31-react--django-setup)
32. [React Login](#32-react-login)
33. [React Protected GET Request](#33-react-protected-get-request)
34. [React Protected POST Request](#34-react-protected-post-request)
35. [React Logout](#35-react-logout)
36. [SessionAuthentication with `APIView`](#36-sessionauthentication-with-apiview)
37. [Global DRF Configuration](#37-global-drf-configuration)
38. [Authentication vs Permission](#38-authentication-vs-permission)
39. [Session Backend Configuration](#39-session-backend-configuration)
40. [Session Security Settings](#40-session-security-settings)
41. [Common Mistakes](#41-common-mistakes)
42. [Complete Request Lifecycle](#42-complete-request-lifecycle)
43. [Final Project Structure](#43-final-project-structure)
44. [Practice Exercise](#44-practice-exercise)
45. [Key Concepts to Memorize](#45-key-concepts-to-memorize)

---

# 1. What We Are Building

We will build a Django REST Framework API using **Django SessionAuthentication**.

The API will contain:

| Endpoint | Method | Purpose | Authentication |
|---|---|---|---|
| `/api/csrf/` | GET | Get/initialize CSRF token | No |
| `/api/login/` | POST | Log the user in | No |
| `/api/profile/` | GET | Return logged-in user | Yes |
| `/api/protected/` | POST | Test protected API | Yes + CSRF |
| `/api/logout/` | POST | Log the user out | Yes + CSRF |

The overall architecture is:

```text
Browser / React
       |
       | username + password
       v
POST /api/login/
       |
       v
Django authenticate()
       |
       v
Django login()
       |
       v
Django Session
       |
       v
sessionid Cookie
       |
       v
Browser stores cookie
       |
       +----------------------+
       |                      |
       v                      v
GET /profile/          POST /protected/
       |                      |
       v                      v
SessionAuthentication  SessionAuthentication
       |                      |
       v                      v
request.user           CSRF validation
       |                      |
       v                      v
IsAuthenticated        IsAuthenticated
       |                      |
       v                      v
     ALLOW                  ALLOW
```

---

# 2. Prerequisites

You should have a basic understanding of:

- Python
- Django
- Django URLs
- Django views
- Django models
- Django REST Framework
- HTTP methods
- JSON
- Basic authentication concepts

Recommended Python environment:

```bash
python --version
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it.

### macOS/Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

# 3. What Is SessionAuthentication?

`SessionAuthentication` is a Django REST Framework authentication class that uses Django's existing session framework.

It is commonly used when a browser has logged into a Django application and the browser has a Django session cookie.

The basic flow is:

```text
User logs in
    |
    v
Django creates an authenticated session
    |
    v
Browser receives sessionid cookie
    |
    v
Browser sends cookie on subsequent requests
    |
    v
DRF SessionAuthentication identifies the user
    |
    v
request.user
```

In DRF:

```python
from rest_framework.authentication import SessionAuthentication
```

Then:

```python
authentication_classes = [
    SessionAuthentication
]
```

---

# 4. How Sessions Work

HTTP is stateless.

For example:

```text
Request 1:
GET /products/

Request 2:
GET /orders/

Request 3:
GET /profile/
```

By default, each request is independent.

Django sessions allow the server to remember information about a user across requests.

When a user logs in:

```text
username = bijay
password = ********
```

Django authenticates the user and establishes a session.

Conceptually:

```text
User ID = 7

Session:
    user_id = 7
```

The browser receives a session cookie:

```text
sessionid=abc123xyz
```

On a later request:

```http
GET /api/profile/
Cookie: sessionid=abc123xyz
```

Django uses the session to identify the user.

Then:

```python
request.user
```

represents that authenticated user.

---

# 5. Session vs Cookie

A session and a cookie are related but are not the same thing.

## Cookie

A cookie is stored by the browser.

Example:

```text
sessionid=abc123xyz
```

## Session

A Django session represents server-side user state when using the database, cache, or cached database session backend.

For the default database backend, the architecture is:

```text
Browser
   |
   | sessionid=abc123
   v
Django
   |
   | look up session
   v
django_session
   |
   v
Authenticated user
```

The browser normally stores the session identifier, not the complete server-side session record.

---

# 6. Create the Django Project

Create a project:

```bash
django-admin startproject session_api
```

Enter the project:

```bash
cd session_api
```

Create an application:

```bash
python manage.py startapp accounts
```

The project will eventually look like:

```text
session_api/
│
├── manage.py
│
├── session_api/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── accounts/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── urls.py
    ├── views.py
    └── migrations/
```

---

# 7. Install Dependencies

Install Django REST Framework:

```bash
pip install djangorestframework
```

For a React frontend on a different origin, you may also need:

```bash
pip install django-cors-headers
```

Check installed packages:

```bash
pip freeze
```

---

# 8. Create the Django App

The app is already created with:

```bash
python manage.py startapp accounts
```

We will put our authentication views inside:

```text
accounts/views.py
```

and our API routes inside:

```text
accounts/urls.py
```

---

# 9. Configure `settings.py`

Open:

```text
session_api/settings.py
```

Add the application:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'accounts',
]
```

The important applications for this lesson are:

```python
'django.contrib.sessions',
'django.contrib.auth',
'rest_framework',
'accounts',
```

---

# 10. Configure Middleware

Make sure the following middleware exists:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

Three middleware components are particularly important.

## SessionMiddleware

```python
'django.contrib.sessions.middleware.SessionMiddleware',
```

Makes:

```python
request.session
```

available.

## CsrfViewMiddleware

```python
'django.middleware.csrf.CsrfViewMiddleware',
```

Provides Django's CSRF protection.

## AuthenticationMiddleware

```python
'django.contrib.auth.middleware.AuthenticationMiddleware',
```

Connects the authenticated Django session to:

```python
request.user
```

Conceptually:

```text
SessionMiddleware
        |
        v
request.session

AuthenticationMiddleware
        |
        v
request.user

CsrfViewMiddleware
        |
        v
CSRF protection
```

---

# 11. Configure DRF

At the bottom of `settings.py`, add:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

This means DRF will use:

```text
SessionAuthentication
```

for authentication and:

```text
IsAuthenticated
```

for the default permission.

Therefore, most API endpoints will require an authenticated session unless they explicitly override the permission.

---

# 12. Run Migrations

Run:

```bash
python manage.py migrate
```

Django creates its built-in tables.

Among them:

```text
auth_user
django_session
```

The `django_session` table is important for the default database session backend.

Conceptually:

```text
django_session
----------------------------------
session_key
session_data
expire_date
```

---

# 13. Create a User

Create a superuser:

```bash
python manage.py createsuperuser
```

Example:

```text
Username: bijay
Email: bijay@example.com
Password: ********
```

You now have a Django user that can be used for testing.

---

# 14. Create the Login API

Open:

```text
accounts/views.py
```

Add:

```python
from django.contrib.auth import authenticate, login, logout

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):

    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {
                'error': 'Username and password are required'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {
                'error': 'Invalid username or password'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    login(request, user)

    return Response(
        {
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username
            }
        },
        status=status.HTTP_200_OK
    )
```

---

# 15. Understand `authenticate()`

This code:

```python
user = authenticate(
    request,
    username=username,
    password=password
)
```

asks Django's authentication system to verify the credentials.

If the credentials are correct:

```python
user
```

contains a Django `User`.

For example:

```python
user.id
```

might be:

```text
7
```

and:

```python
user.username
```

might be:

```text
bijay
```

If authentication fails:

```python
user is None
```

Therefore:

```python
if user is None:
```

handles invalid credentials.

---

# 16. Understand `login()`

This line is the most important line in the login process:

```python
login(request, user)
```

It establishes the authenticated Django session.

Conceptually:

```text
username + password
        |
        v
authenticate()
        |
        v
User
        |
        v
login(request, user)
        |
        v
Authenticated session
        |
        v
sessionid cookie
```

The browser then receives a session cookie.

The password is not stored in the session cookie.

---

# 17. Create the Profile API

Add:

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):

    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'is_authenticated': request.user.is_authenticated
    })
```

The important object is:

```python
request.user
```

The flow is:

```text
sessionid cookie
       |
       v
SessionMiddleware
       |
       v
Django session
       |
       v
AuthenticationMiddleware
       |
       v
request.user
```

Then DRF's:

```python
IsAuthenticated
```

checks whether the request has an authenticated user.

---

# 18. Create the Protected API

Add:

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def protected_view(request):

    return Response({
        'message': 'You can access this protected API.',
        'user': request.user.username
    })
```

This endpoint requires:

1. An authenticated session
2. A valid CSRF token for the unsafe POST request

The flow is:

```text
POST /api/protected/
        |
        v
SessionAuthentication
        |
        v
request.user
        |
        v
CSRF validation
        |
        v
IsAuthenticated
        |
        v
View
```

---

# 19. Create the Logout API

Add:

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):

    logout(request)

    return Response({
        'message': 'Logout successful'
    })
```

Django's:

```python
logout(request)
```

ends the authenticated session.

After logout, a protected endpoint will no longer recognize the user as authenticated.

---

# 20. Create URLs

Create:

```text
accounts/urls.py
```

Add:

```python
from django.urls import path

from .views import (
    login_view,
    profile_view,
    protected_view,
    logout_view
)


urlpatterns = [
    path('login/', login_view),
    path('profile/', profile_view),
    path('protected/', protected_view),
    path('logout/', logout_view),
]
```

---

# 21. Complete `views.py`

At this stage, your `accounts/views.py` should look like:

```python
from django.contrib.auth import authenticate, login, logout

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):

    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {
                'error': 'Username and password are required'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {
                'error': 'Invalid username or password'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    login(request, user)

    return Response(
        {
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):

    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'is_authenticated': request.user.is_authenticated
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def protected_view(request):

    return Response({
        'message': 'You can access this protected API.',
        'user': request.user.username
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):

    logout(request)

    return Response({
        'message': 'Logout successful'
    })
```

---

# 22. Start the Server

Run:

```bash
python manage.py runserver
```

You should see something similar to:

```text
Starting development server at http://127.0.0.1:8000/
```

---

# 23. Test Login

Use Postman, Insomnia, curl, or your frontend.

Request:

```http
POST http://127.0.0.1:8000/api/login/
Content-Type: application/json
```

Body:

```json
{
    "username": "bijay",
    "password": "yourpassword"
}
```

If successful:

```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "bijay"
    }
}
```

More importantly, Django establishes a session and the client should retain the session cookie.

Conceptually:

```text
sessionid=abc123...
```

---

# 24. What Happens During Login

The complete login process is:

```text
POST /api/login/
        |
        v
username/password
        |
        v
authenticate()
        |
        v
User verified
        |
        v
login(request, user)
        |
        v
Django session established
        |
        v
sessionid cookie
        |
        v
Browser/client stores cookie
```

The browser can then send the cookie with later requests.

---

# 25. Test the Protected Profile API

Send:

```http
GET http://127.0.0.1:8000/api/profile/
```

The client must send the authenticated session cookie:

```http
Cookie: sessionid=abc123...
```

Django then performs approximately:

```text
sessionid
   |
   v
Django session
   |
   v
authenticated user
   |
   v
request.user
   |
   v
IsAuthenticated
   |
   v
Profile API
```

Example response:

```json
{
    "id": 1,
    "username": "bijay",
    "email": "bijay@example.com",
    "is_authenticated": true
}
```

---

# 26. What Happens Without Authentication

If you request:

```http
GET /api/profile/
```

without a valid authenticated session:

```text
No authenticated session
        |
        v
AnonymousUser
        |
        v
IsAuthenticated
        |
        v
Request denied
```

The endpoint is protected because it has:

```python
@permission_classes([IsAuthenticated])
```

---

# 27. What Is CSRF?

CSRF means **Cross-Site Request Forgery**.

It is an attack in which an attacker attempts to cause a user's browser to send an unwanted state-changing request to a site where the user is authenticated.

Cookie-based authentication is particularly relevant because browsers can automatically attach cookies to applicable requests.

For example, imagine:

```text
User is logged into:
myshop.com

Browser contains:
sessionid=abc123
```

The user visits an untrusted site.

That site attempts to cause:

```http
POST https://myshop.com/api/orders/
```

If the authenticated cookie is accepted with the request, the server needs a way to distinguish a legitimate application request from a forged one.

CSRF protection provides that additional protection.

---

# 28. Why SessionAuthentication Needs CSRF Protection

DRF's `SessionAuthentication` uses Django's session authentication.

For unsafe methods such as:

```text
POST
PUT
PATCH
DELETE
```

DRF performs CSRF validation when the request is authenticated through the session.

A useful mental model is:

```text
GET request
    |
    v
SessionAuthentication
    |
    v
request.user
```

For an unsafe request:

```text
POST/PUT/PATCH/DELETE
    |
    v
SessionAuthentication
    |
    v
CSRF validation
    |
    v
request.user
```

Therefore, a session-authenticated React application needs to handle both:

```text
session cookie
```

and:

```text
CSRF token
```

---

# 29. CSRF Token Endpoint

A convenient API endpoint for a frontend is:

```python
from django.middleware.csrf import get_token

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_view(request):

    token = get_token(request)

    return Response({
        'csrfToken': token
    })
```

Add it to `accounts/urls.py`:

```python
path('csrf/', csrf_view),
```

Now the frontend can request:

```http
GET /api/csrf/
```

and receive:

```json
{
    "csrfToken": "abcxyz..."
}
```

Calling `get_token(request)` also causes Django to ensure the CSRF cookie is available.

---

# 30. Session Cookie vs CSRF Cookie

These two cookies/tokens have different purposes.

## Session Cookie

Usually:

```text
sessionid
```

Purpose:

```text
Identify the authenticated session.
```

Conceptually:

```text
sessionid
    |
    v
Django session
    |
    v
User
```

## CSRF Cookie/Token

Usually:

```text
csrftoken
```

Purpose:

```text
Protect state-changing cookie-authenticated requests against CSRF.
```

For a protected POST, you commonly send:

```http
Cookie: sessionid=...
X-CSRFToken: ...
```

They solve different problems.

---

# 31. React + Django Setup

Suppose:

```text
React:
http://localhost:3000

Django:
http://localhost:8000
```

These are different origins.

For a typical development setup, install:

```bash
pip install django-cors-headers
```

Add:

```python
INSTALLED_APPS = [
    ...
    'corsheaders',
]
```

Add middleware near the beginning:

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    ...
]
```

Configure:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]

CORS_ALLOW_CREDENTIALS = True
```

Configure CSRF trusted origins:

```python
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
]
```

Use the exact origin of your actual frontend.

For production, use HTTPS and production domains.

---

# 32. React Login

First request the CSRF endpoint:

```javascript
await fetch("http://localhost:8000/api/csrf/", {
    credentials: "include"
});
```

You then need the CSRF token to send with the login request.

A login request can look like:

```javascript
const response = await fetch(
    "http://localhost:8000/api/login/",
    {
        method: "POST",

        credentials: "include",

        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },

        body: JSON.stringify({
            username: "bijay",
            password: "yourpassword"
        })
    }
);
```

Important:

```javascript
credentials: "include"
```

allows credentials such as cookies to be included in a cross-origin request when permitted by the browser and server configuration.

---

# 33. React Protected GET Request

After successful login:

```javascript
const response = await fetch(
    "http://localhost:8000/api/profile/",
    {
        credentials: "include"
    }
);
```

The browser sends the session cookie.

The request flow is:

```text
React
  |
  | sessionid cookie
  v
Django
  |
  v
SessionAuthentication
  |
  v
request.user
  |
  v
IsAuthenticated
  |
  v
Profile API
```

A GET request is normally considered a safe HTTP method, so CSRF token handling is not required in the same way as for an unsafe request.

---

# 34. React Protected POST Request

For a POST:

```javascript
const response = await fetch(
    "http://localhost:8000/api/protected/",
    {
        method: "POST",

        credentials: "include",

        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },

        body: JSON.stringify({})
    }
);
```

The request contains:

```text
sessionid
+
X-CSRFToken
```

The server then validates:

```text
SessionAuthentication
        |
        v
Authenticated user?
        |
        v
CSRF valid?
        |
        v
Permission valid?
        |
        v
Execute API
```

---

# 35. React Logout

Logout is an unsafe POST request, so it also needs the appropriate CSRF token when using session authentication.

```javascript
const response = await fetch(
    "http://localhost:8000/api/logout/",
    {
        method: "POST",

        credentials: "include",

        headers: {
            "X-CSRFToken": csrfToken
        }
    }
);
```

Django executes:

```python
logout(request)
```

The authenticated session is ended.

---

# 36. SessionAuthentication with `APIView`

Since DRF commonly uses class-based views, the same protected endpoint can be written using `APIView`.

```python
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class ProfileAPIView(APIView):

    authentication_classes = [
        SessionAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email
        })
```

The important configuration is:

```python
authentication_classes = [
    SessionAuthentication
]
```

and:

```python
permission_classes = [
    IsAuthenticated
]
```

---

# 37. Global DRF Configuration

Instead of repeating:

```python
authentication_classes = [
    SessionAuthentication
]

permission_classes = [
    IsAuthenticated
]
```

on every view, configure DRF globally:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

Then a normal protected API can simply be:

```python
class ProfileAPIView(APIView):

    def get(self, request):

        return Response({
            'username': request.user.username
        })
```

However, login must be public.

Override the global permission:

```python
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    ...
```

The structure becomes:

```text
Global:
IsAuthenticated
       |
       +---- Profile → protected
       |
       +---- Orders → protected
       |
       +---- Logout → protected
       |
       +---- Login → AllowAny override
```

---

# 38. Authentication vs Permission

This is one of the most important DRF concepts.

## Authentication

Authentication answers:

> Who is this user?

Example:

```python
SessionAuthentication
```

It uses the session to identify the user.

Conceptually:

```text
sessionid
    |
    v
SessionAuthentication
    |
    v
request.user
```

## Permission

Permission answers:

> Is this user allowed to access this endpoint?

Example:

```python
IsAuthenticated
```

Conceptually:

```text
request.user
    |
    v
IsAuthenticated
    |
    +---- authenticated → allow
    |
    +---- anonymous → deny
```

The full process:

```text
SessionAuthentication
        |
        v
WHO?
        |
        v
request.user
        |
        v
IsAuthenticated
        |
        v
ALLOWED?
```

Authentication and authorization are not the same thing.

---

# 39. Session Backend Configuration

Django supports several session backends.

## 39.1 Database Session Backend

The traditional backend is:

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

Architecture:

```text
Browser
   |
   | sessionid
   v
Django
   |
   v
Database
   |
   v
django_session
```

Advantages:

- Persistent
- Easy to understand
- Good default for many applications
- Session data remains server-side

---

## 39.2 Cache Session Backend

Django can use a cache:

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
```

A common production cache is Redis.

Example:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
```

Architecture:

```text
Browser
   |
   | sessionid
   v
Django
   |
   v
Redis
   |
   v
Session
```

Cache sessions can provide very fast access.

---

## 39.3 Cached Database Sessions

Django also provides:

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
```

This uses both database persistence and cache optimization.

Conceptually:

```text
             +---- Cache
             |
Django ------+
             |
             +---- Database
```

This can be useful when you want database persistence while benefiting from caching.

---

## 39.4 Signed Cookie Sessions

Django also supports:

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
```

The session data is stored in the cookie and signed.

Architecture:

```text
Browser
   |
   | session data + signature
   v
Django
```

Important:

**Signed does not mean encrypted.**

Signing protects integrity: Django can detect that the cookie was modified.

It does not provide confidentiality.

Do not put sensitive information in a signed cookie merely because it is signed.

---

## Session Backend Comparison

| Backend | Storage | Database | Main characteristic |
|---|---|---:|---|
| `db` | Database | Yes | Persistent server-side sessions |
| `cache` | Cache | No | Fast cache-based sessions |
| `cached_db` | Database + cache | Yes | Persistence + cache |
| `signed_cookies` | Browser cookie | No | Client-side signed session data |

---

# 40. Session Security Settings

Important Django settings include:

## Secure Cookie

```python
SESSION_COOKIE_SECURE = True
```

This tells the browser to send the session cookie only over HTTPS.

Use this in production when your application is served over HTTPS.

---

## HttpOnly

```python
SESSION_COOKIE_HTTPONLY = True
```

This prevents normal JavaScript from reading the session cookie through:

```javascript
document.cookie
```

This is generally desirable for authentication cookies.

---

## SameSite

Example:

```python
SESSION_COOKIE_SAMESITE = 'Lax'
```

Possible values include:

```text
Lax
Strict
None
```

SameSite controls when browsers send cookies in cross-site contexts.

For cross-site cookie architectures, you may need:

```python
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
```

Only use `SameSite=None` when your architecture actually requires cross-site cookies.

---

## Session Lifetime

Example:

```python
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
```

This represents:

```text
14 days
```

because:

```text
60 seconds
× 60 minutes
× 24 hours
× 14 days
```

You can also configure:

```python
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

if you want the session cookie to expire when the browser closes.

---

# 41. Common Mistakes

## Mistake 1 — Forgetting `credentials`

For a cross-origin React request:

```javascript
fetch(url)
```

may not send the required cookies.

Use:

```javascript
fetch(url, {
    credentials: "include"
})
```

when your cookie/CORS configuration requires it.

---

## Mistake 2 — Sending the Session Cookie but No CSRF Token

For:

```text
GET
```

the CSRF token is generally not required.

For:

```text
POST
PUT
PATCH
DELETE
```

you need proper CSRF handling with SessionAuthentication.

For example:

```http
Cookie: sessionid=abc123
X-CSRFToken: xyz456
```

---

## Mistake 3 — Disabling CSRF

Avoid treating:

```python
@csrf_exempt
```

as the normal solution to a CSRF error in a session-authenticated application.

Instead, understand why the token is missing and configure the frontend and backend correctly.

---

## Mistake 4 — Thinking SessionAuthentication Uses JWT

It does not.

SessionAuthentication:

```text
SessionAuthentication
        |
        v
Django session
        |
        v
sessionid cookie
```

JWT authentication is a separate authentication mechanism:

```text
JWT
  |
  v
Bearer token
  |
  v
Token validation
```

---

## Mistake 5 — Storing Passwords in Sessions

Never do:

```python
request.session['password'] = password
```

The password is not needed in the session.

Django's authentication system handles passwords separately.

---

## Mistake 6 — Trusting a User ID Sent by React

Do not treat this as authentication:

```json
{
    "user_id": 7
}
```

The frontend should not determine which authenticated user it is.

With session authentication:

```text
sessionid
   |
   v
Django session
   |
   v
authenticated user
   |
   v
request.user
```

The server determines the authenticated identity.

---

## Mistake 7 — Storing Huge Data in Sessions

Avoid:

```python
request.session['huge_data'] = huge_object
```

Sessions should generally contain relatively small pieces of state.

Instead of storing a complete shopping cart in the session:

```python
request.session['cart_id'] = 25
```

and keep the actual cart data in the database.

---

# 42. Complete Request Lifecycle

## Login

```text
                     LOGIN
                       |
                       v
              username/password
                       |
                       v
                 authenticate()
                       |
                       v
                  User valid
                       |
                       v
                 login(request,user)
                       |
                       v
              Django authenticated session
                       |
                       v
                sessionid cookie
                       |
                       v
                     Browser
```

## Protected GET

```text
Browser
   |
   | sessionid
   v
Django
   |
   v
SessionAuthentication
   |
   v
request.user
   |
   v
IsAuthenticated
   |
   v
API
```

## Protected POST

```text
Browser / React
   |
   +---- sessionid
   |
   +---- X-CSRFToken
   |
   v
Django
   |
   +---- SessionAuthentication
   |
   +---- CSRF validation
   |
   v
IsAuthenticated
   |
   v
Protected API
```

## Logout

```text
Browser
   |
   | POST + session + CSRF
   v
Django
   |
   v
logout(request)
   |
   v
Authenticated session ended
   |
   v
User no longer authenticated
```

---

# 43. Final Project Structure

Your project should look approximately like:

```text
session_api/
│
├── manage.py
│
├── session_api/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── accounts/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── urls.py
    ├── views.py
    └── migrations/
```

---

# 44. Practice Exercise

After completing the basic implementation, build the following API:

```text
Authentication API
│
├── GET  /api/csrf/
│
├── POST /api/login/
│
├── GET  /api/profile/
│
├── POST /api/logout/
│
└── POST /api/protected/
```

Then extend it with your existing DRF Order API.

For example:

```text
SessionAuthentication
        |
        v
Login
        |
        v
Authenticated User
        |
        +--------------------+
        |                    |
        v                    v
     Category             Orders
        |                    |
        v                    v
 ModelViewSet          ModelViewSet
        |                    |
        v                    v
 Permissions            Permissions
```

Then implement:

```text
1. IsAuthenticated
2. IsAdminUser
3. Custom permission
4. Object-level permission
```

For example, an authenticated customer should only be able to access their own orders.

Conceptually:

```text
User A
   |
   +---- Order 1 → allowed
   +---- Order 2 → allowed

User B
   |
   +---- Order 1 → denied
   +---- Order 2 → allowed
```

This is the natural next step after understanding SessionAuthentication.

---

# 45. Key Concepts to Memorize

## SessionAuthentication

```text
SessionAuthentication
        |
        v
Django Session
        |
        v
Authenticated User
```

## Session Cookie

```text
sessionid
    |
    v
Identifies the session
```

## `request.user`

```python
request.user
```

is the authenticated Django user associated with the request.

## `IsAuthenticated`

```python
IsAuthenticated
```

protects an API endpoint from anonymous users.

## CSRF

For cookie/session-authenticated unsafe requests:

```text
POST
PUT
PATCH
DELETE
```

proper CSRF protection is required.

## Login

```python
authenticate()
login(request, user)
```

## Logout

```python
logout(request)
```

## Session Backends

```text
db
cache
cached_db
signed_cookies
```

---

# Final Mental Model

The most important diagram to remember is:

```text
                         USER
                           |
                           | username/password
                           v
                     /api/login/
                           |
                           v
                    authenticate()
                           |
                           v
                         User
                           |
                           v
                 login(request, user)
                           |
                           v
                       SESSION
                           |
                           v
                   sessionid COOKIE
                           |
                           v
                        BROWSER
                           |
              +------------+------------+
              |                         |
              v                         v
        GET /profile/            POST /protected/
              |                         |
              | sessionid               | sessionid
              |                         | X-CSRFToken
              v                         v
   SessionAuthentication       SessionAuthentication
              |                         |
              v                         v
        request.user              CSRF validation
              |                         |
              v                         v
      IsAuthenticated           IsAuthenticated
              |                         |
              v                         v
            ALLOW                     ALLOW
```

The complete relationship is:

```text
COOKIE
   |
   v
SESSION
   |
   v
AUTHENTICATION
   |
   v
request.user
   |
   v
PERMISSION
   |
   v
API ACCESS
```

And for state-changing requests:

```text
COOKIE
   +
CSRF TOKEN
   |
   v
SESSION AUTHENTICATION
   |
   v
PERMISSION
   |
   v
API
```

This is the core of **Django REST Framework SessionAuthentication**.
