from django.db import models
from django.contrib.auth.models import User

# Extends Django's built-in User model with additional profile information.
# Each user gets exactly one profile thanks to the OneToOneField relationship.
class Profile(models.Model):
    AVAILABILITY_CHOICES = [
        ('weekdays', 'Entre semana'),
        ('weekends', 'Fines de semana'),
        ('any', 'Cualquier día'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name='Foto')
    bio = models.TextField(blank=True, verbose_name='Biografía')
    city = models.CharField(max_length=100, verbose_name='Ciudad')
    age = models.PositiveIntegerField(verbose_name='Edad')
    interests = models.CharField(max_length=200, blank=True, verbose_name='Intereses')
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='any', verbose_name='Disponibilidad')

    def __str__(self):
        return f'{self.user.username} - {self.city}'


# Represents a direct date proposal from one user to another.
# Kept in the codebase for reference but no longer exposed in the UI —
# the friend request system replaced this flow.
class DateRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    proposed_place = models.CharField(max_length=200)
    proposed_date = models.DateField()
    proposed_time = models.TimeField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} -> {self.receiver} | {self.status}'


# An open plan posted by a user for anyone nearby to discover and join.
# Uses is_active as a soft delete — cancelled outings stay in the database
# but are hidden from the public feed.
class Outing(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='outings')
    place = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField()
    city = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.creator.username} - {self.place} ({self.date})'


# Tracks which users have expressed interest in a given outing.
# The unique_together constraint prevents a user from registering
# interest in the same outing more than once.
class Interest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interests')
    outing = models.ForeignKey(Outing, on_delete=models.CASCADE, related_name='interests')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'outing')

    def __str__(self):
        return f'{self.user.username} interesado en {self.outing}'


# In-app notification system. The optional sender field allows
# notifications to link back to the user who triggered them,
# enabling clickable notifications that lead to a profile.
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.message}'


# Stores private messages between two users.
# The optional outing field allows messages to be linked to a specific
# outing context, though it's not required for a conversation to exist.
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    outing = models.ForeignKey(Outing, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username} -> {self.receiver.username}'


# Manages friendship connections between users.
# unique_together ensures a user can only send one request to another user.
# Once accepted, both users can see each other in their friends list.
class Friendship(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptada'),
        ('rejected', 'Rechazada'),
    ]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friendships')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friendships')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f'{self.sender.username} -> {self.receiver.username} | {self.status}'