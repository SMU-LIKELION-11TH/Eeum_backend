from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from question.serializers import QuestionSerializer
from word.models import Edit
from word.serializers import EditSerializer
from .models import User

import requests

from .serializers import UserSerializer, EditEasySerializer, UserCreateSerializer, QuestionEasySerializer
from search.serializers import WordSerializer

@permission_classes((AllowAny,))
class KaKaoCallBackView(APIView):
    def post(self, request):
        print(request.data)
        username = str(request.data["id"])
        age = int(request.data["age"][:2])

        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, password=None,age = age)
            user.set_nickname()
        user.age = age
        user.save()

        refresh = RefreshToken.for_user(user)
        print(Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
        }).data)
        return Response(data = {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
        })

@permission_classes((AllowAny,))
class RefreshAccessToken(APIView):
    def post(self,request):
        print(request.data)
        refresh_token = request.data["refresh"]
        if not refresh_token:
            return Response({'error': 'Refresh 토큰이 필요합니다'}, status=401)

        try:
            refresh_token = RefreshToken(refresh_token)
            access_token = str(refresh_token.access_token)

            return Response({'access': access_token,'refresh':str(refresh_token)})
        except Exception as e:
            return Response({'error': '유효하지 않은 Refresh 토큰'}, status=401)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class UserInfo(APIView):
    def get(self,request):
        serializer = UserSerializer(instance=request.user)
        return Response(serializer.data)

    def put(self,request):
        user = request.user
        user.nickname = request.data["nickname"]
        user.save()
        resp = UserSerializer(request.user).data
        return Response(resp, status=200)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class UserWord(APIView):
    def get(self,request):
        words = request.user.word_set.all().order_by("-created_at")
        response = WordSerializer(words,many = True).data
        return Response(response)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class UserWordList(APIView):
    def get(self,request):
        words = request.user.word_set.all().order_by("-created_at")
        words = WordSerializer(words,many = True).data
        response = {
            "user" : request.user.nickname,
            "words" : words
        }
        return Response(response)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class UserQuestion(APIView):
    def get(self,request):
        questions = request.user.question_set.all().order_by("-created_at")
        response = QuestionEasySerializer(questions,many = True).data
        return Response(response)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class UserQuestionList(APIView):
    def get(self,request):
        questions = request.user.question_set.all().order_by("-created_at")
        questions = QuestionSerializer(questions,many = True).data
        data = {
            "user" : request.user.nickname,
            "questions" : questions
        }
        return Response(data)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class UserEdit(APIView):
    def get(self,request):
        edits = Edit.objects.filter(author = request.user).order_by("created_at")
        response = EditEasySerializer(edits,many = True).data
        return Response(response)

@permission_classes((IsAuthenticated,))
@authentication_classes([JWTAuthentication])
class UserEditList(APIView):
    def get(self,request):
        edits = Edit.objects.filter(author = request.user).order_by("created_at")
        edits = EditSerializer(edits,many = True).data
        response = {
            "user" : request.user.nickname,
            "edits" : edits
        }
        return Response(response)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
