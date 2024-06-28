from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from datetime import datetime
import pickle


# Create your views here.
def feed_page(request):
    
    if request.user.is_anonymous:
        return redirect('/login/')

    if (request.method == "POST"):
        post_text_title = request.POST.get('post-text-title')
        post_text_desc = request.POST.get('post-text-message')
    
        post_image_title = request.POST.get('post-image-title')
        post_image_desc = request.POST.get('post-image-message')
        post_image_image = request.FILES.get('post-image-image')


        # If there's no title for the text post title this means that the image post is being submited.
        if (post_text_title == None):
            new_image_post = Post(belongs_to = request.user, post_title = post_image_title, post_picture = post_image_image, is_image_post = True, post_description = post_image_desc, created_at = datetime.now())
            new_image_post.save()
            messages.success(request, "New Image Post is posted on the social media platform. 😀")
            return redirect('/')

        else:
            new_text_post = Post(belongs_to = request.user, post_title = post_text_title, 
                                post_description = post_text_desc, created_at = datetime.now())
            new_text_post.save()
            messages.success(request, "New Text Post is posted on the social media platform. 😀")
            return redirect('/')
    
    
    # Logic Behind the Try-Catch.
    # If a user profile of the current user is not found, it will through an error, the error will clearly indicate the new-user has just created an account, but he/she has not created his UserProfile, so he/she will be redirected to do so.
    # The User Must create a "User-Profile" in order to view the feed_page.
    
    try:
        user_data = UserProfile.objects.get(user = request.user)
        all_posts = Post.objects.order_by('-created_at')                # This will order-by and will display the recent posts at first.
        no_of_posts = Post.objects.filter(belongs_to = request.user).count()
        no_of_new_users = helper_func(request, 2)
    
    except Exception as e:
        messages.warning(request, "Please Provide us with furthur details and complete you're UserProfile.😀")
        return redirect('/create_user_profile/')

    context = {'user_profile_info': user_data, 'posts': all_posts, 'no_of_posts': no_of_posts, 'no_of_new_users': no_of_new_users}
    return render(request, "feed_page.html", context = context)


def login_page(request):

    if (request.method == "POST"):
        login_username = request.POST.get('login-username')
        login_password = request.POST.get('login-password')
        
        signup_username = request.POST.get('signup-username')
        signup_email= request.POST.get('signup-email')
        signup_password = request.POST.get('signup-password')

        # If this signup field is None, then the user is trying to Login the website.
        if (signup_username == None):
            
            user = authenticate(username = login_username, password = login_password)

            if user is not None:
                login(request, user)
                return redirect('/')
            
            else:
                messages.warning(request, "Please Check You're UserName and Password and try again.")

        else:
            
            # If the user enters username that already exists with some user then Exception will be raised.
            try:
                new_user = User(username = signup_username, email = signup_email)
                new_user.set_password(signup_password)
                new_user.save()

                login(request, new_user)
                messages.success(request, "Your're Account Has been created Successfully. 😀")

                # After the successfull creation of the User account the user must create his UserProfile with all necessary details.
                # Otherwise the user will not be allowed to view the feed_page.
                return redirect('/create_user_profile/')

            except Exception as e:
                messages.warning(request, "User With Same Username Exists in our Database. Please Set A New Username.")
    
    return render(request, "login.html")


def create_user_profile(request):

    if (request.method == "POST"):
        first_name = request.POST.get('user-profile-fname').title()
        last_name = request.POST.get('user-profile-lname').title()
        desc = request.POST.get('user-profile-desc')
        profile_pic = request.FILES.get('user-profile-image')
        
        # This will update the first_name and the last_name of the User object.
        current_user = request.user
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.save()

        # This will create the user_profile for the new user who has just signed up.
        user_profile_obj = UserProfile(user = current_user, profile_pic = profile_pic, followers_list = pickle.dumps([]), 
                                       following_list = pickle.dumps([]), profile_desc = desc, created_at = datetime.now())

        user_profile_obj.save()
        return redirect('/')

    return render(request, "create_user_profile.html")


