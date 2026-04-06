from django.contrib import admin
from django.urls import path
from usuarios import views
from django.conf import settings
from django.conf.urls.static import static

# Each path maps a URL to a view function and gives it a name
# so templates can use {% url 'name' %} instead of hardcoded paths.
urlpatterns = [
    # Django's built-in admin panel
    path('admin/', admin.site.urls),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # User profile
    path('', views.home, name='home'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/remove-photo/', views.remove_photo, name='remove_photo'),
    path('user/<int:user_id>/', views.user_profile, name='user_profile'),
    path('users/', views.nearby_users, name='nearby_users'),

    # Outings — open plans anyone nearby can discover and join
    path('outings/', views.outings_list, name='outings_list'),
    path('outings/create/', views.create_outing, name='create_outing'),
    path('outings/mine/', views.my_outings, name='my_outings'),
    path('outings/interest/<int:outing_id>/', views.toggle_interest, name='toggle_interest'),
    path('outings/cancel/<int:outing_id>/', views.cancel_outing, name='cancel_outing'),

    # Messaging
    path('messages/', views.inbox, name='inbox'),
    path('messages/<int:user_id>/', views.conversation, name='conversation'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),

    # Friendships
    path('friends/', views.friends, name='friends'),
    path('friends/request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friends/accept/<int:friendship_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friends/reject/<int:friendship_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('friends/remove/<int:user_id>/', views.remove_friend, name='remove_friend'),
]

# Serve media files (user uploads) during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom 404 page — active only when DEBUG=False in production
handler404 = 'usuarios.views.error_404'