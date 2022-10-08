from turtle import ondrag
from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification

# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.vendor_name

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # Update checkbox active de vendor
            orig = Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                }
                if self.is_approved == True:
                    # Enviar correo de notificacion si hay cambios en el chekboox
                    mail_subject = "Congratulation! Your account has been approved"
                    send_notification(mail_subject, mail_template, context)
                else:
                    # enviar notificacion si hay cambio en el checkboox
                    mail_subject = "We're sorry! You are not elegible for publishing your menu on our marketplace"
                    send_notification(mail_subject, mail_template, context)
        return super(Vendor, self).save(*args, **kwargs)