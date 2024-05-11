from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import BotService
from .credentials import BOT_SETWEBHOOK_URL, BOT_URL
import requests
import json


class Hook(APIView):
    def post(self, request, format=None):
        update = json.loads(request.body)
        user_service = BotService(update)
        success, message = user_service.process_telegram_update()
        print(message)
        if success:
            return Response({'message': "message"}, status=status.HTTP_200_OK)
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)


class SetWebHook(APIView):
    def get(self, request, *args, **kwargs):
        response = requests.get(BOT_SETWEBHOOK_URL)
        if response.status_code == 200:
            return Response({'message': response.json()}, status=status.HTTP_200_OK)
        return Response({'error': response.json()}, status=status.HTTP_400_BAD_REQUEST)
