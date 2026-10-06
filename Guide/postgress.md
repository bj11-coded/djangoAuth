# Comprehensive Django REST Framework Guide with PostgreSQL

A complete, production-ready guide to building scalable REST APIs with Django REST Framework, PostgreSQL, and Django ORM.

---

## 1. Project Setup

### 1.1 Python & Virtual Environment

```bash
# Check Python version (requires 3.8+)
python3 --version

# Create a project directory
mkdir django_api_project
cd django_api_project

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 1.2 Installing Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install Django, DRF, and database drivers
pip install django==4.2.8
pip install djangorestframework==3.14.0
pip install psycopg2-binary==2.9.9
pip install python-decouple==3.8
pip install django-cors-headers==4.3.1
pip install django-filter==23.5
pip install djangorestframework-simplejwt==5.3.2

# Create requirements.txt for easy reproduction
pip freeze > requirements.txt
```

### 1.3 PostgreSQL Setup

```bash
# macOS (using Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Windows: Download installer from postgresql.org

# Create a new database user and database
psql postgres
CREATE USER django_user WITH PASSWORD 'secure_password';
ALTER ROLE django_user SET client_encoding TO 'utf8';
ALTER ROLE django_user SET default_transaction_isolation TO 'read_committed';
ALTER ROLE django_user SET default_transaction_deferrable TO on;
ALTER ROLE django_user SET timezone TO 'UTC';
CREATE DATABASE django_api OWNER django_user;
GRANT ALL PRIVILEGES ON DATABASE django_api TO django_user;
\q
```

### 1.4 Django Project Scaffold

```bash
# Create Django project
django-admin startproject config .

# Create Django app
python manage.py startapp books

# Create additional app for managing authors
python manage.py startapp authors
```

### 1.5 Django Settings Configuration

**config/settings.py** - Key configurations:

```python
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'django_filters',
    'corsheaders',
    
    # Local apps
    'books.apps.BooksConfig',
    'authors.apps.AuthorsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# PostgreSQL Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='django_api'),
        'USER': config('DB_USER', default='django_user'),
        'PASSWORD': config('DB_PASSWORD', default='secure_password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'disable',
        }
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Create .env file in project root
```

**Create .env file** in project root:

```
SECRET_KEY=your-very-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=django_api
DB_USER=django_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
```

---

## 2. Data Modeling with Django ORM

### 2.1 Model Design

**authors/models.py** - Author model with custom manager:

```python
from django.db import models
from django.core.validators import URLValidator
from django.utils.timezone import now

class AuthorQuerySet(models.QuerySet):
    """Custom queryset for Author model"""
    def active(self):
        return self.filter(is_active=True)
    
    def with_book_count(self):
        return self.annotate(
            book_count=models.Count('books')
        )

class AuthorManager(models.Manager):
    """Custom manager for Author model"""
    def get_queryset(self):
        return AuthorQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def with_book_count(self):
        return self.get_queryset().with_book_count()

class Author(models.Model):
    """Author model"""
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = AuthorManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return self.name
```

**books/models.py** - Book and Publisher models:

```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from authors.models import Author

class Publisher(models.Model):
    """Publisher model"""
    name = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=100)
    founded_year = models.IntegerField(null=True, blank=True)
    website = models.URLField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Publishers'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Genre(models.Model):
    """Genre model"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class BookQuerySet(models.QuerySet):
    """Custom queryset for Book model"""
    def published(self):
        return self.filter(publication_date__isnull=False, is_published=True)
    
    def high_rated(self, rating=4.0):
        return self.filter(rating__gte=rating)
    
    def with_author_info(self):
        return self.select_related('author', 'publisher')
    
    def with_genre_count(self):
        return self.annotate(genre_count=models.Count('genres'))

class BookManager(models.Manager):
    """Custom manager for Book model"""
    def get_queryset(self):
        return BookQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def high_rated(self, rating=4.0):
        return self.get_queryset().high_rated(rating)
    
    def with_author_info(self):
        return self.get_queryset().with_author_info()

class Book(models.Model):
    """Book model"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    isbn = models.CharField(max_length=13, unique=True)
    
    # ForeignKey relationship
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books'
    )
    
    # ForeignKey to Publisher
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    
    # ManyToMany relationship
    genres = models.ManyToManyField(
        Genre,
        related_name='books'
    )
    
    # Book metadata
    publication_date = models.DateField(null=True, blank=True)
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    language = models.CharField(max_length=50, default='English')
    
    # Rating system
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = BookManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['author', 'is_published']),
            models.Index(fields=['-rating']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_book_per_author'
            )
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author.name}"
    
    @property
    def is_recent(self):
        """Check if book was created recently (within 30 days)"""
        from django.utils.timezone import now
        from datetime import timedelta
        return now() - self.created_at < timedelta(days=30)

class BookReview(models.Model):
    """Review model with OneToOne optional relationship"""
    book = models.OneToOneField(
        Book,
        on_delete=models.CASCADE,
        related_name='featured_review'
    )
    reviewer = models.CharField(max_length=255)
    content = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review of {self.book.title} by {self.reviewer}"
```

### 2.2 Running Migrations

```bash
# Create migrations for models
python manage.py makemigrations authors
python manage.py makemigrations books

# Review migration files
python manage.py showmigrations

# Apply migrations to database
python manage.py migrate

# Create superuser for admin
python manage.py createsuperuser
```

