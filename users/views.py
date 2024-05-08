from django.shortcuts import render,redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib import auth
from django.http import JsonResponse,HttpResponse, HttpResponseBadRequest,HttpResponseForbidden
from .models import User

from django.contrib.auth import authenticate,get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
# Create your views here.

class LoginView(APIView):
    def post(self, request):
        email=request.data.get('email')
        password=request.data.get('password')
        print(email)
        # User=auth.get_user_model()

        try:
            user=User.objects.get(email=email)
            if user.check_password(password):
                auth_user=auth.authenticate(email=email,password=password)
                print(auth_user)
                if auth_user is not None:
                    auth.login(request,user)
                    print(user.is_active)
                    user_metadata={
                        'firstName':user.first_name,
                        'lastName':user.last_name,
                        'grantee':user.grantee,
                        'role':user.role,
                    }
                    return Response({'email':user.email,'metadata':user_metadata})
                else:
                    print('user is none')
                    return HttpResponseForbidden(JsonResponse({"message":"Could not authenticate user"}))
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
                'firstName':user.first_name,
                'lastName':user.last_name,
                'grantee':user.grantee,
                'role':user.role,
            }
            return Response({'email':email,'user_metadata':user_metadata})
        
class LogoutView(APIView):
    def post(self,request):
        email=request.data.get('email')

        User=auth.get_user_model()
        try:
            user=User.objects.get(email=email)
            auth.logout(request)

            return Response({'message':'User logout successful'})
        except User.DoesNotExist:
            return HttpResponseForbidden(JsonResponse({'message':'The email is not a registered email'}))
        


#activate user email
def activate(request,uidb64,token):
    User=get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        print(uid)
        user = User.objects.get(email=uid)
        print(user)
    except:
        user=None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        
        # messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('http://coastalerosion.rcmrd.org/#/login')
