from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
# Create your views here.
from rest_framework.permissions import IsAuthenticated

from .serializers import UserDetailSerializer, EmailSerializer
from . import serializers
from rest_framework.views import APIView
from .models import User
from rest_framework.response import Response

class UserView(CreateAPIView):
    serializer_class = serializers.CreateUserSerializer

class UsernameCountView(APIView):
    def get(self,request,username):
        count = User.objects.filter(username=username).count()

        data = {
            'username':username,
            'count':count
            }
        return Response(data)

class MobileCountView(APIView):
    def get(self,request,mobile):
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile':mobile,
            'count':count
            }
        return Response(data)




class UserDetailView(RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class EmailView(UpdateAPIView):
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class VerifyEmailView(APIView):
    def get(self, request):

        token = request.query_params.get('token')
        if not token:
            return Response({'message':'缺少token'},status=status.HTTP_400_BAD_REQUEST)
        user = User.check_verify_email_url(token)
        print(user)
        if not user:
            return Response({'message': '无效的token'}, status=status.HTTP_400_BAD_REQUEST)
        user.email_active = True
        user.save()
        return Response({'message':'邮箱验证成功'})
