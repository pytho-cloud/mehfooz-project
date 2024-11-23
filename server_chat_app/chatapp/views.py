# myapp/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import LoginSerializer ,RegisterSerializer
from rest_framework.views import APIView
from .models import User
class LoginView(generics.GenericAPIView):
    
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        print("this is workiing")

        return Response({'message': 'Login successful', 'user_id': user.id}, status=status.HTTP_200_OK)




class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class OnlineUserView(APIView):
    def post(self, request):
        data = request.data
        print(data, "Received data")  # Log the incoming data
        email = data.get('email')
        camera_id = data.get('cameraId')

        print("Email:", email, "Camera ID:", camera_id)

        if not email or camera_id is None:
            return Response(
                {"message": "Email and camera ID are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch user based on email
            user = User.objects.get(email=email)

            # Check if the user has permission
            if not user.is_permission:
                print("Permission check failed")
                return Response(
                    {"message": "You are banned from using the camera."},
                    status=status.HTTP_403_FORBIDDEN  # Forbidden because the user is banned
                )

            # If the user is not banned, set their camera ID
            user.camera_id = camera_id
            user.save()

            return Response(
                {"message": "Access granted", "status": "success"},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"message": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(str(e))
            return Response(
                {"message": "Internal server error.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserBannedView(APIView):

    def post(self, request):
        data = request.data
        email = data.get('user')
        camera_id = data.get('camera')
        print("this is my data ==============" , email , camera_id)
        if not email or not camera_id:
            return Response({"message": "Email and camera ID are required.", 'status': status.HTTP_400_BAD_REQUEST})

        try:
            user = User.objects.get(email=email)
            user.camera_id = camera_id 
            user.save()

            return Response({"message": "Banned successfully", 'status': status.HTTP_200_OK})

        except User.DoesNotExist:
            return Response({"message": "User not found", 'status': status.HTTP_404_NOT_FOUND})
        except Exception as e:
            return Response({"message": str(e), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})