def logout_user(request):
    logout(request)
    return redirect('/login/')


# This function is designed to perform 2 tasks.
# When task_id = 1 --> This will return the actual list of new-users that can be followed by the current user (i.e they are not-followed by the current user will now)
# When task_id = 2 --> This will return the count of such new-users possible. (These count is required to display in the navbar check 'feed_page' function ON TOP)

def helper_func(request, task_id):
    user_profile = UserProfile.objects.get(user = request.user)
    
    # The User Object except the current user object can be treated as friend. ( No User Can be his/her own friend )
    all_users_available = UserProfile.objects.exclude(user = request.user)           

    # This returns the profiles of the users that the current user is already following.
    already_followed_users = pickle.loads(user_profile.following_list)   

    # All the users, except the users that are already followed are being displayed in the friend section.
    users_not_already_following = []
    for user in all_users_available:
        if (user not in already_followed_users):
            users_not_already_following.append(user)

    if (task_id == 1):
        return users_not_already_following
    
    elif (task_id == 2):
        return len(users_not_already_following)


# This function display's the list of new-users that the current user can follow.
def friend_list(request):
    
    user_profile = UserProfile.objects.get(user = request.user)

    # In This case the helper_func will generate the real-list of users that the current user is not following.
    users_not_already_following = helper_func(request, 1)            
    
    context = {'user_profile_info': user_profile, 'all_user_list': users_not_already_following, 
               'no_of_new_users': len(users_not_already_following)}
    return render(request, "friend_list.html", context=context)



# This function will handel the request's when the current user will send follow request to new users.
#  LOGIC BEHIND THE OPERATION : 
    # When the current_user will follow a friend_user, then the friend_user will be added to the following_list of the current_user.
    # and the current_user will be added to the followers_list of the friend_user.
    
def follow_user(request, pk):
    
    userProfile = UserProfile.objects.get(user = request.user)   # This will return as the user profile of the current user.
    current_user_following_list = pickle.loads(userProfile.following_list)  # This will return the following_list of the current user.
    
    friend_user = UserProfile.objects.get(id = pk)                      # The user profile whom we want to follow.
    friend_follower_list = pickle.loads(friend_user.followers_list)    # This will return the followers_list of the friend user.

    if (friend_user not in current_user_following_list):
    
        current_user_following_list.append(friend_user)  # Add the new friend to the following list.
        userProfile.following += 1                       # If a new user is being followed then the following count will increment by 1.
        friend_user.followers += 1                       # The user i followed his/her followers count will increment by 1.
        friend_follower_list.append(userProfile)         # If the user has followed the friend_profile, then he will be his new follower.

        userProfile.following_list = pickle.dumps(current_user_following_list)  # Update the following_list of the current user.
        friend_user.followers_list = pickle.dumps(friend_follower_list)         # Update the followers_list of the friend user.

        friend_user.save()
        userProfile.save()                                                # save the profile.

        messages.success(request, f"You have successfully followed @{friend_user.user.username}.")

    else:
        messages.warning(request, f"Your're already following user @{friend_user.user.username}.")

    return redirect('/friend_list/')



# This function will handel the request's when the current user will send unfollow request to new users.
#   LOGIC BEHIND THE OPERATION : 
    # When the current_user will unfollow a already following_user, then the already following_user will be removed from the  following_list of the current_user.
    # and the current_user will also be removed from the followers_list of the already following_user.

