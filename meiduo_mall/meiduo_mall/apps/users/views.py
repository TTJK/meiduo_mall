from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from .serializers import UserDetailSerializer, EmailSerializer,UserAddressSerializer,AddressTitleSerializer,CreateUserSerializer
from . import serializers,constants
from rest_framework.views import APIView
from .models import User
from rest_framework.response import Response
from rest_framework import mixins

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

class AddressViewSet(mixins.CreateModelMixin,mixins.UpdateModelMixin,GenericViewSet):
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted = False)

    def list(self,request,*args,**kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many = True)
        user = self.request.user

        return Response({
            'user_id':user.id,
            'default_address_id':user.default_address_id,
            'limit':constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses':serializer.data,
            })

    def create(self, request, *args, **kwargs):
        """地址新增"""

        count = request.user.addresses.all().count()
        # co = Address.objects.filter(user=request.user).count()

        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '用户地址超过上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super(AddressViewSet, self).create(request, *args, **kwargs)
        # # 创建序列化器进行反序列化
        # serializer = self.get_serializer(data=request.data)
        # # 数据校验
        # serializer.is_valid(raise_exception=True)
        # # 保存数据
        # serializer.save()
        # # self.request.user
        # return Response(serializer.data)

        # delete /addresses/<pk>/

    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

        # put /addresses/pk/status/

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)