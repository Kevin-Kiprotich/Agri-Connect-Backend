from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib import auth
from django.http import JsonResponse,HttpResponse, HttpResponseBadRequest,HttpResponseForbidden
from .models import User
# Create your views here.

class LoginView(APIView):
    def post(self, request):
        email=request.data.get('email')
        password=request.data.get('password')
        print(email)
        # User=auth.get_user_model()

        try:
            print(User.objects.all().values())
            user=User.objects.get(email=email)
            if user.check_password(password):
                # auth_user=auth.authenticate(email=email,password=password)
                auth.login(request,user)
                print(user.is_active)
                user_metadata={
                    'first_name':user.first_name,
                    'last_name':user.last_name,
                    'grantee':user.grantee,
                    'role':user.role,
                }
                return Response({'email':user.email,'metadata':user_metadata})
            else:
                return HttpResponseForbidden(JsonResponse({"message":"Email and password do not match"}))
        except User.DoesNotExist:
            return HttpResponseBadRequest(JsonResponse({'message':'Your email is not registered'}))
        
class SignUpView(APIView):
    def post(self,request):
        email=request.data.get('email')
        first_name=request.data.get('first_name')
        last_name=request.data.get('last_name')
        grantee=request.data.get('grantee')
        role=request.data.get('role')
        password=request.data.get('password')

        try:
            user=User.objects.get(email=email)
            return HttpResponseBadRequest(JsonResponse({'message':'The email is already taken'}))
        except User.DoesNotExist:
            user=User.objects.create_user(email=email,first_name=first_name,last_name=last_name,grantee=grantee,role=role,password=password)
            user.save()
            user_metadata={
                'first_name':user.first_name,
                'last_name':user.last_name,
                'grantee':user.grantee,
                'role':user.role,
            }
            return Response({'email':email,'user_metadata':user_metadata})