### 2.3 Admin Configuration

**authors/admin.py**:

```python
from django.contrib import admin
from .models import Author

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Personal Info', {
            'fields': ('name', 'email', 'bio', 'birth_date')
        }),
        ('Online Presence', {
            'fields': ('website',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
```

**books/admin.py**:

```python
from django.contrib import admin
from .models import Book, Publisher, Genre, BookReview

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'founded_year')
    search_fields = ('name', 'country')

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class BookReviewInline(admin.TabularInline):
    model = BookReview
    extra = 1

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'rating', 'is_published')
    list_filter = ('is_published', 'publication_date', 'genres', 'author')
    search_fields = ('title', 'isbn', 'author__name')
    filter_horizontal = ('genres',)
    inlines = [BookReviewInline]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'isbn')
        }),
        ('Author & Publisher', {
            'fields': ('author', 'publisher')
        }),
        ('Classification', {
            'fields': ('genres', 'language')
        }),
        ('Details', {
            'fields': ('pages', 'rating', 'publication_date')
        }),
        ('Status', {
            'fields': ('is_published',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
```

---

## 3. API Design with Django REST Framework

### 3.1 Serializers

**authors/serializers.py**:

```python
from rest_framework import serializers
from .models import Author

class AuthorSerializer(serializers.ModelSerializer):
    """Basic Author serializer"""
    book_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = [
            'id', 'name', 'email', 'bio', 'birth_date',
            'website', 'is_active', 'book_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'book_count']
    
    def get_book_count(self, obj):
        """Count books for this author"""
        return obj.books.count()

class AuthorDetailSerializer(serializers.ModelSerializer):
    """Detailed author with nested books"""
    from books.serializers import BookMinimalSerializer
    books = BookMinimalSerializer(many=True, read_only=True)
    
    class Meta:
        model = Author
        fields = [
            'id', 'name', 'email', 'bio', 'birth_date',
            'website', 'is_active', 'books', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'books']

class AuthorCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating authors"""
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = Author
        fields = ['name', 'email', 'bio', 'birth_date', 'website', 'is_active']
    
    def validate_email(self, value):
        """Ensure email is unique"""
        # Exclude current instance if updating
        queryset = Author.objects.filter(email=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("An author with this email already exists.")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        if not data.get('name'):
            raise serializers.ValidationError("Name is required.")
        return data
```

**books/serializers.py**:

```python
from rest_framework import serializers
from .models import Book, Publisher, Genre, BookReview
from authors.serializers import AuthorSerializer

class GenreSerializer(serializers.ModelSerializer):
    """Genre serializer"""
    class Meta:
        model = Genre
        fields = ['id', 'name', 'description']

class PublisherSerializer(serializers.ModelSerializer):
    """Publisher serializer"""
    book_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'country', 'founded_year', 'website', 'book_count']
        read_only_fields = ['id', 'book_count']
    
    def get_book_count(self, obj):
        return obj.books.count()

class BookMinimalSerializer(serializers.ModelSerializer):
    """Minimal book serializer for nested use"""
    class Meta:
        model = Book
        fields = ['id', 'title', 'isbn', 'rating', 'publication_date']
        read_only_fields = ['id']

class BookListSerializer(serializers.ModelSerializer):
    """Book list view serializer"""
    author_name = serializers.CharField(source='author.name', read_only=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True)
    genre_names = serializers.StringRelatedField(
        source='genres',
        many=True,
        read_only=True
    )
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'isbn', 'author_name', 'publisher_name',
            'rating', 'is_published', 'genre_names', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class BookDetailSerializer(serializers.ModelSerializer):
    """Detailed book serializer with nested relationships"""
    author = AuthorSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    featured_review = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description', 'isbn', 'author',
            'publisher', 'genres', 'publication_date', 'pages',
            'language', 'rating', 'is_published', 'featured_review',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_featured_review(self, obj):
        """Get featured review if exists"""
        if hasattr(obj, 'featured_review'):
            return BookReviewSerializer(obj.featured_review).data
        return None

class BookCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating books"""
    author_id = serializers.IntegerField(write_only=True)
    publisher_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        write_only=True,
        source='genres'
    )
    
    class Meta:
        model = Book
        fields = [
            'title', 'description', 'isbn', 'author_id', 'publisher_id',
            'genre_ids', 'publication_date', 'pages', 'language',
            'rating', 'is_published'
        ]
    
    def validate_isbn(self, value):
        """Validate ISBN"""
        if len(value) != 13:
            raise serializers.ValidationError("ISBN must be 13 characters long.")
        if not value.isdigit():
            raise serializers.ValidationError("ISBN must contain only digits.")
        return value
    
    def validate_rating(self, value):
        """Validate rating is between 0 and 5"""
        if not 0 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 0 and 5.")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        author_id = data.get('author_id')
        from authors.models import Author
        
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            raise serializers.ValidationError("Invalid author ID.")
        
        data['author'] = author
        return data
    
    def create(self, validated_data):
        """Handle creation with M2M relationship"""
        genres = validated_data.pop('genres', [])
        book = Book.objects.create(**validated_data)
        book.genres.set(genres)
        return book
    
    def update(self, instance, validated_data):
        """Handle update with M2M relationship"""
        genres = validated_data.pop('genres', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        if genres is not None:
            instance.genres.set(genres)
        
        return instance

class BookReviewSerializer(serializers.ModelSerializer):
    """Book review serializer"""
    class Meta:
        model = BookReview
        fields = ['id', 'book', 'reviewer', 'content', 'rating', 'created_at']
        read_only_fields = ['id', 'created_at']
```

