from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    profile_pic = models.ImageField(upload_to="profile_pic", null = True, blank = True)
    profile_desc = models.TextField()

    followers_list = models.BinaryField()
    following_list = models.BinaryField()
    
    created_at = models.DateTimeField(auto_now = True)
    followers = models.IntegerField(default = 0)
    following = models.IntegerField(default = 0)

    def __str__(self):
        return f"{self.user.username} | {self.user.email}"
    


class Post(models.Model):
    
    belongs_to = models.ForeignKey(User, on_delete = models.CASCADE)

    post_title = models.CharField(max_length = 300)
    post_picture = models.ImageField(upload_to = "post_pic", null = True, blank = True)
    post_description = models.TextField()
    
    is_image_post = models.BooleanField(default = False)

    no_of_likes = models.IntegerField(default = 0)
    no_of_comments = models.IntegerField(default = 0)

    liked_by_current_user = models.BooleanField(default = False)
    list_of_user_liked_the_post = models.BinaryField()

    created_at = models.DateTimeField()


    def __str__(self):
        return f"{self.post_title} | Likes : {self.no_of_likes}"
    


class Comment(models.Model):
    
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
        
    comment = models.CharField(max_length = 500)
    reply = models.CharField(max_length = 500)
    commented_by = models.OneToOneField(User, on_delete = models.CASCADE, related_name = "commented_by_user")
    replied_by = models.OneToOneField(User, on_delete = models.CASCADE, related_name = "replied_by_user")
    
    def __str__(self):
        return f"{self.comment}"