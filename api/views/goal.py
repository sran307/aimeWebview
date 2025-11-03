from rest_framework import generics, status
from django.contrib.auth.models import User

from ..models import Goals, deviceDetails, CustomUser, Todo
from ..serializers import checkDataSerializer,metaDataSerializer,goalSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from decoder import decode_data, verify_checksum, decode_jwt_token
import json
from django.contrib.auth import authenticate
import jwt, datetime
from django.utils import timezone
from django.db import transaction
from encoder import hashUsername, hashPassword, baseEncode
from rest_framework.exceptions import AuthenticationFailed
from datetime import date, datetime as dateMode

@api_view(['POST'])
def save(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON data'}, status=400)
    
    serializer = checkDataSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    base64_encoded_data = serializer.validated_data.get('encodedData')
    decodedData = decode_data(base64_encoded_data)
    token = decodedData['token']
    payload = decode_jwt_token(token, 'secret')
    if payload == 400:
        return Response({
            'error':'Token expired'
            }, status=400)
    elif payload == 405:
        return Response({
            'error': 'Invalid Token'
        }, status=400)
    else:
        objId = payload['id']
        try:
            user = CustomUser.objects.get(guid=objId)
            if user is not None:
                deviceData = deviceDetails.objects.filter(user=user).order_by('last_login_at').first()
                metada = {}
                metada['user'] = user.id
                metada['deviceName'] = deviceData.device_name
                metada['dateTime'] = timezone.now()
                
                goal = {}
                goal['goal_name'] = decodedData['name']
                goal['goal_amnt'] = decodedData['amount']
                goal['user'] = user.id

                metadaSerializer = metaDataSerializer(data = metada)
                try:
                    if metadaSerializer.is_valid():
                        with transaction.atomic():
                            metaInstance = metadaSerializer.save()
                            goal['insertAt'] = metaInstance.id
                            goal_serializer = goalSerializer(data = goal)
                            if goal_serializer.is_valid():
                                goal_serializer.save()
                                return Response({'message': 'Item Added.'}, status=status.HTTP_200_OK)
                            else:
                                metaInstance.delete()
                                return Response(goal_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(metadaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                raise AuthenticationFailed('Invalid username')
        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def list(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON data'}, status=400)
    
    serializer = checkDataSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    base64_encoded_data = serializer.validated_data.get('encodedData')
    decodedData = decode_data(base64_encoded_data)
    token = decodedData['token']
    payload = decode_jwt_token(token, 'secret')
    if payload == 400:
        return Response({
            'error':'Token expired'
            }, status=400)
    elif payload == 405:
        return Response({
            'error': 'Invalid Token'
        }, status=400)
    else:
        objId = payload['id']
        try:
            user = CustomUser.objects.get(guid=objId)
            if user is not None:
                current_date = timezone.now().date()
                goalsPend = Goals.objects.filter(user=user, isAchieved=False)
                goalsComp = Goals.objects.filter(user=user, isAchieved=True)
                print(goalsPend)
                goals_pending = [{'guid': str(goals['guid']), 'goal_name': goals['goal_name'], 'goal_amount': goals['goal_amnt']} for goals in goalsPend.values()]
                goals_completed = [{'guid': str(goals['guid']), 'goal_name': goals['goal_name'], 'goal_amount': goals['goal_amnt']} for goals in goalsComp.values()]

                data = {
                    'goalPend': goals_pending,
                    'goalComp': goals_completed,
                }
                encodedData = baseEncode(data)
                
                return Response({'data': encodedData}, status=200)
            else:
                raise AuthenticationFailed('Invalid username')
        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)