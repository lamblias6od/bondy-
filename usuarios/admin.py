from django.contrib import admin
from .models import Profile, DateRequest, Outing, Interest, Notification, Message, Friendship

# Register all models to make them accessible from the Django admin panel.
# Useful for managing data and debugging during development.
admin.site.register(Profile)
admin.site.register(DateRequest)
admin.site.register(Outing)
admin.site.register(Interest)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(Friendship)