from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Goals, assets, deviceDetails, CustomUser, Todo, MetaData, StockNames

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'email', 'password', 'username', 'last_login', 'guid']
        extra_kwargs ={
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class checkDataSerializer(serializers.Serializer):
    encodedData = serializers.CharField()
    # Checksum = serializers.CharField()

class deviceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = deviceDetails
        fields = ['device_name', 'device_id', 'user', 'last_login_at']
        
class todoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['todoName', 'todoDate', 'guid', 'isCompleted', 'user', 'insertAt', 'updateAt', 'isRegular']
        
class metaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaData
        fields = '__all__'

class stockNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockNames
        fields = '__all__'

class goalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goals
        fields = '__all__'

class assetSerializer(serializers.ModelSerializer):
    class Meta:
        model = assets
        fields = '__all__'