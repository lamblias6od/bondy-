from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .forms import ProfileForm, OutingForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Profile, Outing, Interest, Notification, Message, Friendship


# Redirect to outings feed if already logged in, otherwise go to login page.
def home(request):
    if request.user.is_authenticated:
        return redirect('outings_list')
    return redirect('login')

# Standard registration flow using Django's built-in UserCreationForm.
# On success, the user is logged in automatically and sent to complete their profile.
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-control'
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Tu cuenta fue creada satisfactoriamente!')
            return redirect('profile_edit')
    else:
        form = UserCreationForm()
        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-control'
    return render(request, 'usuarios/register.html', {'form': form})

# Redirects already authenticated users away from the login page.
# Bootstrap classes are applied directly to the form widgets here
# because AuthenticationForm is a built-in Django form with no custom Meta class.
def login_view(request):
    if request.user.is_authenticated:
        return redirect('outings_list')
    elif request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-control'
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('outings_list')
    else:
        form = AuthenticationForm()
        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-control'
    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# Handles both creating a new profile and editing an existing one.
# The try/except block covers first-time users who don't have a profile yet.
# The profile object is passed to the template so it can display the current photo.
@login_required
def profile_edit(request):
    try:
        profile = request.user.profile
    except:
        profile = None

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Perfil guardado!')
            return redirect('outings_list')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'usuarios/profile_edit.html', {'form': form, 'profile': profile})


# Shows users from the same city as the logged-in user.
# Falls back to an empty list if the user hasn't set up their profile yet.
@login_required
def nearby_users(request):
    try:
        user_profile = request.user.profile
        users = Profile.objects.exclude(user=request.user).filter(city=user_profile.city)
    except:
        users = []
    return render(request, 'usuarios/nearby_users.html', {'users': users})


# Pre-fills the city field with the user's profile city to save them a step.
@login_required
def create_outing(request):
    if request.method == 'POST':
        form = OutingForm(request.POST)
        if form.is_valid():
            outing = form.save(commit=False)
            outing.creator = request.user
            outing.save()
            messages.success(request, '¡Publicación creada!')
            return redirect('outings_list')
    else:
        try:
            initial_city = request.user.profile.city
        except:
            initial_city = ''
        form = OutingForm(initial={'city': initial_city})
    return render(request, 'usuarios/create_outing.html', {'form': form})


# Main feed. Excludes the current user's own outings and supports
# optional filtering by city (case-insensitive) and exact date.
# Also passes a list of outing IDs the user has already liked
# so the template can toggle the button state.
@login_required
def outings_list(request):
    outings = Outing.objects.filter(is_active=True).exclude(creator=request.user).order_by('-created_at')

    city = request.GET.get('city')
    date = request.GET.get('date')

    if city:
        outings = outings.filter(city__icontains=city)
    if date:
        outings = outings.filter(date=date)

    user_interests = Interest.objects.filter(user=request.user).values_list('outing_id', flat=True)
    return render(request, 'usuarios/outings_list.html', {
        'outings': outings,
        'user_interests': user_interests,
        'search_city': city or '',
        'search_date': date or ''
    })


# Toggles interest on or off. If the user is interested for the first time,
# a notification is sent to the outing creator.
# Cancelled outings are blocked from receiving new interests.
@login_required
def toggle_interest(request, outing_id):
    outing = Outing.objects.get(id=outing_id)
    if not outing.is_active:
        messages.error(request, 'Esta salida ya fue cancelada.')
        return redirect('outings_list')
    interest, created = Interest.objects.get_or_create(user=request.user, outing=outing)
    if not created:
        interest.delete()
        messages.success(request, 'Ya no estás interesado.')
    else:
        messages.success(request, '¡Interés registrado!')
        Notification.objects.create(
            user=outing.creator,
            sender=request.user,
            message=f'{request.user.username} está interesado en tu salida: {outing.place}'
        )
    return redirect('outings_list')


# Shows all outings created by the logged-in user, including cancelled ones.
@login_required
def my_outings(request):
    outings = Outing.objects.filter(creator=request.user).order_by('-created_at')
    return render(request, 'usuarios/my_outings.html', {'outings': outings})


# Soft delete — sets is_active to False instead of removing the record.
# Only the creator can cancel their own outing.
@login_required
def cancel_outing(request, outing_id):
    outing = Outing.objects.get(id=outing_id, creator=request.user)
    outing.is_active = False
    outing.save()
    messages.success(request, 'Salida cancelada.')
    return redirect('my_outings')


