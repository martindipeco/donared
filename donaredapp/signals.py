# donaredapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

# Set up logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender='donaredapp.Profile')  # Listen to Profile model saves
def profile_created_handler(sender, instance, created, **kwargs):
    """
    Signal handler that sends email when a new profile is created
    and the user has requested validation (checked the validado checkbox)
    """
    if created and instance.validado:  # New profile created with validado=True
        send_validation_notification_email(instance.user, instance)


def send_validation_notification_email(user, profile):
    """
    Send email notification to admins when a user requests validation
    """
    try:
        # Get admin emails from settings
        admin_emails = getattr(settings, 'ADMIN_EMAILS', ['donareddonared@gmail.com'])
        
        # Skip if no admin emails configured
        if not admin_emails:
            logger.warning("No admin emails configured for validation notifications")
            return
        
        # Email subject
        subject = f'Nueva solicitud de validación - {user.username}'
        
        # Context for email template
        context = {
            'user': user,
            'profile': profile,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'movil': profile.movil if profile.movil else 'No proporcionado',
            'admin_url': f"{getattr(settings, 'SITE_URL', '')}/admin/donaredapp/profile/{profile.id}/change/"
        }
        
        # Render HTML email template
        html_message = render_to_string('donaredapp/emails/validacion_pedido.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Validation notification email sent for user: {user.username}")
        
    except Exception as e:
        logger.error(f"Error sending validation email for user {user.username}: {str(e)}")
