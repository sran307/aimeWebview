import base64
import json
import hashlib
import jwt, datetime

def decode_data(encoded_data):
    # Decode base64 data
    decoded_bytes = base64.b64decode(encoded_data)
    decoded_str = decoded_bytes.decode('utf-8')
    
    # Parse JSON
    decoded_data = json.loads(decoded_str)
    
    return decoded_data

def verify_checksum(json_data, received_checksum):
    # Generate checksum from received data
    # calculated_checksum = hashlib.md5(json.dumps(data).encode()).hexdigest()
    # return calculated_checksum
    # Compare checksums
    # if calculated_checksum == received_checksum:
    #     return True
    # else:
    #     return False
    
    # Convert the JSON data to bytes
    # json_bytes = json_data.encode('utf-8')
    
    # Compute the MD5 hash
    # md5_hash = hashlib.md5(json_data)
    # return 'hyyy'
    # Return the hexadecimal representation of the hash digest
    # return md5_hash.hexdigest()


    # Convert the JSON data to a string
    json_data = '{"name":"Ubuntu","version":"22.04.1 LTS (Jammy Jellyfish)","id":"ubuntu","idLike":["debian"],"versionCodename":"jammy","versionId":"22.04","prettyName":"Ubuntu 22.04.1 LTS","buildId":null,"variant":null,"variantId":null,"machineId":"40b635c8dc724ae8a3ac8e9998bacda6"}'
    # json_string = json.dumps(json_data)
    
    # Convert the string to bytes using UTF-8 encoding

    # json_bytes = json_string.encode('utf-8')
    
    # Compute the MD5 hash
    # md5_hash = hashlib.md5(json_data)
    # return md5_hash.hexdigest()
    
    # Return the hexadecimal representation of the hash digest
    # return md5_hash.hexdigest()

    json_string = json.dumps(json_data)

    # Compute SHA-256 hash
    sha256_hash = hashlib.sha256(json_data.encode())
    return sha256_hash


def decode_jwt_token(token, secret_key):
    try:
        # Decode the JWT token
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        # Return decoded token data
        return decoded_token
    except jwt.ExpiredSignatureError:
        return 400
    except jwt.InvalidTokenError:
        return 405