from rest_framework import generics, status
from django.contrib.auth.models import User

from ..models import deviceDetails, CustomUser, assets
from ..serializers import checkDataSerializer,metaDataSerializer,assetSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from decoder import decode_data, verify_checksum, decode_jwt_token
import json
from django.contrib.auth import authenticate
import jwt, datetime
from django.utils import timezone
from django.db import transaction
from encoder import *
from rest_framework.exceptions import AuthenticationFailed
from datetime import date, datetime as dateMode
from django.db.models import Sum, Case, When, F, FloatField

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
                
                asset = {}
                asset['asset_name'] = decodedData['name']
                asset['asset_amnt'] = decodedData['amount']
                asset['user'] = user.id                

                asset['purchased_on'] = DateTimeConvert(decodedData['purchased'])
                if decodedData['validity']:
                    asset['valid_on'] = DateTimeConvert(decodedData['validity'])

                metadaSerializer = metaDataSerializer(data = metada)
                try:
                    if metadaSerializer.is_valid():
                        with transaction.atomic():
                            metaInstance = metadaSerializer.save()
                            asset['insertAt'] = metaInstance.id
                            asset_serializer = assetSerializer(data = asset)
                            if asset_serializer.is_valid():
                                asset_serializer.save()
                                return Response({'message': 'Item Added.'}, status=status.HTTP_200_OK)
                            else:
                                metaInstance.delete()
                                return Response(asset_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(metadaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                raise AuthenticationFailed('Invalid username')
        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def update(request):
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
        guid = decodedData['guid']
        objId = payload['id']
        try:
            user = CustomUser.objects.get(guid=objId)
            if user is not None:
                deviceData = deviceDetails.objects.filter(user=user).order_by('last_login_at').first()
                metada = {}
                metada['user'] = user.id
                metada['deviceName'] = deviceData.device_name
                metada['dateTime'] = timezone.now()              

                metadaSerializer = metaDataSerializer(data = metada)
                try:
                    if metadaSerializer.is_valid():
                        with transaction.atomic():
                            metaInstance = metadaSerializer.save()
                            assets.objects.filter(guid=guid).update(
                                valid_on=timezone.now(),
                                updateAt=metaInstance.id
                            )
                            return Response({'message': 'Item Updated.'}, status=status.HTTP_200_OK)
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
                assetObj = assets.objects.filter(user=user).order_by('-id')
                assetsData = [{
                    'guid': str(asset['guid']), 
                    'asset_name': asset['asset_name'], 
                    'asset_amount': asset['asset_amnt'], 
                    'validity': asset['valid_on'].isoformat() if isinstance(asset['valid_on'], dateMode) else None
                } for asset in assetObj.values()]

                data = {
                    'data': assetsData,
                }
                encodedData = baseEncode(data)
                
                return Response({'data': encodedData}, status=200)
            else:
                raise AuthenticationFailed('Invalid username')
        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        
@api_view(['POST'])
def amnt(request):
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
                # 1. Sum of all asset amounts
                total_amount = assets.objects.filter(user=user).aggregate(total=Sum('asset_amnt',output_field=FloatField()))

                # 2. Sum of asset amounts where validity is NULL
                amount_if_validity_null = assets.objects.filter(user=user).aggregate(
                    total_null=Sum(Case(
                        When(valid_on__isnull=True, then=F('asset_amnt')),
                        default=0,
                        output_field=FloatField()
                    ))
                )

                # 3. Sum of asset amounts where validity is NOT NULL
                amount_if_validity_not_null = assets.objects.filter(user=user).aggregate(
                    total_not_null=Sum(Case(
                        When(valid_on__isnull=False, then=F('asset_amnt')),
                        default=0,
                        output_field=FloatField()
                    ))
                )
                assetsData = [{
                    'totalAmnt': total_amount['total'], 
                    'ongoing': amount_if_validity_null['total_null'], 
                    'expired': amount_if_validity_not_null['total_not_null'], 
                }]

                data = {
                    'data': assetsData,
                }
                encodedData = baseEncode(data)
                
                return Response({'data': encodedData}, status=200)
            else:
                raise AuthenticationFailed('Invalid username')
        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)