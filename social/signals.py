from django.db.models.signals import m2m_changed , post_delete
from django.dispatch import receiver
from .models import *
from django.core.mail import send_mail

@receiver(m2m_changed, sender=Post.likes.through)
def users_like_changed(sender, instance, **kwargs):
    instance.total_likes = instance.likes.count()
    instance.save()

@receiver(post_delete,sender=Post)
def users_like_changed(sender,instance,**kwargs):
    author=instance.author
    subject="deleted"
    message=f"its deleted(Id:{instance.id})"


    send_mail('subject', message, "hoorieh.darvishi77@gmail.com", ["hooridarvishi@gmail.com"],
          fail_silently=False)

@receiver(m2m_changed, sender=Post.saved_by.through)
def users_save_changed(sender, instance, **kwargs):
    instance.total_saves = instance.saved_by.count()
    instance.save()