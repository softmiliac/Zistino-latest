"""
SMS Service for sending SMS notifications via MeliPayamak (priority) or Mizban SMS (fallback).
"""
import logging
import requests
import json
from django.conf import settings

logger = logging.getLogger(__name__)


def _normalize_phone_number(phone_number):
    """
    Normalize phone number to Iranian format (09123456789).
    
    Args:
        phone_number (str): Phone number in any format
        
    Returns:
        str: Normalized phone number (09123456789 format)
    """
    normalized = phone_number.strip()
    if normalized.startswith('+98'):
        normalized = '0' + normalized[3:]  # +989123456789 -> 09123456789
    elif normalized.startswith('98'):
        normalized = '0' + normalized[2:]  # 989123456789 -> 09123456789
    elif not normalized.startswith('0'):
        normalized = '0' + normalized  # 9123456789 -> 09123456789
    return normalized


def _send_sms_melipayamak(phone_number, message):
    """
    Send SMS via MeliPayamak REST API.
    
    MeliPayamak REST API endpoint: https://rest.payamak-panel.com/api/SendSMS/SendSMS
    This method is used for sending SMS to a maximum of 100 recipients per call.
    
    According to MeliPayamak documentation:
    - username: Your account username (phone number) in the system
    - password: API key from settings and web service in developer menu
    - to: Recipient number(s), separated by comma (،) for multiple recipients
    - from: Dedicated sender number
    - text: SMS text content
    - isFlash: Optional boolean to send as flash message
    
    Args:
        phone_number (str): Phone number to send SMS to
        message (str): Message content
        
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        username = settings.MELIPAYAMAK_USERNAME
        api_key = settings.MELIPAYAMAK_API_KEY  # API Key is used as password
        api_url = settings.MELIPAYAMAK_API_URL
        sender = settings.MELIPAYAMAK_SENDER
        
        if not username or not api_key:
            error_msg = "MeliPayamak credentials not configured. Please set MELIPAYAMAK_USERNAME and MELIPAYAMAK_API_KEY in settings."
            logger.error(error_msg)
            return False, error_msg
        
        if not sender:
            error_msg = "MeliPayamak sender number not configured. Please set MELIPAYAMAK_SENDER in settings."
            logger.error(error_msg)
            return False, error_msg
        
        # Normalize phone number
        normalized_phone = _normalize_phone_number(phone_number)
        
        # MeliPayamak REST API endpoint
        # Default: https://rest.payamak-panel.com/api/SendSMS/SendSMS
        send_endpoint = api_url if api_url else "https://rest.payamak-panel.com/api/SendSMS/SendSMS"
        
        # Prepare payload according to MeliPayamak REST API documentation
        # Note: The API accepts form-encoded data (application/x-www-form-urlencoded)
        payload = {
            'username': username,  # Phone number (e.g., 09155009664)
            'password': api_key,   # API Key (e.g., f2b89fd9-5633-4623-92c1-b3a896639f76)
            'to': normalized_phone,  # Recipient number (e.g., 09155309685)
            'from': sender,          # Sender number (e.g., 21700077)
            'text': message          # SMS text content
            # isFlash is optional, not included by default
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/plain, */*'
        }
        
        logger.info(f"Sending SMS via MeliPayamak REST API to {normalized_phone}")
        logger.info(f"Using endpoint: {send_endpoint}")
        logger.info(f"Username: {username}, Sender: {sender}")
        logger.debug(f"Payload: {payload}")
        
        # Send POST request with form-encoded data
        response = requests.post(
            send_endpoint,
            data=payload,  # Use 'data' for form-encoded
            headers=headers,
            timeout=30
        )
        
        logger.info(f"MeliPayamak API Response Status: {response.status_code}")
        logger.info(f"MeliPayamak API Response Text: {response.text[:500]}")
        
        # Store raw response for debugging
        raw_response_text = response.text
        
        if response.status_code == 200:
            response_text = response.text.strip()
            
            # MeliPayamak REST API typically returns:
            # - Success: Positive number (message ID) or JSON with status
            # - Error: Negative number, error message, or JSON with error
            
            # Try to parse as JSON first
            try:
                response_data = response.json()
                logger.info(f"MeliPayamak API Response JSON: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # Check for success indicators in JSON response
                if isinstance(response_data, dict):
                    # Common success fields
                    status = (
                        response_data.get('status') or
                        response_data.get('Status') or
                        response_data.get('RetStatus') or
                        response_data.get('StrRetStatus')
                    )
                    
                    # Check if status indicates success
                    if isinstance(status, (int, float)) and status > 0:
                        logger.info(f"SMS sent successfully via MeliPayamak to {normalized_phone}. Status: {status}")
                        return True, None
                    elif isinstance(status, str) and status.lower() in ['ok', 'success', 'true']:
                        logger.info(f"SMS sent successfully via MeliPayamak to {normalized_phone}")
                        return True, None
                    else:
                        error_msg = response_data.get('message') or response_data.get('Message') or str(response_data)
                        logger.error(f"MeliPayamak API returned error: {error_msg}")
                        return False, f"API Error: {error_msg}"
                else:
                    # If response is not a dict, treat as success if status is 200
                    logger.info(f"SMS sent successfully via MeliPayamak to {normalized_phone}")
                    return True, None
                    
            except (ValueError, json.JSONDecodeError):
                # Not JSON, treat as plain text
                # Success: positive number (message ID)
                # Error: negative number or error message
                if response_text.isdigit():
                    message_id = int(response_text)
                    if message_id > 0:
                        logger.info(f"SMS sent successfully via MeliPayamak to {normalized_phone}. Message ID: {message_id}")
                        return True, None
                    else:
                        logger.error(f"MeliPayamak API returned error code: {message_id}")
                        return False, f"API Error: {message_id}"
                elif 'ok' in response_text.lower() or response_text.lower() == 'success':
                    logger.info(f"SMS sent successfully via MeliPayamak to {normalized_phone}")
                    return True, None
                else:
                    logger.error(f"MeliPayamak API returned error: {response_text}")
                    return False, f"API Error: {response_text}"
        else:
            error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            logger.error(f"MeliPayamak API request failed: {error_msg}")
            return False, error_msg
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error: {str(e)}"
        logger.error(f"Network error while sending SMS via MeliPayamak: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Failed to send SMS via MeliPayamak: {error_msg}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False, error_msg


def _send_sms_mizban(phone_number, message):
    """
    Send SMS via Mizban SMS API.
    
    Args:
        phone_number (str): Phone number to send SMS to
        message (str): Message content
        
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        username = settings.MIZBAN_SMS_USERNAME
        password = settings.MIZBAN_SMS_PASSWORD
        api_url = settings.MIZBAN_SMS_API_URL
        sender = settings.MIZBAN_SMS_SENDER
        auth_token = settings.MIZBAN_SMS_AUTH_TOKEN
        
        # Normalize phone number
        normalized_phone = _normalize_phone_number(phone_number)
        
        # Prepare API request
        if api_url:
            send_endpoint = api_url.rstrip('/')
        else:
            send_endpoint = 'https://services.mizbansms.com/api/Message/SendMessage'
        
        # Mizban SMS API uses JSON format with specific structure
        from datetime import datetime
        
        payload = {
            'userType': 1,
            'sendSMSType': 1,
            'messageType': 1,
            'messages': [message],
            'mobiles': [normalized_phone],
            'subject': '',
            'sendDate': datetime.now().isoformat() + 'Z',
            'sendDateShamsi': 'آنی',
            'smsNumber': sender.strip() if sender and not sender.strip().startswith('#') else '',
            'smsNumberId': 2016 if sender and sender.strip() == '5000467254' else 0,
            'smsOperator': '',
            'timerSendSMSId': 0,
            'repeatCount': 0,
            'countRow': 0,
            'row': 0,
            'operatorId': 0,
            'provinceId': 0,
            'countyId': 0,
            'cityId': 0,
            'provinceName': '',
            'cityName': [],
            'zipCode': 0,
            'gender': None,
            'ageFrom': 0,
            'ageTo': 0,
            'isOrder': None,
            'informations': [],
            'mapInfo': []
        }
        
        if sender and not sender.strip().startswith('#'):
            sender_value = sender.strip()
            payload['smsNumber'] = sender_value
            logger.info(f"Using sender number: {sender_value}")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if auth_token:
            headers['Authorization'] = auth_token
            logger.info("Using authorization token for authentication")
        elif username and password:
            payload['username'] = username
            payload['password'] = password
            logger.warning("No authorization token - trying username/password in payload.")
        else:
            logger.error("No authentication credentials provided.")
        
        logger.info(f"Sending SMS via Mizban SMS API to {normalized_phone}")
        logger.info(f"Using endpoint: {send_endpoint}")
        
        response = requests.post(
            send_endpoint,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        logger.info(f"Mizban SMS API Response Status: {response.status_code}")
        logger.info(f"Mizban SMS API Response Text: {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                logger.info(f"Mizban SMS API Response JSON: {json.dumps(response_data, indent=2)}")
                
                if isinstance(response_data, dict):
                    status = (
                        response_data.get('status') or 
                        response_data.get('Status') or 
                        response_data.get('success') or
                        response_data.get('Success') or
                        response_data.get('isSuccess') or
                        response_data.get('IsSuccess') or
                        response_data.get('result') or
                        response_data.get('Result')
                    )
                    
                    is_success = False
                    if status in [1, '1', 'success', 'ok', 'OK', True, 'true', 'True']:
                        is_success = True
                    elif status is None or status == '' or status == {}:
                        is_success = True
                    elif isinstance(status, dict) and len(status) == 0:
                        is_success = True
                    
                    if is_success:
                        logger.info(f"SMS sent successfully via Mizban SMS to {normalized_phone}")
                        return True, None
                    else:
                        error_msg = (
                            response_data.get('message') or 
                            response_data.get('Message') or 
                            response_data.get('error') or
                            response_data.get('Error') or
                            response_data.get('errorMessage') or
                            response_data.get('ErrorMessage') or
                            str(response_data)
                        )
                        logger.error(f"Mizban SMS API returned error: {error_msg}")
                        return False, f"API Error: {error_msg}"
                elif isinstance(response_data, list):
                    logger.info(f"SMS sent successfully via Mizban SMS to {normalized_phone}")
                    return True, None
                else:
                    logger.info(f"SMS sent successfully via Mizban SMS to {normalized_phone}")
                    return True, None
            except ValueError:
                if response.status_code == 200:
                    logger.info(f"SMS sent successfully via Mizban SMS to {normalized_phone} (HTTP 200, non-JSON)")
                    return True, None
                else:
                    logger.error(f"Mizban SMS API returned unexpected response: {response.text}")
                    return False, f"Unexpected API response: {response.text}"
            except Exception as e:
                logger.error(f"Error parsing API response: {str(e)}")
                if response.status_code == 200:
                    logger.info(f"SMS sent successfully via Mizban SMS to {normalized_phone} (HTTP 200, parsing failed)")
                    return True, None
                return False, f"Error parsing response: {str(e)}"
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            logger.error(f"Mizban SMS API request failed: {error_msg}")
            return False, error_msg
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error: {str(e)}"
        logger.error(f"Network error while sending SMS via Mizban SMS: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Failed to send SMS via Mizban SMS: {error_msg}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False, error_msg


def send_sms(phone_number, message):
    """
    Send SMS to phone number using MeliPayamak (priority) or Mizban SMS (fallback).
    
    Priority order:
    1. MeliPayamak (if MELIPAYAMAK_USERNAME and MELIPAYAMAK_API_KEY are configured)
    2. Mizban SMS (if MIZBAN_SMS credentials are configured)
    3. Development mode (log to console only)
    
    Args:
        phone_number (str): Phone number to send SMS to (format: 09123456789 or +989123456789)
        message (str): Message content
        
    Returns:
        tuple: (success: bool, error_message: str or None)
               If success=True, error_message is None
               If success=False, error_message contains the error details
    """
    try:
        # Check MeliPayamak credentials first (priority provider)
        melipayamak_username = settings.MELIPAYAMAK_USERNAME
        melipayamak_api_key = settings.MELIPAYAMAK_API_KEY
        
        if melipayamak_username and melipayamak_api_key:
            logger.info("Using MeliPayamak SMS service (priority provider)")
            return _send_sms_melipayamak(phone_number, message)
        
        # Fallback to Mizban SMS
        mizban_username = settings.MIZBAN_SMS_USERNAME
        mizban_password = settings.MIZBAN_SMS_PASSWORD
        mizban_auth_token = settings.MIZBAN_SMS_AUTH_TOKEN
        
        if mizban_username and mizban_password:
            logger.info("Using Mizban SMS service (fallback provider)")
            return _send_sms_mizban(phone_number, message)
        elif mizban_auth_token:
            logger.info("Using Mizban SMS service with auth token (fallback provider)")
            return _send_sms_mizban(phone_number, message)
        
        # No SMS credentials configured - log to console (development mode)
        logger.warning("No SMS credentials configured. SMS will be logged only.")
        logger.info(f"[SMS] To: {phone_number}")
        logger.info(f"[SMS] Message: {message}")
        print(f"\n{'='*60}")
        print(f"[SMS NOTIFICATION - DEVELOPMENT MODE]")
        print(f"To: {phone_number}")
        print(f"Message: {message}")
        print(f"{'='*60}\n")
        return True, None
        
    except Exception as e:
        error_msg = f"Unexpected error in send_sms: {str(e)}"
        logger.error(f"Failed to send SMS to {phone_number}: {error_msg}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False, error_msg


def send_deposit_request_confirmation(phone_number, amount):
    """
    Send SMS confirmation when customer creates deposit request.
    
    Args:
        phone_number (str): Customer phone number
        amount (Decimal): Deposit amount
        
    Returns:
        bool: True if SMS was sent successfully
    """
    message = f"Your deposit request of {amount:,.0f} Rials has been registered. Please deposit the money and wait for verification."
    success, _ = send_sms(phone_number, message)
    return success


def send_deposit_confirmation(phone_number, amount, balance):
    """
    Send SMS confirmation when deposit is approved and money is added to wallet.
    
    Args:
        phone_number (str): Customer phone number
        amount (Decimal): Deposited amount
        balance (Decimal): New wallet balance
        
    Returns:
        bool: True if SMS was sent successfully
    """
    message = f"{amount:,.0f} Rials have been deposited into your account. Your current balance is {balance:,.0f} Rials."
    success, _ = send_sms(phone_number, message)
    return success


def send_deposit_rejection(phone_number, amount, reason=None):
    """
    Send SMS notification when deposit request is rejected.
    
    Args:
        phone_number (str): Customer phone number
        amount (Decimal): Requested deposit amount
        reason (str, optional): Reason for rejection
        
    Returns:
        bool: True if SMS was sent successfully
    """
    message = f"Your deposit request of {amount:,.0f} Rials has been rejected."
    if reason:
        message += f" Reason: {reason}"
    success, _ = send_sms(phone_number, message)
    return success


def send_delivery_reminder(phone_number, delivery_date, delivery_id=None):
    """
    Send SMS reminder 1 hour before delivery time period.
    
    Args:
        phone_number (str): Customer phone number
        delivery_date (datetime): Scheduled delivery date/time
        delivery_id (str, optional): Delivery ID for reference
        
    Returns:
        bool: True if SMS was sent successfully
    """
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Format delivery time period
    # Assume delivery_date is the start time, estimate end time as +2 hours
    delivery_start = delivery_date
    delivery_end = delivery_date + timedelta(hours=2)
    
    # Format times in Persian/Farsi style or simple format
    start_time = delivery_start.strftime('%H:%M')
    end_time = delivery_end.strftime('%H:%M')
    
    # Format date
    delivery_date_str = delivery_start.strftime('%Y/%m/%d')
    
    # Create message
    message = f"یادآوری: راننده در بازه زمانی {start_time} تا {end_time} امروز ({delivery_date_str}) به آدرس شما خواهد آمد. لطفا آماده باشید."
    # English version (optional): f"Reminder: Driver will arrive between {start_time} and {end_time} today ({delivery_date_str}). Please be ready."
    
    success, _ = send_sms(phone_number, message)
    return success


def add_melipayamak_pattern(title, body, black_list_id=1):
    """
    Add a pattern (template) to MeliPayamak using SharedServiceBodyAdd method.
    
    Patterns are pre-approved SMS templates that can be used to send messages.
    This is useful for:
    - Pre-approved message templates (required in some countries)
    - Consistent message formatting
    - Better deliverability
    
    Args:
        title (str): Pattern title/name (e.g., "Order Confirmation")
        body (str): Pattern body with variables (e.g., "Your order #{code} has been confirmed. Total: {amount} Rials")
                    Use {variable_name} format for variables
        black_list_id (int): Black list ID (default: 1 as per MeliPayamak documentation)
    
    Returns:
        tuple: (success: bool, pattern_id: int or None, error_message: str or None)
               If success=True: pattern_id contains the BodyId (5-6 digit number)
               If success=False: pattern_id is None and error_message contains the error
    
    Example:
        success, pattern_id, error = add_melipayamak_pattern(
            title="Order Confirmation",
            body="Your order #{order_id} has been confirmed. Total: {amount} Rials"
        )
        if success:
            print(f"Pattern registered with ID: {pattern_id}")
    """
    try:
        username = settings.MELIPAYAMAK_USERNAME
        api_key = settings.MELIPAYAMAK_API_KEY  # API Key is used as password
        
        if not username or not api_key:
            error_msg = "MeliPayamak credentials not configured. Please set MELIPAYAMAK_USERNAME and MELIPAYAMAK_API_KEY in settings."
            logger.error(error_msg)
            return False, None, error_msg
        
        # MeliPayamak SharedService SOAP endpoint
        # Using non-WSDL format: POST to method URL with form-encoded data
        endpoint = "https://api.payamak-panel.com/post/SharedService.asmx/SharedServiceBodyAdd"
        
        # Prepare payload
        payload = {
            'username': username,
            'password': api_key,  # API Key is used as password
            'title': title,
            'body': body,
            'blackListId': black_list_id
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/xml, application/xml, text/plain, */*'
        }
        
        logger.info(f"Adding MeliPayamak pattern: {title}")
        logger.info(f"Pattern body: {body}")
        
        # Send POST request
        response = requests.post(
            endpoint,
            data=payload,
            headers=headers,
            timeout=30
        )
        
        logger.info(f"MeliPayamak Pattern API Response Status: {response.status_code}")
        logger.info(f"MeliPayamak Pattern API Response Text: {response.text[:500]}")
        
        if response.status_code == 200:
            response_text = response.text.strip()
            
            # Parse response - can be XML or plain text
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response_text)
                # Look for SharedServiceBodyAddResult element
                result_elem = root.find('.//{http://tempuri.org/}SharedServiceBodyAddResult')
                if result_elem is not None:
                    result_text = result_elem.text.strip()
                else:
                    # Try without namespace
                    result_elem = root.find('.//SharedServiceBodyAddResult')
                    result_text = result_elem.text.strip() if result_elem is not None else response_text
            except ET.ParseError:
                # Not XML, treat as plain text
                result_text = response_text
            
            # Parse result
            # Success: positive number (5-6 digits) = BodyId
            # Error: -2 (invalid black list ID), 0 (wrong credentials), negative number
            try:
                result_value = int(result_text)
                
                if result_value > 0:
                    # Success - result_value is the BodyId (pattern ID)
                    logger.info(f"Pattern '{title}' registered successfully with BodyId: {result_value}")
                    return True, result_value, None
                elif result_value == -2:
                    error_msg = "Invalid black list ID. blackListId must be 1."
                    logger.error(f"MeliPayamak Pattern API error: {error_msg}")
                    return False, None, error_msg
                elif result_value == 0:
                    error_msg = "Invalid username or password (API key)."
                    logger.error(f"MeliPayamak Pattern API error: {error_msg}")
                    return False, None, error_msg
                else:
                    error_msg = f"API returned error code: {result_value}"
                    logger.error(f"MeliPayamak Pattern API error: {error_msg}")
                    return False, None, error_msg
            except ValueError:
                # Not a number, might be an error message
                error_msg = f"Unexpected API response: {result_text}"
                logger.error(f"MeliPayamak Pattern API error: {error_msg}")
                return False, None, error_msg
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            logger.error(f"MeliPayamak Pattern API request failed: {error_msg}")
            return False, None, error_msg
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error: {str(e)}"
        logger.error(f"Network error while adding MeliPayamak pattern: {error_msg}")
        return False, None, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Failed to add MeliPayamak pattern: {error_msg}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False, None, error_msg


def send_sms_with_pattern(phone_number, pattern_id, pattern_args):
    """
    Send SMS using a registered MeliPayamak pattern (template).
    
    This function uses MeliPayamak Smart webservice REST API to send SMS with pre-approved patterns.
    Patterns must be approved by MeliPayamak before they can be used.
    
    According to Smart webservice documentation:
    - REST API: https://rest.payamak-panel.com/api/SendSMS/SendByBaseNumber
    - Uses JSON payload with username, password, to, bodyId, and args array
    
    Args:
        phone_number (str): Phone number to send SMS to (format: 09123456789 or +989123456789)
        pattern_id (int): Pattern ID (BodyId) from MeliPayamak (e.g., 389656)
        pattern_args (list): List of values to replace pattern variables
                           Example: If pattern has {۰}, {۱}, {۲}, {۳}
                           Then pattern_args should be: ['value0', 'value1', 'value2', 'value3']
    
    Returns:
        tuple: (success: bool, error_message: str or None)
               If success=True, error_message is None
               If success=False, error_message contains the error details
    
    Example:
        # Pattern: "کاربر گرامی {۰} کد تایید شما {۱} می باشد. تاریخ {۲} در ساعت {۳}"
        # Pattern ID: 389656
        success, error = send_sms_with_pattern(
            phone_number="09123456789",
            pattern_id=389656,
            pattern_args=["علی احمدی", "12345", "1404/08/15", "14:30"]
        )
    """
    try:
        username = settings.MELIPAYAMAK_USERNAME
        api_key = settings.MELIPAYAMAK_API_KEY  # API Key is used as password
        
        if not username or not api_key:
            error_msg = "MeliPayamak credentials not configured. Please set MELIPAYAMAK_USERNAME and MELIPAYAMAK_API_KEY in settings."
            logger.error(error_msg)
            return False, error_msg
        
        # Normalize phone number
        normalized_phone = _normalize_phone_number(phone_number)
        
        # MeliPayamak Smart webservice REST API endpoint
        # According to Smart webservice documentation
        rest_endpoint = "https://rest.payamak-panel.com/api/SendSMS/SendByBaseNumber"
        
        # Prepare JSON payload for REST API
        # Smart webservice expects: username, password, to, bodyId, args (array)
        payload = {
            'username': username,
            'password': api_key,  # API Key is used as password
            'to': normalized_phone,
            'bodyId': pattern_id,
            'args': pattern_args  # Array of arguments (not comma-separated string)
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        logger.info(f"Sending SMS via MeliPayamak Smart webservice (REST API) to {normalized_phone}")
        logger.info(f"Pattern ID: {pattern_id}")
        logger.info(f"Pattern args: {pattern_args}")
        logger.info(f"Using endpoint: {rest_endpoint}")
        
        # Send REST API POST request with JSON payload
        response = requests.post(
            rest_endpoint,
            json=payload,  # Use json parameter for JSON payload
            headers=headers,
            timeout=30
        )
        
        logger.info(f"MeliPayamak Smart API Response Status: {response.status_code}")
        logger.info(f"MeliPayamak Smart API Response Text: {response.text[:500]}")
        
        if response.status_code == 200:
            # Parse JSON response
            try:
                response_data = response.json()
                logger.info(f"MeliPayamak Smart API Response JSON: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # Check response structure
                # Success responses typically have status/StrRetStatus or similar fields
                # Error responses may have error messages
                
                # Try to find status indicators
                status = None
                message_id = None
                error_message = None
                
                # Common response field names
                if isinstance(response_data, dict):
                    # Check for status field
                    status = (
                        response_data.get('StrRetStatus') or
                        response_data.get('status') or
                        response_data.get('Status') or
                        response_data.get('RetStatus') or
                        response_data.get('result')
                    )
                    
                    # Check for message ID
                    message_id = (
                        response_data.get('RetStatus') or
                        response_data.get('messageId') or
                        response_data.get('MessageId') or
                        response_data.get('id')
                    )
                    
                    # Check for error message
                    error_message = (
                        response_data.get('message') or
                        response_data.get('Message') or
                        response_data.get('error') or
                        response_data.get('Error')
                    )
                
                # Determine success
                is_success = False
                
                # If status is a positive number or "Ok"/"ok"
                if isinstance(status, (int, float)) and status > 0:
                    is_success = True
                elif isinstance(message_id, (int, float)) and message_id > 0:
                    is_success = True
                elif isinstance(status, str) and status.lower() in ['ok', 'success', 'true']:
                    is_success = True
                elif isinstance(response_data, dict) and 'RetStatus' in response_data:
                    # RetStatus > 0 means success
                    ret_status = response_data.get('RetStatus')
                    if isinstance(ret_status, (int, float)) and ret_status > 0:
                        is_success = True
                        message_id = ret_status
                
                if is_success:
                    logger.info(f"SMS sent successfully via MeliPayamak Smart pattern {pattern_id} to {normalized_phone}. Message ID: {message_id}")
                    return True, None
                else:
                    # Error case
                    error_msg = error_message or str(response_data) or "Unknown error from API"
                    logger.error(f"MeliPayamak Smart API returned error: {error_msg}")
                    return False, error_msg
                    
            except ValueError:
                # Response is not JSON, treat as plain text
                response_text = response.text.strip()
                
                # Check if it's a success (positive number)
                try:
                    result_value = int(response_text)
                    if result_value > 0:
                        logger.info(f"SMS sent successfully via MeliPayamak Smart pattern {pattern_id} to {normalized_phone}. Message ID: {result_value}")
                        return True, None
                    else:
                        error_msg = f"API returned error code: {result_value}"
                        logger.error(f"MeliPayamak Smart API error: {error_msg}")
                        return False, error_msg
                except ValueError:
                    # Not a number
                    if 'ok' in response_text.lower() or response_text.startswith('1'):
                        logger.info(f"SMS sent successfully via MeliPayamak Smart pattern {pattern_id} to {normalized_phone}")
                        return True, None
                    else:
                        error_msg = f"Unexpected API response: {response_text}"
                        logger.error(f"MeliPayamak Smart API error: {error_msg}")
                        return False, error_msg
        else:
            error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            logger.error(f"MeliPayamak Smart API request failed: {error_msg}")
            return False, error_msg
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error: {str(e)}"
        logger.error(f"Network error while sending SMS via MeliPayamak pattern: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Failed to send SMS via MeliPayamak pattern: {error_msg}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False, error_msg


def _send_sms_with_pattern_soap(phone_number, pattern_id, pattern_args, username, api_key, normalized_phone):
    """
    Alternative SOAP XML approach for sending SMS with pattern.
    This is used as a fallback when form-encoded POST fails.
    """
    try:
        # Convert pattern_args list to comma-separated string
        pattern_text = ','.join(str(arg) for arg in pattern_args)
        
        # Try different method names with SOAP XML
        method_names = ["SendByBaseNumber2", "SendByBaseNumber", "SendByBaseNumber3"]
        base_endpoint = "https://api.payamak-panel.com/post/SharedService.asmx"
        
        for method_name in method_names:
            # Escape XML special characters
            import html
            escaped_username = html.escape(str(username))
            escaped_password = html.escape(str(api_key))
            escaped_text = html.escape(str(pattern_text))
            escaped_to = html.escape(str(normalized_phone))
            
            # Create SOAP XML envelope
            soap_body = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <{method_name} xmlns="http://tempuri.org/">
      <username>{escaped_username}</username>
      <password>{escaped_password}</password>
      <text>{escaped_text}</text>
      <to>{escaped_to}</to>
      <bodyId>{pattern_id}</bodyId>
    </{method_name}>
  </soap:Body>
</soap:Envelope>'''
            
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': f'http://tempuri.org/{method_name}',
                'Accept': 'text/xml, application/xml'
            }
            
            logger.info(f"Trying SOAP XML method: {method_name}")
            
            response = requests.post(
                base_endpoint,
                data=soap_body.encode('utf-8'),
                headers=headers,
                timeout=30
            )
            
            logger.info(f"SOAP XML Response Status: {response.status_code}")
            logger.info(f"SOAP XML Response Text: {response.text[:500]}")
            
            if response.status_code == 200:
                if "method name is not valid" in response.text.lower():
                    continue
                
                # Parse SOAP response
                try:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(response.text)
                    result_elem = root.find(f'.//{{http://tempuri.org/}}{method_name}Result')
                    if result_elem is not None:
                        result_text = result_elem.text.strip()
                    else:
                        result_elem = root.find(f'.//{method_name}Result')
                        result_text = result_elem.text.strip() if result_elem is not None else response.text
                    
                    try:
                        result_value = int(result_text)
                        if result_value > 0:
                            logger.info(f"SMS sent successfully via SOAP XML pattern {pattern_id} to {normalized_phone}. Message ID: {result_value}")
                            return True, None
                        else:
                            continue  # Try next method
                    except ValueError:
                        if 'ok' in result_text.lower():
                            logger.info(f"SMS sent successfully via SOAP XML pattern {pattern_id} to {normalized_phone}")
                            return True, None
                        continue
                except ET.ParseError:
                    continue
        
        return False, "All SOAP XML methods failed. Please check MeliPayamak documentation for correct method name."
    except Exception as e:
        error_msg = f"SOAP XML error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def send_verification_code_pattern(phone_number, user_name, verification_code, date=None, time=None):
    """
    Send verification code SMS using the Zistino pattern (ID: 389656).
    
    Pattern: "کاربر گرامی {۰} کد تایید شما {۱} می باشد. تاریخ {۲} در ساعت {۳} www.zistino.com"
    Pattern ID: 389656
    
    Args:
        phone_number (str): Phone number to send SMS to
        user_name (str): User's name (replaces {۰})
        verification_code (str): Verification code (replaces {۱})
        date (str, optional): Date in format "1404/08/15" (replaces {۲}). If None, uses current date
        time (str, optional): Time in format "14:30" (replaces {۳}). If None, uses current time
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    
    Example:
        success, error = send_verification_code_pattern(
            phone_number="09123456789",
            user_name="علی احمدی",
            verification_code="12345"
        )
    """
    from datetime import datetime
    
    # Use current date/time if not provided
    if date is None:
        # Convert to Persian date format (you may need to adjust this based on your needs)
        # For now, using simple format
        now = datetime.now()
        date = now.strftime('%Y/%m/%d')
    
    if time is None:
        now = datetime.now()
        time = now.strftime('%H:%M')
    
    # Pattern variables: {۰}, {۱}, {۲}, {۳}
    pattern_args = [
        user_name,           # {۰} - User name
        verification_code,  # {۱} - Verification code
        date,               # {۲} - Date
        time                # {۳} - Time
    ]
    
    return send_sms_with_pattern(
        phone_number=phone_number,
        pattern_id=389656,  # Zistino verification code pattern ID
        pattern_args=pattern_args
    )