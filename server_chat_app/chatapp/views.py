# myapp/views.py
import random
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import LoginSerializer ,RegisterSerializer ,VerifyOTPSerializer
from rest_framework.views import APIView
from .models import User ,OTP
from .helper import sendEmailToNewRegistration
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OTP
from .serializers import VerifyOTPSerializer
from django.utils import timezone
from rest_framework.generics import GenericAPIView
from .models import AnonymousUser


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Send a response indicating that the user should verify OTP if not verified
        if not user.is_verified:
            return Response({'message': 'User not verified. Please verify your OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Login successful', 'user_id': user.id}, status=status.HTTP_200_OK)





class RegisterView(APIView):
    def post(self, request):
        print(request.data)
        register_serializer = RegisterSerializer(data=request.data)

        if register_serializer.is_valid():
            print("Serializer is valid")
            
            email = register_serializer.validated_data['email']
            password = register_serializer.validated_data['password']
            print(f"Password: {password}")

            # Generate and send OTP
            otp_generation = sendEmailToNewRegistration(email)

            if otp_generation is not True:
                return Response({"error": "OTP could not be sent"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Check if user already exists
            if User.objects.filter(email=email).exists():
                return Response(register_serializer.validated_data, status=status.HTTP_200_OK)

            # Hash password before saving
           
            
            # Create the user
            user = User.objects.create(email=email, password=password)
            user.save()

            return Response(register_serializer.validated_data, status=status.HTTP_200_OK)

        return Response(register_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyOTPView(APIView):
    def post(self, request):
        data = request.data
        print("++++++++++")

        email = data.get('email')
        otp = data.get('otp')
        
  
        verified_serializer = VerifyOTPSerializer(data=data)

        if verified_serializer.is_valid():
            
            try:
                otp_record = OTP.objects.get(email=email)

          
                if otp_record.otp == otp:
                    if timezone.now() > otp_record.expires_at:
                    
                        return Response({"message": "OTP has expired. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        user = User.objects.get(email= otp_record.email)
                        user.is_verified = True 
                        user.save()
                        
                        return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
                else:
                  
                    return Response({"message": "Invalid OTP. Please try again."}, status=status.HTTP_400_BAD_REQUEST)

            except OTP.DoesNotExist:
              
                return Response({"message": "OTP record not found. Please request a new OTP."}, status=status.HTTP_404_NOT_FOUND)


        return Response(verified_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OnlineUserView(APIView):
    def post(self, request):
        data = request.data
        print(data, "Received data")  
        email = data.get('email')
        camera_id = data.get('cameraId')

        print("Email:", email, "Camera ID:", camera_id)

        if not email or camera_id is None:
            return Response(
                {"message": "Email and camera ID are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
       
            user = User.objects.get(email=email)

           
            if not user.is_permission:
                print("Permission check failed")
                return Response(
                    {"message": "You are banned from using the camera."},
                    status=status.HTTP_403_FORBIDDEN 
                )

           
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
        email = data.get('email')
        camera_id = data.get('camera_id')
    
     
        try:

            if email and camera_id :
                print("this is my data bhaifffffffffffffffd")
                user = User.objects.get(email=email)
                
                user.is_permission = False
                user.save()
            if not email and camera_id :
                print("this is my data bhai")
                user = AnonymousUser.objects.get(camera_id=camera_id)
                user.is_permission = False
                user.save()

            return Response({"message": "Banned successfully", 'status': status.HTTP_200_OK})

        except User.DoesNotExist:
            return Response({"message": "User not found", 'status': status.HTTP_404_NOT_FOUND})
        except Exception as e:
            return Response({"message": str(e), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR})
        



        
class ForgetPasswordView(APIView):
    def post(self, request):
        data = request.data
        print(data, "this is my data")
        email = data.get('email')
        
   
        email_exist = User.objects.filter(email=email).first()
        print(email_exist, "-------------------")
        if not email_exist:
            print('this is true false')
            return Response({"message": "Email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Generate OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        print(otp, "OTP is generated")

     
        send_mail(
            subject='Password Reset OTP',
            message=f"Your OTP for renewing the password is: {otp}",
            from_email='dhavalshelar2012gmail.com',
            recipient_list=[email],  
            fail_silently=False,
        )

        
        request.session['reset_otp'] = otp
        request.session['reset_email'] = email

        return Response({"message": "OTP sent successfully!"}, status=status.HTTP_200_OK)
    



class AnonymousUserLogin(APIView):

    def post(self, request):
        data = request.data
        print(data, "Received data")
        
        camera_id = data.get('cameraId')
        
        if not camera_id:
            return Response({
                'message': 'cameraId is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
          
            AUser = AnonymousUser.objects.get(camera_id=camera_id)


            if AUser.is_permission:
                return Response({
                    'message': "User exists and permission is valid." ,
                     'status': 200
                }, status=status.HTTP_200_OK)
            else:
         
                return Response({
                    'message': "You are banned from using the camera.",
                    'status': 403
                }, status=status.HTTP_403_FORBIDDEN)

        except AnonymousUser.DoesNotExist:
           
            AUser = AnonymousUser.objects.create(
                camera_id=camera_id,
                is_permission=True  
            )
            return Response({
                'message': "New user created with permission." ,
                'status': 200
            }, status=status.HTTP_201_CREATED)