# Checks the friendship status between the logged-in user and the profile being viewed
# so the template can render the correct button (add, pending, accept, or remove).
@login_required
def user_profile(request, user_id):
    profile_user = User.objects.get(id=user_id)
    try:
        profile = profile_user.profile
    except:
        profile = None

    friendship_status = None
    friendship_id = None

    try:
        friendship = Friendship.objects.get(sender=request.user, receiver=profile_user)
        friendship_status = 'pending_sent' if friendship.status == 'pending' else 'accepted'
        friendship_id = friendship.id
    except Friendship.DoesNotExist:
        try:
            friendship = Friendship.objects.get(sender=profile_user, receiver=request.user)
            friendship_status = 'pending_received' if friendship.status == 'pending' else 'accepted'
            friendship_id = friendship.id
        except Friendship.DoesNotExist:
            pass

    return render(request, 'usuarios/user_profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'friendship_status': friendship_status,
        'friendship_id': friendship_id
    })


# Marks all unread notifications as read as soon as the user opens the page.
@login_required
def notifications(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'usuarios/notifications.html', {'notifs': notifs})


# Fetches the full message history between two users and marks incoming
# messages as read. Prevents users from messaging themselves.
@login_required
def conversation(request, user_id):
    other_user = User.objects.get(id=user_id)
    if other_user == request.user:
        return redirect('inbox')
    messages_list = Message.objects.filter(
        sender=request.user, receiver=other_user
    ) | Message.objects.filter(
        sender=other_user, receiver=request.user
    )
    messages_list = messages_list.order_by('created_at')

    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content
            )
            return redirect('conversation', user_id=user_id)

    return render(request, 'usuarios/conversation.html', {
        'other_user': other_user,
        'messages_list': messages_list
    })


# Groups received messages by sender so each contact appears only once.
# Also calculates unread count per conversation for the badge display.
@login_required
def inbox(request):
    received = Message.objects.filter(receiver=request.user).exclude(sender=request.user).order_by('-created_at')
    seen_users = []
    conversations = []
    for msg in received:
        if msg.sender.id not in seen_users:
            seen_users.append(msg.sender.id)
            unread = Message.objects.filter(sender=msg.sender, receiver=request.user, is_read=False).count()
            conversations.append({'msg': msg, 'unread': unread})
    return render(request, 'usuarios/inbox.html', {'conversations': conversations})


# Custom 404 handler. Registered in urls.py and only active when DEBUG=False.
def error_404(request, exception):
    return render(request, '404.html', status=404)


# Deletes the photo file from disk and clears the field in the database.
@login_required
def remove_photo(request):
    try:
        profile = request.user.profile
        profile.photo.delete()
        profile.photo = None
        profile.save()
        messages.success(request, 'Foto eliminada.')
    except:
        pass
    return redirect('profile_edit')


# Sends a friend request and notifies the receiver.
# Uses get_or_create to prevent duplicate requests.
@login_required
def send_friend_request(request, user_id):
    receiver = User.objects.get(id=user_id)
    if receiver != request.user:
        friendship, created = Friendship.objects.get_or_create(
            sender=request.user,
            receiver=receiver
        )
        if created:
            Notification.objects.create(
                user=receiver,
                sender=request.user,
                message=f'{request.user.username} te envió una solicitud de amistad'
            )
            messages.success(request, '¡Solicitud de amistad enviada!')
        else:
            messages.info(request, 'Ya enviaste una solicitud a este usuario.')
    return redirect('user_profile', user_id=user_id)


# Only the intended receiver can accept a request.
# Sends a notification back to the original sender on acceptance.
@login_required
def accept_friend_request(request, friendship_id):
    friendship = Friendship.objects.get(id=friendship_id)
    if friendship.receiver == request.user:
        friendship.status = 'accepted'
        friendship.save()
        Notification.objects.create(
            user=friendship.sender,
            sender=request.user,
            message=f'{request.user.username} aceptó tu solicitud de amistad'
        )
        messages.success(request, '¡Amistad aceptada!')
    return redirect('friends')


@login_required
def reject_friend_request(request, friendship_id):
    friendship = Friendship.objects.get(id=friendship_id)
    if friendship.receiver == request.user:
        friendship.status = 'rejected'
        friendship.save()
        messages.success(request, 'Solicitud rechazada.')
    return redirect('notifications')


# Builds the friends list by checking both directions of the friendship —
# the current user could be either the sender or the receiver.
# Also fetches pending incoming requests to show at the top of the page.
@login_required
def friends(request):
    friendships = Friendship.objects.filter(
        status='accepted'
    ).filter(
        models.Q(sender=request.user) | models.Q(receiver=request.user)
    )
    friends_list = []
    for f in friendships:
        if f.sender == request.user:
            friends_list.append(f.receiver)
        else:
            friends_list.append(f.sender)

    pending = Friendship.objects.filter(receiver=request.user, status='pending')

    return render(request, 'usuarios/friends.html', {
        'friends_list': friends_list,
        'pending': pending
    })


# Removes the friendship in both directions so neither user sees the other as a friend.
@login_required
def remove_friend(request, user_id):
    other_user = User.objects.get(id=user_id)
    Friendship.objects.filter(
        sender=request.user, receiver=other_user
    ).delete()
    Friendship.objects.filter(
        sender=other_user, receiver=request.user
    ).delete()
    messages.success(request, 'Amigo eliminado.')
    return redirect('friends')