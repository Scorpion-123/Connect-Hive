from social_app.models import *
import pickle


def reset_follower_and_following():
    users = UserProfile.objects.all()

    for user in users:
        user.followers = 0
        user.following = 0
        user.followers_list = pickle.dumps([])
        user.following_list = pickle.dumps([])

        user.save()


def reset_post_liked_data():
    posts = Post.objects.all()

    for post in posts:
        post.no_of_likes = 0
        post.list_of_user_liked_the_post = pickle.dumps([])

        post.save()