def unfollow_user(request, pk):

    currentUserProfile = UserProfile.objects.get(user = request.user)
    unfollow_user_profile = UserProfile.objects.get(id = pk)

    following_list = pickle.loads(currentUserProfile.following_list)           # This is the following_list of the current user.
    followers_list = pickle.loads(unfollow_user_profile.followers_list)        # This is the followers_list of the current user.

    if (unfollow_user_profile in following_list):
        
        # Removed the current_user and the unfollow_user from the following and followers list respectively.
        following_list.remove(unfollow_user_profile)
        followers_list.remove(currentUserProfile)

        # Update the follower and the following list.
        currentUserProfile.following_list = pickle.dumps(following_list)
        unfollow_user_profile.followers_list = pickle.dumps(followers_list)
        
        # Decrement the follower and the following count.
        currentUserProfile.following -= 1
        unfollow_user_profile.followers -= 1

        # Save the changes applied to the profile.
        currentUserProfile.save()
        unfollow_user_profile.save()

        messages.success(request, f"You Have Successfully unfollowed user @{unfollow_user_profile.user.username}.")

    else:
        messages.warning(request, f"The User @{unfollow_user_profile.user.username} is already unfollowed.")

    return redirect('/')


# This function is used to view the individual profile of all the users except the current logged-in user.
# This provides us a detail page about the user-profile that we want to see.
def view_individual_user(request, pk):
    
    current_user_profile = UserProfile.objects.get(user = request.user)
    query_user = UserProfile.objects.get(id = pk)

    # We cannot view the simple profile of the current user.
    # We have to view the settings profile of the current user, so whenever the current_profile and the query_profile is same the user is directly redirected to the "update_user_profile" url where he has upgraded settings to modify his/her profile.
    if (current_user_profile == query_user):
        return redirect('/update_user_profile/')
    

    posts = Post.objects.filter(belongs_to = query_user.user)
    
    # This is used to identify whether the queried user is followed by the current user or not.
    is_already_following = False
    following_list = pickle.loads(current_user_profile.following_list)

    if (query_user in following_list):
        is_already_following = True    


    no_of_new_users = helper_func(request, 2)

    context = {'user_profile_info': current_user_profile, 'query_user': query_user, 'query_user_posts': posts, 
               'no_of_new_users': no_of_new_users, 'is_already_following': is_already_following}
    return render(request, "view_individual_user.html", context = context)


# This function is for the current logged-in user.
# If the user wants to changes his/her personal details OR if they wish to delete a post. They can do so easily.
def update_profile(request):
    
    current_user_profile = UserProfile.objects.get(user = request.user)
    current_user = current_user_profile.user

    if (request.method == "POST"):
        first_name = request.POST.get('profile-first-name')
        last_name = request.POST.get('profile-last-name')
        email = request.POST.get('profile-email')
        description = request.POST.get('profile-desc')
        
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = email
        
        current_user.save()

        current_user_profile.profile_desc = description

        current_user_profile.save()
        
        return redirect('/update_user_profile/')


    no_of_new_users = helper_func(request, 2)
    query_posts = Post.objects.filter(belongs_to = request.user)

    context = {'user_profile_info': current_user_profile, 'query_user': current_user_profile, 'no_of_new_users': no_of_new_users, 
               'query_user_posts': query_posts}
    
    return render(request, "update_profile.html", context = context)


# This function is responsible for deleting the irrelevant posts from the current user profile.
def delete_post(request, pk):
    
    post = Post.objects.get(id = pk)

    messages.success(request, f"You're Post Titled {post.post_title} has been deleted.")
    post.delete()

    return redirect('/update_user_profile/')


# This function will be responsible for the like and dislike of the post by the current-user.
def like_post(request, pk):
    
    current_user_profile = UserProfile.objects.get(user = request.user)
    post = Post.objects.get(id = pk)

    liked_users_list = pickle.loads(post.list_of_user_liked_the_post)

    # If the current user likes the post.
    if (current_user_profile not in liked_users_list):

        post.no_of_likes += 1
        liked_users_list.append(current_user_profile)
        post.list_of_user_liked_the_post = pickle.dumps(liked_users_list)

        post.save()

    # If the current user dis-likes the post.
    else:
        post.no_of_likes -= 1
        liked_users_list.remove(current_user_profile)
        post.list_of_user_liked_the_post = pickle.dumps(liked_users_list)

        post.save()

    return redirect('/')



