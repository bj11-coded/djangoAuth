from django.shortcuts import render
from rest_framework import viewsets
from .models import Student
from .serializer import StudentSerializer

# Create your views here.
#  using modelviewSet and default route

class StudentViewSet(viewsets.ModelViewSet):

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'rollNo'

    


