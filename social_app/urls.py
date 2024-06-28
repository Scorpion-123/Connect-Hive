from django.urls import path
from .views import *

urlpatterns = [
    path('', feed_page, name='feed_page'),

    path('login/', login_page, name='login_user'),
    path('logout/', logout_user, name='logout_user'),

    path('friend_list/', friend_list, name="friend_list"),
    path('create_user_profile/', create_user_profile, name="create_user_proofile"),

    path('follow_user/<int:pk>/', follow_user, name="follow_user"),
    path('unfollow_user/<int:pk>/', unfollow_user, name="unfollow_user"),
 
    path('view_individual_user/<int:pk>/', view_individual_user, name="view_individual_user"),
    path('update_user_profile/', update_profile, name="update_profile"),

    path('like_post/<int:pk>/', like_post, name="like_post"),

    path('delete_post/<int:pk>/', delete_post, name="delete_post"),
]