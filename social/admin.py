from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
# Register your models here.
@admin.register(User)
class UserAdmin(UserAdmin):
    list_display=["first_name","last_name","username","phone"]
    list_display_links = ['username']
    fieldsets=UserAdmin.fieldsets + (
        ("additional information",{"fields":("date_of_birth","bio","photo","job","phone")}),
    )

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'created', 'title']
    ordering = [ 'created']
    search_fields = [ 'description']


admin.site.register(Contact)

@admin.register(Comment)
class PostAdmin(admin.ModelAdmin):
    list_display =["post","massage","name"]



