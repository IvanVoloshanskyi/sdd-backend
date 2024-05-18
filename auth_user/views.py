from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        data = request.data
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone_number = data.get('phone_number')
        address = data.get('address')

        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)

        if not email:
            return JsonResponse({'error': 'Email are required'}, status=400)

        if not phone_number:
            return JsonResponse({'error': 'Phone number is required'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        if User.objects.filter(phone_number=phone_number).exists():
            return JsonResponse({'error': 'Phone number already exists'}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone_number=phone_number,
            address=address
        )

        return JsonResponse({'success': 'User registered successfully'}, status=201)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        data = request.data
        username = data.get('username')
        password = data.get('password')

        if not username:
            return JsonResponse({'error': 'Username is required'}, status=400)

        if not password:
            return JsonResponse({'error': 'Password is required'}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'success': 'User logged in successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
