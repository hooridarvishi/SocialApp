from django.urls import reverse
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from taggit.managers import TaggableManager
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
# Create your models here.


class User(AbstractUser):
    date_of_birth = models.DateField(verbose_name="تاریخ تولد ", blank=True, null=True)
    bio = models.TextField(verbose_name=" بیوگرافی ", blank=True, null=True)
    photo = models.ImageField(upload_to="profile_image/", blank=True, null=True)
    job = models.CharField(max_length=120, verbose_name=" شغل ", blank=True, null=True)
    phone=models.CharField(max_length=11)
    following=models.ManyToManyField("self" , through='Contact' , related_name="followers" , symmetrical=False)
    # def get_absolute_url(self):
    #     return reverse("social:user_detail" , args=[self.usename])
    def get_followers(self):
        return [contact.user_from for contact in self.rel_to_set.all().order_by('-created')]

    def get_followings(self):
        return [contact.user_to for contact in self.rel_from_set.all().order_by('-created')]


# following =>خودش به خودش وصل شد چون خواستیم جدول میانی بسازیم
# through=>برای جدول میانی ست
# قبلا از جدول واسط دیفالت استفاده می کرد
# برای منی تو منی ، جنگو جدول میانی دیفالت میسازه اما
# خودمان مثل اینجا میتونیم پیش فرضش رو بسازیم
# symmetrical=>یعنی رابطه متقارن باشه
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_posts", verbose_name="نویسنده")
    tags=TaggableManager()
    description = models.TextField(verbose_name="توضیحات")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    likes=models.ManyToManyField(User,related_name="liked_posts" , blank=True)
    saved_by=models.ManyToManyField(User,related_name="saved_posts")
    total_liks=models.PositiveIntegerField(default=0)
    # PositiveIntegerField فقط مثبت ها رو نمایش بده
    title=models.CharField(default="",max_length=12 )

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=["total_liks"])
        ]
        verbose_name = "پست"
        verbose_name_plural = "پست ها"

    def __str__(self):
        return self.author.username

    def get_absolute_url(self):
        return reverse('social:post_detail', args=[self.id])


class Contact(models.Model):
    user_from = models.ForeignKey(User, related_name='rel_from_set', on_delete=models.CASCADE)
    # user_from می خواد کسی رو فالو کنه

    user_to = models.ForeignKey(User, related_name='rel_to_set', on_delete=models.CASCADE)
    # user_to کسی که فالو شده
    created = models.DateTimeField(auto_now_add=True)

    # created زمان فالو شدن
    class Meta:
        indexes = [
            models.Index(fields=['-created'])
        ]
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user_from} follows {self.user_to}"


class Comment(models.Model):
    post=models.ForeignKey(Post,related_name="comment" ,max_length=13,verbose_name="پست",on_delete=models.CASCADE)
    massage=models.TextField(max_length=170)
    name = models.CharField(max_length=170)



class Image(models.Model):
    post=models.ForeignKey(Post,related_name="images",on_delete=models.CASCADE)
    desc=models.CharField(max_length=12)
    image_file=models.ImageField(upload_to="posts")

class Ticket(models.Model):
    name=models.CharField(max_length=12 , default="" , null=True , blank=True)
    email=models.EmailField(max_length=32 , default="" , null=True , blank=True)
    phone=models.CharField(max_length=19 , null=True , blank=True)
    message=models.CharField(max_length=14 , default="" , null=True , blank=True)
    respond_ticket=models.CharField(max_length=20 , default="" , null=True , blank=True)





















