from rest_framework import generics, status
from django.contrib.auth.models import User

from ..models import deviceDetails, CustomUser, Todo
from ..serializers import checkDataSerializer,UserSerializer, deviceDetailsSerializer, todoSerializer,metaDataSerializer

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
# class Usercreate(generics.ListCreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

# class AuthView(generics.GenericAPIView):
#     def deviceExist(self, request):
#         print(request)

@api_view(['POST'])
def checkDeviceExist(request):
    try:
        device_data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON data'}, status=400)
    
    serializer = checkDataSerializer(data=device_data)
    if serializer.is_valid():
        base64_encoded_data = serializer.validated_data.get('encodedData')
        
        decodedData = decode_data(base64_encoded_data)
        deviceName = decodedData['deviceName']
        deviceId = decodedData['deviceId']
        try:
            isExist = deviceDetails.objects.filter(device_name = deviceName, device_id = deviceId).count()
            if(isExist > 0):
                return Response({
                    'status': 200,
                    'isExist': True
                })
            else:
                return Response({
                    'status': 400,
                    'isExist': False
                })
        except deviceDetails.DoesNotExist:
            return Response({
                'status': 400, 
                'isExist' : False,
                'isException': True
                })
    else:
        return Response({
                'status': 400, 
                'isExist' : False,
                'isException': True
                })
    
@api_view(['POST'])
def registerUser(request):
    try:
        device_data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON data'}, status=400)
    
    serializer = checkDataSerializer(data=device_data) 
    if serializer.is_valid():
        base64_encoded_data = serializer.validated_data.get('encodedData')
        decoded_data = decode_data(base64_encoded_data)

        pin = decoded_data.get('username')
        username = hashUsername(decoded_data.get('username'))
        password = hashPassword(decoded_data.get('password'), decoded_data.get('username'))
        user_data = {
            'first_name': decoded_data.get('first_name'),
            'email': decoded_data.get('email'),
            'password': password,
            'username': username,
            'last_login':timezone.now()
        }

        device_data = {
            'device_name': decoded_data['deviceDetails']['deviceName'],
            'device_id': decoded_data['deviceDetails']['deviceId']
        }
        # Validate and save user data
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            try:
                with transaction.atomic():  # Use transaction to ensure atomicity
                    user_instance = user_serializer.save()
                    device_data['user'] = user_instance.id 
                    device_data['last_login_at']= timezone.now()
                    device_serializer = deviceDetailsSerializer(data=device_data)
                    # return Response(device_data, status=status.HTTP_400_BAD_REQUEST)
                    if device_serializer.is_valid():
                        device_serializer.save()
                        return Response({'pin': pin}, status=status.HTTP_201_CREATED)
                    else:
                        user_instance.delete()  # Rollback user creation if device creation fails
                        return Response(device_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def loginUser(request):
    try:
        device_data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON data'}, status=400)
    
    serializer = checkDataSerializer(data=device_data)
    serializer.is_valid(raise_exception=True)
    
    base64_encoded_data = serializer.validated_data.get('encodedData')
    decoded_data = decode_data(base64_encoded_data)
    
    pin = decoded_data['pin']
    username = hashUsername(pin)
    password = hashPassword(pin, pin)
    
    try:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            payload = {
                'id': str(user.guid),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                'iat': datetime.datetime.utcnow()
            }
            token = jwt.encode(payload, 'secret', algorithm='HS256')
            return Response({'status': 200, 'token': token}, status=status.HTTP_200_OK)
        else:
            raise AuthenticationFailed('Invalid username or password')
    except AuthenticationFailed as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def todoInsert(request):
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
                todo = {}
                dateIns = decodedData['date']
                date_obj = dateMode.strptime(dateIns, '%d-%m-%Y %H:%M')
                formatted_date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                todo['todoName'] = decodedData['name']
                todo['todoDate'] = formatted_date_str
                if decodedData['option'] == 'Regular':
                    option =  True
                else:
                    option = False
                todo['isRegular'] = option
                todo['user'] = user.id
                metadaSerializer = metaDataSerializer(data = metada)
                try:
                    if metadaSerializer.is_valid():
                        with transaction.atomic():
                            metaInstance = metadaSerializer.save()
                            todo['insertAt'] = metaInstance.id
                            todo_serializer = todoSerializer(data = todo)
                            if todo_serializer.is_valid():
                                todo_serializer.save()
                                return Response({'message': 'Item Added.'}, status=status.HTTP_200_OK)
                            else:
                                metaInstance.delete()
                                return Response(todo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(metadaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                raise AuthenticationFailed('Invalid username')
        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def todoList(request):
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
                todoToday = Todo.objects.filter(user=user, todoDate__date=current_date, isCompleted=False)
                todoYesterday = Todo.objects.filter(user=user, todoDate__date__lt=current_date, isCompleted=False)
                todoTomorrow = Todo.objects.filter(user=user, todoDate__date__gt=current_date, isCompleted=False)

                todo_today_list = [{'guid': str(todo['guid']), 'todoName': todo['todoName']} for todo in todoToday.values()]
                todo_yesterday_list = [{'guid': str(todo['guid']), 'todoName': todo['todoName']} for todo in todoYesterday.values()]
                todo_tomorrow_list = [{'guid': str(todo['guid']), 'todoName': todo['todoName']} for todo in todoTomorrow.values()]

                data = {
                    'todoToday': todo_today_list,
                    'todoYesterday': todo_yesterday_list,
                    'todoTomorrow': todo_tomorrow_list
                }
                encodedData = baseEncode(data)
                
                return Response({'data': encodedData}, status=200)
            else:
                raise AuthenticationFailed('Invalid username')
        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def todoUpdate(request):
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
                metadaSerializer = metaDataSerializer(data = metada)
                try:
                    if metadaSerializer.is_valid():
                        with transaction.atomic():
                            metaInstance = metadaSerializer.save()
                           
                            Todo.objects.filter(guid=decodedData['guId']).update(isCompleted=True, updateAt = metaInstance.id)                            
                            return Response({'message': 'Status Updated.'}, status=status.HTTP_200_OK)
                    else:
                        return Response(metadaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                raise AuthenticationFailed('Invalid username')
        except Todo.DoesNotExist:
            return Response({'error': 'Error Occured'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)