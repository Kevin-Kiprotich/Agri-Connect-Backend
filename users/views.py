from django.shortcuts import render,redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib import auth
from django.http import JsonResponse,HttpResponse, HttpResponseBadRequest,HttpResponseForbidden
from .models import User

from django.core.mail import EmailMessage
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
                auth.login(request,user)
                print(user.is_active)
                user_metadata={
                    'firstName':user.first_name,
                    'lastName':user.last_name,
                    'grantee':user.grantee,
                    'role':user.role,
                    'email':user.email
                }
                if user.is_active:
                    return Response({'email':user.email,'metadata':user_metadata})
                else:
                    mail_subject = "Activate your user account."
                    message = render_to_string("template_activate_account.html", {
                        'first_name': user.first_name,
                        'last_name':user.last_name,
                        'domain': get_current_site(request).domain,
                        'uid': urlsafe_base64_encode(force_bytes(email)),
                        'token': account_activation_token.make_token(user),
                        "protocol": 'https' if request.is_secure() else 'http'
                    })
                    mail = EmailMessage(mail_subject, message, to=[email])
                    mail.content_subtype = 'html'
                    if mail.send():
                        print("Email sent")
                        return HttpResponseBadRequest(JsonResponse({'message':'Email not verified. A verification email has been sent to you.'}))
                    else:
                        print('Email not sent')
                        return HttpResponseBadRequest(JsonResponse({'message':'Could not send verification email. Please make sure you use a valid email.'}))
                
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
            user.is_active=False
            user.save()
            user_metadata={
                'firstName':user.first_name,
                'lastName':user.last_name,
                'grantee':user.grantee,
                'role':user.role,
            }
            mail_subject = "Activate your user account."
            message = render_to_string("template_activate_account.html", {
                'first_name': first_name,
                'last_name':last_name, 
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(email)),
                'token': account_activation_token.make_token(user),
                "protocol": 'https' if request.is_secure() else 'http'
            })
            mail = EmailMessage(mail_subject, message, to=[email])
            mail.content_subtype = 'html'  # Set the content type to HTML
            # email.attach_alternative(message, 'text/html')
            print('sending message')
            if mail.send():
                print("Email sent")
                return Response({'email':email,'user_metadata':user_metadata})
            else:
                print('Email not sent')
                return HttpResponseBadRequest(JsonResponse({'message':'Could not send verification email. Please make sure you use a valid email.'}))
            
        
class LogoutView(APIView):
    def post(self,request):
        email=request.data.get('email')

        print(email)
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
        return redirect('http://139.84.235.200/#/')


"""
    Sequence to reset passwords.
"""
class UpdatePassword(APIView):
    def post(self,request):
        email=request.data.get('email')
        try:
            user=User.objects.get(email=email)
            mail_subject = "Reset Your Password." 
            message = render_to_string("template_change_password.html", {
                'user': user,
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(email)),
                'token': account_activation_token.make_token(user),
                "protocol": 'https' if request.is_secure() else 'http'
            })
            mail = EmailMessage(mail_subject, message, to=[email])
            mail.content_subtype = 'html'  # Set the content type to HTML
            # email.attach_alternative(message, 'text/html')
            # email = EmailMultiAlternatives(mail_subject, message, to=[email])
            if mail.send():
                print(f"Email sent for {email}")
                return Response({'Success':True,'Message':'Check your email for a verification alert'})
            else:
                print(f'Email not sent for {email}')
                return Response({'Success':False,'Message':'Trouble sending email. Make sure you have entered a valid email.'})
            
        except User.DoesNotExist:
            return Response({'Success':False,'Message':'Email is not registered'})


# Redirect when the access token link is clicked.
def update(request,uidb64,token):
    User=get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        print(uid)
        user = User.objects.get(email=uid)
        print(user)
        
        userEmail=user.email
        print(userEmail)
    except:
        user=None
    if user is not None and account_activation_token.check_token(user, token):
        return redirect(f'http://139.84.235.200/#/')
    

class changePassword(APIView):
    def post(self,request):
        User=get_user_model()
        # email=request.data.get('email')
        token=request.data.get('token')
        uidb64=request.data.get('uid')
        password=request.data.get('password')
        uid=force_str(urlsafe_base64_decode(uidb64))
        
        print(uid)
        print(password)
        
        try:
            user=User.objects.get(email=uid)
            user.set_password(password)
            user.save()
            print('passoword changed')
            return Response({'Success':True,'Message':'Password Changed Successfully'})
        except User.DoesNotExist:
            return HttpResponseBadRequest(JsonResponse({'Success':False,'Message':'Email not recognized'}))
