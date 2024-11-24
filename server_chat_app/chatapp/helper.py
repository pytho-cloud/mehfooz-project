from django.utils import timezone
from datetime import timedelta
import random
from django.core.mail import send_mail
from .models import OTP

def sendEmailToNewRegistration(email):
    try:

        print(f"Attempting to send OTP to {email}")


        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

   
        expires_at = timezone.now() + timedelta(minutes=5)
        print(expires_at,"this is my exipres time")

        otp_record, created = OTP.objects.get_or_create(email=email)

        otp_record.otp = otp
        otp_record.expires_at = expires_at  
        otp_record.save()

        print(f"OTP generated and stored: {otp}")

        # Send OTP to the provided email
        send_mail(
            subject='New Registration OTP',
            message=f"Your OTP for new registration is: {otp}. It will expire in 5 minutes.",
            from_email='dhavalshelar2012@gmail.com', 
            recipient_list=[email],
            fail_silently=False,
        )

    
        print(f"OTP sent to {email}")

        return True
    except Exception as e:
        # Log error if any
        print(f"Error sending OTP to {email}: {str(e)}")
        return False
