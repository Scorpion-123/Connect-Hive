from django import template
from social_app.models import *
import pickle

register = template.Library()

@register.filter(name = "get_image_url")
def get_image_url(user_obj):
    
    user_obj = UserProfile.objects.get(user = user_obj)
    return user_obj.profile_pic.url


@register.filter(name = "get_data")
def get_data(binary_data):
    return pickle.loads(binary_data)


@register.filter(name = "get_userprofile_id")
def get_userprofile_id(user_obj):
    
    user = UserProfile.objects.get(user = user_obj)
    return user.id


# This filter is used to determine the color of the Like Button. 
# If the user has liked the post then the UserProfile will be present in the 'liked_users_list' and the color of the Like Button will be 'Red' Indicating the user has liked the post.
# If not, then the like button will be 'Blue' in Color as usual.
@register.filter(name="has_current_user_liked")
def has_current_user_liked(post_obj, user_obj):
    
    user_profile = UserProfile.objects.get(user = user_obj)
    liked_users_list = pickle.loads(post_obj.list_of_user_liked_the_post)

    if (user_profile in liked_users_list):
        return True
    else:
        return False