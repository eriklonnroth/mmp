from django.core.mail import send_mail
from django.conf import settings
import smtplib
from email.mime.text import MIMEText

# First, let's verify our email settings
print("Email settings:")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")

# Now let's try to connect to the SMTP server directly
try:
    print("\nTesting SMTP connection...")
    smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    smtp.set_debuglevel(1)  # This will show us the SMTP conversation
    print("Connected to SMTP server")
    
    print("Starting TLS...")
    smtp.starttls()
    print("TLS started")
    
    print("Attempting login...")
    smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    print("Login successful")
    
    print("\nAttempting to send test email...")
    try:
        result = send_mail(
            subject='Test Email from Django',
            message='If you see this, email sending is working!',
            from_email='Make My Meal Plan <erik@eriklonnroth.com>',
            recipient_list=['erik.lonnroth@gmail.com'],
            fail_silently=False,
        )
        print(f"send_mail returned: {result}")
    except Exception as e:
        print(f"Error sending mail: {str(e)}")
        print(f"Error type: {type(e)}")
    
    smtp.quit()
    
except Exception as e:
    print(f"Connection error: {str(e)}")
    print(f"Error type: {type(e)}")