### 3.2 ViewSets and Views

**authors/views.py**:

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from .models import Author
from .serializers import (
    AuthorSerializer,
    AuthorDetailSerializer,
    AuthorCreateUpdateSerializer
)

class AuthorViewSet(viewsets.ModelViewSet):
    """ViewSet for Author model"""
    queryset = Author.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return AuthorDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AuthorCreateUpdateSerializer
        return AuthorSerializer
    
    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        """Get all books by an author"""
        author = self.get_object()
        books = author.books.all()
        
        page = self.paginate_queryset(books)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active authors"""
        authors = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(authors, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_authors(self, request):
        """Get top authors by book count"""
        top_authors = Author.objects.annotate(
            book_count=Count('books')
        ).order_by('-book_count')[:5]
        
        serializer = self.get_serializer(top_authors, many=True)
        return Response(serializer.data)
```

**books/views.py**:

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Q
from .models import Book, Publisher, Genre, BookReview
from .serializers import (
    BookListSerializer,
    BookDetailSerializer,
    BookCreateUpdateSerializer,
    PublisherSerializer,
    GenreSerializer,
    BookReviewSerializer
)

class BookViewSet(viewsets.ModelViewSet):
    """ViewSet for Book model with advanced filtering"""
    queryset = Book.objects.select_related('author', 'publisher').prefetch_related('genres')
    permission_classes = [IsAuthenticated]
    filterset_fields = ['author', 'publisher', 'is_published', 'genres']
    search_fields = ['title', 'isbn', 'description']
    ordering_fields = ['title', 'rating', 'created_at', 'publication_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return BookDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BookCreateUpdateSerializer
        return BookListSerializer
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get reviews for a specific book"""
        book = self.get_object()
        try:
            review = book.featured_review
            serializer = BookReviewSerializer(review)
            return Response(serializer.data)
        except BookReview.DoesNotExist:
            return Response({'detail': 'No featured review'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def high_rated(self, request):
        """Get books with rating >= 4.0"""
        rating = request.query_params.get('rating', 4.0)
        books = self.queryset.filter(rating__gte=float(rating))
        
        page = self.paginate_queryset(books)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def published(self, request):
        """Get only published books"""
        books = self.queryset.filter(is_published=True)
        
        page = self.paginate_queryset(books)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_author(self, request):
        """Get books by specific author"""
        author_id = request.query_params.get('author_id')
        if not author_id:
            return Response(
                {'detail': 'author_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        books = self.queryset.filter(author_id=author_id)
        
        page = self.paginate_queryset(books)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get book statistics"""
        stats = {
            'total_books': Book.objects.count(),
            'published_books': Book.objects.filter(is_published=True).count(),
            'average_rating': Book.objects.aggregate(Avg('rating'))['rating__avg'],
            'books_by_genre': dict(
                Book.objects.values('genres__name')
                .annotate(count=Count('id'))
                .values_list('genres__name', 'count')
            ),
        }
        return Response(stats)

class PublisherViewSet(viewsets.ModelViewSet):
    """ViewSet for Publisher model"""
    queryset = Publisher.objects.annotate(book_count=Count('books'))
    serializer_class = PublisherSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'country']
    ordering_fields = ['name', 'book_count']

class GenreViewSet(viewsets.ModelViewSet):
    """ViewSet for Genre model"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name']
```

### 3.3 URL Routing

**config/urls.py**:

```python
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from authors.views import AuthorViewSet
from books.views import BookViewSet, PublisherViewSet, GenreViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'books', BookViewSet, basename='book')
router.register(r'publishers', PublisherViewSet, basename='publisher')
router.register(r'genres', GenreViewSet, basename='genre')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
```

---

## 4. Database and Migrations

### 4.1 Creating Migrations

```bash
# Create migrations for models
python manage.py makemigrations

# Show migration status
python manage.py showmigrations

# Show SQL for a specific migration
python manage.py sqlmigrate authors 0001

# Apply migrations
python manage.py migrate

# Rollback to specific migration
python manage.py migrate authors 0001
```

### 4.2 Seeding Data

**management/commands/seed_data.py**:

```python
from django.core.management.base import BaseCommand
from django.db import transaction
from authors.models import Author
from books.models import Book, Publisher, Genre

class Command(BaseCommand):
    help = 'Seed database with sample data'
    
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Create genres
        genres = []
        genre_names = ['Fiction', 'Non-Fiction', 'Science', 'History', 'Fantasy']
        for name in genre_names:
            genre, created = Genre.objects.get_or_create(name=name)
            genres.append(genre)
            if created:
                self.stdout.write(f'Created genre: {name}')
        
        # Create publishers
        publishers = []
        publisher_data = [
            {'name': 'Penguin Books', 'country': 'UK', 'founded_year': 1935},
            {'name': 'Simon & Schuster', 'country': 'USA', 'founded_year': 1924},
            {'name': 'Oxford University Press', 'country': 'UK', 'founded_year': 1586},
        ]
        for data in publisher_data:
            publisher, created = Publisher.objects.get_or_create(**data)
            publishers.append(publisher)
            if created:
                self.stdout.write(f'Created publisher: {data["name"]}')
        
        # Create authors
        authors = []
        author_data = [
            {
                'name': 'George Orwell',
                'email': 'george.orwell@example.com',
                'bio': 'English novelist and political commentator',
                'is_active': True
            },
            {
                'name': 'J.K. Rowling',
                'email': 'jk.rowling@example.com',
                'bio': 'British author of the Harry Potter series',
                'is_active': True
            },
            {
                'name': 'Carl Sagan',
                'email': 'carl.sagan@example.com',
                'bio': 'American astronomer and science communicator',
                'is_active': False
            },
        ]
        for data in author_data:
            author, created = Author.objects.get_or_create(**data)
            authors.append(author)
            if created:
                self.stdout.write(f'Created author: {data["name"]}')
        
        # Create books
        books_data = [
            {
                'title': '1984',
                'author': authors[0],
                'publisher': publishers[0],
                'isbn': '9780451524935',
                'description': 'Dystopian social science fiction novel',
                'pages': 328,
                'rating': 4.5,
                'genres': [genres[0], genres[3]]
            },
            {
                'title': 'Harry Potter and the Philosopher\'s Stone',
                'author': authors[1],
                'publisher': publishers[1],
                'isbn': '9780439708180',
                'description': 'A young wizard\'s first year at magic school',
                'pages': 309,
                'rating': 4.8,
                'genres': [genres[0], genres[4]]
            },
            {
                'title': 'Cosmos',
                'author': authors[2],
                'publisher': publishers[2],
                'isbn': '9780394503677',
                'description': 'Scientific exploration of the universe',
                'pages': 978,
                'rating': 4.6,
                'genres': [genres[1], genres[2]]
            },
        ]
        
        for data in books_data:
            genres_list = data.pop('genres')
            book, created = Book.objects.get_or_create(**data)
            if created:
                book.genres.set(genres_list)
                self.stdout.write(f'Created book: {data["title"]}')
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully'))
```

Run seeding:

```bash
python manage.py seed_data
```

### 4.3 Migration Best Practices

```python
# Good migration practices
# - Always use --name flag for clarity
# - Test migrations in development
# - Review generated SQL
# - Never use RunPython with raw imports in production migrations
# - Use squashmigrations to clean up history

python manage.py makemigrations --name add_book_isbn_index
python manage.py squashmigrations books 0001 0003
```

---

## 5. Advanced ORM Usage

### 5.1 Query Optimization

```python
# BAD: N+1 query problem
books = Book.objects.all()
for book in books:
    print(book.author.name)  # One query per book!

# GOOD: Using select_related (for ForeignKey/OneToOne)
books = Book.objects.select_related('author', 'publisher').all()
for book in books:
    print(book.author.name)  # No additional queries!

# GOOD: Using prefetch_related (for reverse ForeignKey and ManyToMany)
authors = Author.objects.prefetch_related('books').all()
for author in authors:
    for book in author.books.all():  # No additional queries!
        print(book.title)

# Advanced: Custom Prefetch for filtered relationships
from django.db.models import Prefetch

published_books = Book.objects.filter(is_published=True)
authors = Author.objects.prefetch_related(
    Prefetch('books', queryset=published_books)
).all()

# Check query count
from django.test.utils import override_settings
from django.db import connection
from django.test import TestCase

with override_settings(DEBUG=True):
    books = Book.objects.select_related('author').all()
    print(len(connection.queries))  # Print number of queries
```

### 5.2 Aggregations and Annotations

```python
from django.db.models import Count, Avg, Max, Min, Sum, Q

# Count
books_per_author = Author.objects.annotate(
    book_count=Count('books')
)

# Filter by annotation
prolific_authors = Author.objects.annotate(
    book_count=Count('books')
).filter(book_count__gte=5)

# Average rating
author_avg_rating = Author.objects.annotate(
    avg_rating=Avg('books__rating')
)

# Multiple annotations
book_stats = Book.objects.aggregate(
    total=Count('id'),
    avg_rating=Avg('rating'),
    max_pages=Max('pages'),
    min_pages=Min('pages')
)
# Returns: {'total': 10, 'avg_rating': 4.2, 'max_pages': 1000, 'min_pages': 150}

# Complex annotations with Q objects
books_stats = Book.objects.annotate(
    published_count=Count('id', filter=Q(is_published=True)),
    unpublished_count=Count('id', filter=Q(is_published=False))
)

# Group by
from django.db.models import F
books_by_author = Book.objects.values('author__name').annotate(
    count=Count('id'),
    avg_rating=Avg('rating')
).order_by('-count')
# Returns: [{'author__name': 'Author1', 'count': 5, 'avg_rating': 4.2}, ...]

# Using F expressions for field-based calculations
Book.objects.annotate(
    ratio=F('rating') * 2
)
```

### 5.3 Transactions and Atomic Operations

```python
from django.db import transaction
from django.db.models import F

# Using transaction context manager
@transaction.atomic
def create_author_with_books(author_data, books_data):
    author = Author.objects.create(**author_data)
    for book_data in books_data:
        book_data['author'] = author
        Book.objects.create(**book_data)
    return author

# Manual transaction control
with transaction.atomic():
    author = Author.objects.create(name="New Author", email="author@example.com")
    Book.objects.create(
        title="New Book",
        author=author,
        isbn="1234567890123"
    )

# Bulk operations
Book.objects.bulk_create([
    Book(title="Book1", author=author, isbn="1"),
    Book(title="Book2", author=author, isbn="2"),
], batch_size=100)

# Bulk update
Book.objects.filter(rating__lt=2).update(is_published=False)

# Transaction savepoints
with transaction.atomic():
    author = Author.objects.create(name="Test", email="test@example.com")
    
    sid = transaction.savepoint()
    try:
        book = Book.objects.create(
            title="Bad Book",
            author=author,
            isbn="invalid"  # Will fail
        )
    except:
        transaction.savepoint_rollback(sid)
    
    # Author still exists but book doesn't
    Book.objects.create(
        title="Good Book",
        author=author,
        isbn="9876543210123"
    )
    transaction.savepoint_commit(sid)
```

### 5.4 Raw SQL When Necessary

```python
from django.db import connection
from django.db.models import Model

# Raw queries
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT a.name, COUNT(b.id) as book_count
        FROM authors_author a
        LEFT JOIN books_book b ON a.id = b.author_id
        GROUP BY a.id
        ORDER BY book_count DESC
    """)
    columns = [col[0] for col in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]

# Raw queries with ORM fallback
books = Book.objects.raw("""
    SELECT * FROM books_book
    WHERE rating > %s
    ORDER BY rating DESC
""", [4.0])

# Parameterized queries (ALWAYS use parameters, never string formatting!)
Book.objects.raw(
    'SELECT * FROM books_book WHERE title = %s',
    [user_input]  # Safe from SQL injection
)

# Using connection for complex operations
from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT version();")
version = cursor.fetchone()
```

---

## 6. Testing and Debugging

### 6.1 Model Tests

**books/tests.py**:

```python
from django.test import TestCase
from django.utils.timezone import now
from datetime import timedelta
from .models import Book, Publisher, Genre
from authors.models import Author

class AuthorModelTest(TestCase):
    """Test cases for Author model"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data once for the entire test class"""
        cls.author = Author.objects.create(
            name="Test Author",
            email="test@example.com",
            bio="A test author"
        )
    
    def test_author_creation(self):
        """Test creating an author"""
        self.assertEqual(self.author.name, "Test Author")
        self.assertTrue(self.author.is_active)
    
    def test_author_string_representation(self):
        """Test author __str__ method"""
        self.assertEqual(str(self.author), "Test Author")
    
    def test_author_email_validation(self):
        """Test that email must be unique"""
        with self.assertRaises(Exception):
            Author.objects.create(
                name="Duplicate",
                email="test@example.com"
            )
    
    def test_author_with_books(self):
        """Test author with books relationship"""
        book = Book.objects.create(
            title="Test Book",
            description="Test",
            isbn="1234567890123",
            author=self.author,
            pages=100
        )
        self.assertIn(book, self.author.books.all())
        self.assertEqual(self.author.books.count(), 1)

class BookModelTest(TestCase):
    """Test cases for Book model"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data"""
        cls.author = Author.objects.create(
            name="Author Name",
            email="author@example.com"
        )
        cls.publisher = Publisher.objects.create(
            name="Test Publisher",
            country="USA"
        )
        cls.genre = Genre.objects.create(
            name="Fiction",
            description="Fictional works"
        )
        cls.book = Book.objects.create(
            title="Test Book",
            description="A test book",
            isbn="1234567890123",
            author=cls.author,
            publisher=cls.publisher,
            pages=300,
            rating=4.5
        )
        cls.book.genres.add(cls.genre)
    
    def test_book_creation(self):
        """Test creating a book"""
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.rating, 4.5)
    
    def test_book_isbn_unique(self):
        """Test ISBN uniqueness constraint"""
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Duplicate ISBN",
                description="Test",
                isbn="1234567890123",
                author=self.author,
                pages=200
            )
    
    def test_book_relationships(self):
        """Test book relationships"""
        self.assertEqual(self.book.author, self.author)
        self.assertEqual(self.book.publisher, self.publisher)
        self.assertIn(self.genre, self.book.genres.all())
    
    def test_book_is_recent(self):
        """Test is_recent property"""
        self.assertTrue(self.book.is_recent)
        
        # Create old book
        old_book = Book.objects.create(
            title="Old Book",
            description="Test",
            isbn="9876543210987",
            author=self.author,
            pages=200
        )
        old_book.created_at = now() - timedelta(days=60)
        old_book.save()
        
        self.assertFalse(old_book.is_recent)
    
    def test_book_queryset_published(self):
        """Test published() queryset method"""
        published = Book.objects.published()
        self.assertIn(self.book, published)
        
        unpublished_book = Book.objects.create(
            title="Unpublished",
            description="Test",
            isbn="5555555555555",
            author=self.author,
            pages=200,
            is_published=False
        )
        
        self.assertNotIn(unpublished_book, Book.objects.published())
```

### 6.2 API Tests

**books/tests/test_views.py**:

```python
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from authors.models import Author
from books.models import Book, Publisher, Genre

class BookAPITest(TestCase):
    """Test cases for Book API endpoints"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data"""
        # Create user for authentication
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test data
        cls.author = Author.objects.create(
            name="Test Author",
            email="author@example.com"
        )
        cls.publisher = Publisher.objects.create(
            name="Test Publisher",
            country="USA"
        )
        cls.genre = Genre.objects.create(name="Fiction")
        
        cls.book = Book.objects.create(
            title="Test Book",
            description="A test book",
            isbn="1234567890123",
            author=cls.author,
            publisher=cls.publisher,
            pages=300,
            rating=4.5
        )
        cls.book.genres.add(cls.genre)
    
    def setUp(self):
        """Set up client for each test"""
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_list_books(self):
        """Test listing books"""
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_retrieve_book(self):
        """Test retrieving a single book"""
        response = self.client.get(f'/api/books/{self.book.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Book")
    
    def test_create_book(self):
        """Test creating a book"""
        data = {
            'title': 'New Book',
            'description': 'A new book',
            'isbn': '9999999999999',
            'author_id': self.author.id,
            'publisher_id': self.publisher.id,
            'genre_ids': [self.genre.id],
            'pages': 250,
            'rating': 3.5
        }
        response = self.client.post('/api/books/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
    
    def test_update_book(self):
        """Test updating a book"""
        data = {'rating': 5.0}
        response = self.client.patch(
            f'/api/books/{self.book.id}/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.rating, 5.0)
    
    def test_delete_book(self):
        """Test deleting a book"""
        response = self.client.delete(f'/api/books/{self.book.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)
    
    def test_book_high_rated_action(self):
        """Test high_rated custom action"""
        response = self.client.get('/api/books/high_rated/?rating=4.0')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_book_statistics_action(self):
        """Test statistics custom action"""
        response = self.client.get('/api/books/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_books'], 1)
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access API"""
        client = APIClient()
        response = client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthorAPITest(TestCase):
    """Test cases for Author API endpoints"""
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        cls.author = Author.objects.create(
            name="Test Author",
            email="author@example.com"
        )
    
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_list_authors(self):
        """Test listing authors"""
        response = self.client.get('/api/authors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_author_active_action(self):
        """Test active authors action"""
        Author.objects.create(
            name="Inactive Author",
            email="inactive@example.com",
            is_active=False
        )
        response = self.client.get('/api/authors/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
```

### 6.3 Debugging Tips

```python
# Enable SQL logging
import logging
logger = logging.getLogger('django.db.backends')
logger.setLevel(logging.DEBUG)

# Print queries
from django.db import connection
print(connection.queries)

# Use django-debug-toolbar
pip install django-debug-toolbar

# Check query count
from django.test.utils import override_settings
from django.db import connection, reset_queries

@override_settings(DEBUG=True)
def test_query_count():
    reset_queries()
    books = Book.objects.select_related('author').all()
    print(f"Queries executed: {len(connection.queries)}")

# Use ipdb for debugging
import ipdb; ipdb.set_trace()

# Check model fields
from books.models import Book
print(Book._meta.fields)
print(Book._meta.many_to_many)
```

---

## 7. Deployment Considerations

### 7.1 Production Settings

Create **config/settings/production.py**:

```python
from .settings import *  # Import base settings

# Security settings
SECRET_KEY = config('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])

# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database configuration
DATABASES['default']['CONN_MAX_AGE'] = 600
DATABASES['default']['OPTIONS']['sslmode'] = 'require'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```

Update **config/settings.py** to use environment:

```python
ENVIRONMENT = config('ENVIRONMENT', default='development')

if ENVIRONMENT == 'production':
    from .settings.production import *
```

### 7.2 Running with Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4

# With environment variables
gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class sync \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
```

### 7.3 Nginx Configuration

Create **nginx.conf**:

```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;
    
    client_max_body_size 100M;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/javascript application/json;
    gzip_min_length 1000;
    
    location /static/ {
        alias /path/to/project/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias /path/to/project/media/;
    }
    
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### 7.4 Security Best Practices

```python
# CSRF Protection - enabled by default
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=lambda v: [s.strip() for s in v.split(',')])

# Content Security Policy
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),
    'style-src': ("'self'", "'unsafe-inline'"),
}

# Authentication
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config('SECRET_KEY'),
}

# Rate limiting
pip install djangorestframework-ratelimit

# Custom permission classes
from rest_framework.permissions import BasePermission

class IsAuthorOrReadOnly(BasePermission):
    """Allow access only to authors of an object, or read-only access"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
```

---

## 8. Minimal Runnable Example

Here's a complete, minimal example to get started:

### File Structure
```
django_api/
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── books/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── tests.py
├── .env
└── requirements.txt
```

### Quick Start

```bash
# 1. Setup
python3 -m venv venv
source venv/bin/activate
pip install django djangorestframework psycopg2-binary python-decouple

# 2. Create project
django-admin startproject config .
python manage.py startapp books

# 3. Add this code and run
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Complete Code

**models.py**:
```python
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    pages = models.IntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
```

**serializers.py**:
```python
from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'pages', 'rating', 'created_at']
        read_only_fields = ['id', 'created_at']
```

**views.py**:
```python
from rest_framework import viewsets
from .models import Book
from .serializers import BookSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```

**config/urls.py**:
```python
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from books.views import BookViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
```

**config/settings.py** - Update INSTALLED_APPS and DATABASES:
```python
INSTALLED_APPS = [
    # ... existing ...
    'rest_framework',
    'books.apps.BooksConfig',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_api',
        'USER': 'django_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

---

## 9. Quick Reference Cheat Sheet

### Common Serializer Patterns

```python
# Field types
from rest_framework import serializers

fields = {
    'CharField': serializers.CharField(max_length=100),
    'IntegerField': serializers.IntegerField(min_value=0),
    'FloatField': serializers.FloatField(),
    'DecimalField': serializers.DecimalField(max_digits=5, decimal_places=2),
    'BooleanField': serializers.BooleanField(),
    'DateField': serializers.DateField(),
    'DateTimeField': serializers.DateTimeField(),
    'ListField': serializers.ListField(child=serializers.CharField()),
    'DictField': serializers.DictField(),
    'ChoiceField': serializers.ChoiceField(choices=['option1', 'option2']),
}

# Relationships
relationships = {
    'ForeignKey': serializers.PrimaryKeyRelatedField(queryset=Model.objects.all()),
    'Nested': NestedSerializer(read_only=True),
    'Reverse ForeignKey': serializers.StringRelatedField(many=True, read_only=True),
    'ManyToMany': serializers.PrimaryKeyRelatedField(many=True, queryset=Model.objects.all()),
}
```

### DRF Permissions

```python
from rest_framework import permissions

# Built-in permissions
permissions = {
    'AllowAny': permissions.AllowAny(),
    'IsAuthenticated': permissions.IsAuthenticated(),
    'IsAdminUser': permissions.IsAdminUser(),
    'IsAuthenticatedOrReadOnly': permissions.IsAuthenticatedOrReadOnly(),
    'DjangoObjectPermissions': permissions.DjangoObjectPermissions(),
    'DjangoModelPermissions': permissions.DjangoModelPermissions(),
}

# Custom permission
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
```

### ORM Query Helpers

```python
# Common queryset methods
qs = Model.objects
    .all()                          # All objects
    .filter(active=True)            # Filter
    .exclude(archived=True)         # Exclude
    .get(id=1)                      # Get single
    .create(name="test")            # Create
    .bulk_create([obj1, obj2])      # Bulk create
    .update(status="active")        # Update
    .delete()                       # Delete
    .values()                       # Dict format
    .values_list()                  # List format
    .distinct()                     # Remove duplicates
    .order_by('-created_at')        # Order
    .reverse()                      # Reverse order
    .first()                        # First object
    .last()                         # Last object
    .count()                        # Count
    .exists()                       # Check exists
    .explain()                      # Show execution plan

# Filtering
Model.objects.filter(
    name__iexact='test',           # Case-insensitive exact
    age__gt=18,                     # Greater than
    created__date=today,            # Date comparison
    status__in=['active', 'pending'] # In list
)
```

### ViewSet Actions

```python
class MyViewSet(viewsets.ModelViewSet):
    # Override to change serializer by action
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DetailSerializer
        return ListSerializer
    
    # Override to change queryset by action
    def get_queryset(self):
        if self.action == 'list':
            return MyModel.objects.filter(published=True)
        return MyModel.objects.all()
    
    # Custom action
    @action(detail=True, methods=['post'])
    def set_published(self, request, pk=None):
        obj = self.get_object()
        obj.published = True
        obj.save()
        return Response({'status': 'published'})
```

### Status Codes

```python
from rest_framework import status

common_codes = {
    'HTTP_200_OK': 200,
    'HTTP_201_CREATED': 201,
    'HTTP_204_NO_CONTENT': 204,
    'HTTP_400_BAD_REQUEST': 400,
    'HTTP_401_UNAUTHORIZED': 401,
    'HTTP_403_FORBIDDEN': 403,
    'HTTP_404_NOT_FOUND': 404,
    'HTTP_500_INTERNAL_SERVER_ERROR': 500,
}
```

---

## 10. Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT APPLICATION                       │
│                    (Web, Mobile, Desktop)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                       HTTP/HTTPS Requests
                             │
┌─────────────────────────────▼────────────────────────────────────┐
│                         NGINX/GUNICORN                           │
│              (Reverse Proxy & Application Server)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌─────────────────────────────▼────────────────────────────────────┐
│                      DJANGO APPLICATION                         │
├──────────────────────────────────────────────────────────────────┤
│                       URL ROUTING (urls.py)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ router.register('books', BookViewSet)                    │   │
│  │ router.register('authors', AuthorViewSet)                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    VIEWSETS / VIEWS                      │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │ BookViewSet (CRUD + Custom Actions)             │   │   │
│  │  │ - list()          → GET /api/books/             │   │   │
│  │  │ - create()        → POST /api/books/            │   │   │
│  │  │ - retrieve()      → GET /api/books/{id}/        │   │   │
│  │  │ - update()        → PUT /api/books/{id}/        │   │   │
│  │  │ - destroy()       → DELETE /api/books/{id}/     │   │   │
│  │  │ - high_rated()    → GET /api/books/high_rated/  │   │   │
│  │  │ - statistics()    → GET /api/books/statistics/  │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            SERIALIZERS (Validation & Data)              │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │ BookListSerializer                              │   │   │
│  │  │ BookDetailSerializer                            │   │   │
│  │  │ BookCreateUpdateSerializer                      │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          PERMISSIONS & AUTHENTICATION                   │   │
│  │  - IsAuthenticated                                      │   │
│  │  - Custom permission classes                           │   │
│  │  - Token/JWT validation                                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │             DJANGO ORM (Model Access)                   │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │ QuerySets & Managers                            │   │   │
│  │  │ - select_related() → Reduce queries             │   │   │
│  │  │ - prefetch_related() → Optimize M2M            │   │   │
│  │  │ - annotate() → Aggregate data                   │   │   │
│  │  │ - filter() → Query filtering                    │   │   │
│  │  │ - transactions → ACID compliance                │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              DJANGO MODELS (Schema)                      │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │ Book                                             │   │   │
│  │  │  ├── title (CharField)                          │   │   │
│  │  │  ├── author (ForeignKey → Author)               │   │   │
│  │  │  ├── publisher (ForeignKey → Publisher)         │   │   │
│  │  │  ├── genres (ManyToMany → Genre)                │   │   │
│  │  │  └── rating (DecimalField)                      │   │   │
│  │  │                                                  │   │   │
│  │  │ Author                                          │   │   │
│  │  │  ├── name (CharField)                           │   │   │
│  │  │  ├── email (EmailField, unique)                 │   │   │
│  │  │  └── is_active (BooleanField)                   │   │   │
│  │  │                                                  │   │   │
│  │  │ Publisher, Genre, BookReview...                 │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬───────────────────────────────┘
                                   │
                           SQL Queries
                                   │
┌──────────────────────────────────▼───────────────────────────────┐
│                      POSTGRESQL DATABASE                         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ books_book   │  │ authors_auth │  │ books_pub    │           │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤           │
│  │ id (PK)      │  │ id (PK)      │  │ id (PK)      │           │
│  │ title        │  │ name         │  │ name         │           │
│  │ isbn (UQ)    │  │ email (UQ)   │  │ country      │           │
│  │ author_id(FK)├──┤ active       │  │ founded_year │           │
│  │ publisher_id │──┤              │  │              │           │
│  │ rating       │  │ created_at   │  │ created_at   │           │
│  │ created_at   │  │ updated_at   │  │ updated_at   │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│       │                 │                   │                    │
│       │ Many-to-Many    │                   │                    │
│       └─────────────────┼───────────────────┘                    │
│                         │                                         │
│  ┌──────────────────────▼──────────────────┐                    │
│  │ books_book_genres                       │                    │
│  ├─────────────────────────────────────────┤                    │
│  │ id (PK)                                 │                    │
│  │ book_id (FK → books_book)               │                    │
│  │ genre_id (FK → books_genre)             │                    │
│  └─────────────────────────────────────────┘                    │
│                                                                  │
│  Indexes & Constraints                                           │
│  - Unique constraints on isbn, email                            │
│  - Indexed fields: isbn, author_id, rating, created_at          │
│  - Foreign key constraints for referential integrity            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────┐
│                    REQUEST/RESPONSE FLOW                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ CLIENT REQUEST: GET /api/books/                                 │
│         │                                                        │
│         ▼                                                        │
│ URL ROUTER matches: BookViewSet.list()                          │
│         │                                                        │
│         ▼                                                        │
│ PERMISSION CHECKS: IsAuthenticated?                             │
│         │                                                        │
│         ├─ No → HTTP 401 Unauthorized                           │
│         │                                                        │
│         └─ Yes ▼                                                │
│          FILTERING & PAGINATION                                 │
│         │  - DjangoFilterBackend                                │
│         │  - SearchFilter                                       │
│         │  - OrderingFilter                                     │
│         │  - PageNumberPagination                               │
│         │                                                        │
│         ▼                                                        │
│ QUERYSET OPTIMIZATION                                           │
│         │  - select_related('author', 'publisher')             │
│         │  - prefetch_related('genres')                         │
│         │                                                        │
│         ▼                                                        │
│ DATABASE QUERY (Single optimized query)                         │
│         │  SELECT books_book.*, authors_author.*, ...           │
│         │  FROM books_book                                      │
│         │  LEFT JOIN authors_author ON ...                      │
│         │  WHERE ...                                            │
│         │                                                        │
│         ▼                                                        │
│ SERIALIZATION                                                   │
│         │  - Validate data                                      │
│         │  - Transform to JSON                                  │
│         │  - Include nested objects                             │
│         │                                                        │
│         ▼                                                        │
│ RESPONSE: HTTP 200 OK                                           │
│         │                                                        │
│         ▼                                                        │
│ CLIENT receives JSON with paginated results                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Deployment Checklist

- [ ] Security settings configured (DEBUG=False, ALLOWED_HOSTS, etc.)
- [ ] Secret key rotated and secured
- [ ] Database backed up and optimized
- [ ] Static files collected and served via CDN
- [ ] HTTPS/SSL certificate installed
- [ ] Logging configured for errors
- [ ] Rate limiting implemented
- [ ] Database migrations tested in staging
- [ ] API documentation generated
- [ ] Load testing performed
- [ ] Monitoring and alerts set up
- [ ] Backup strategy implemented

---

## References & Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Real Python Django Tutorials](https://realpython.com/learning-paths/django-web-development/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)