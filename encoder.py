import hashlib
import base64
import json
from datetime import date, datetime as dateMode


def hashUsername(input_string):
    # Convert input string to bytes (UTF-8 encoding)
    input_bytes = input_string.encode('utf-8')
    
    # Calculate MD5 hash
    md5_hash = hashlib.md5(input_bytes)
    
    # Get hexadecimal representation of the hash
    md5_hex = md5_hash.hexdigest()
    
    return md5_hex


def hashPassword(password, username, iterations=7):
    # Concatenate password and username
    concatenated_string = password + username

    # Hash the concatenated string using SHA-256 multiple times
    hashed_result = concatenated_string.encode('utf-8')
    for _ in range(iterations):
        hashed_result = hashlib.sha256(hashed_result).digest()

    # Convert the final hashed result to hexadecimal representation
    hashed_password = hashlib.sha256(hashed_result).hexdigest()

    return hashed_password

def baseEncode(string_to_encode):
    json_data = json.dumps(string_to_encode)
    encoded_bytes = base64.b64encode(json_data.encode('utf-8'))
    encoded_string = encoded_bytes.decode('utf-8')
    
    return encoded_string

def DateTimeConvert(stringDate):
    date_obj = dateMode.strptime(stringDate, '%d-%m-%Y %H:%M')
    formatted_date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S.%f')

    return formatted_date_str