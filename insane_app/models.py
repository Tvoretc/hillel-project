from django.db import models
from django.db.models import F
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import escape

User = get_user_model()


class SanityRank(models.Model):
    name = models.CharField(unique=True, max_length=20)
    sanity_cap = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sanity = models.PositiveIntegerField(default=0)
    rank = models.ForeignKey(SanityRank, on_delete=models.PROTECT)

    # creates Profile when User is created
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            rank = SanityRank.objects.first()
            Profile.objects.create(user=instance, sanity=rank.sanity_cap, rank=rank)

    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    class Meta:
        ordering = ['user']
        db_table = 'insane_user'

    def __str__(self):
        return self.user.username

    def modify_sanity(delta):
        Profile.objects.filter(sanity__lt=F('rank.sanity_cap')).sanity = F('sanity') + delta


class UserGroup(models.Model):
    name = models.CharField(max_length=32)

    def get_new_admin(self):
        return self.members.first()

    members = models.ManyToManyField(
        User,
        related_name='user_group',
        through='Membership',
        through_fields=('user_group', 'user')
    )
    dt_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def add_member(self, new_user):
        Membership.objects.create(user=new_user, user_group=self)


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_group = models.ForeignKey(UserGroup, on_delete=models.CASCADE)
    ROLES = (
        ('ad', 'admin'),
        ('mb', 'member'),
    )
    role = models.CharField(max_length=2, choices=ROLES)

    class Meta:
        unique_together = (('user', 'user_group'),)

    def __str__(self):
        return f'{self.user_group.name} - {self.user.username}[{self.get_role_display()}]'


class Story(models.Model):
    name = models.CharField(max_length=64)
    body = models.TextField(max_length=600)
    like_count = models.PositiveIntegerField(default=0, blank=True)
    dt_created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('insane:story', args=[self.pk])


def get_story_image_path (instance, filename):
    return f"images/{instance.author.username}/{filename}"


class StoryImage(models.Model):
    image = models.ImageField(upload_to=get_story_image_path)
    product = models.ForeignKey(
        Story,
        related_name='image',
        on_delete=models.CASCADE
    )


class StoryLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("user", "story"),)

    def __str__(self):
        return f"{self.user.username} likes {self.story.name}"


@receiver(post_save, sender=StoryLike)
def _story_like_save(sender, instance, **kwargs):
    print(instance.story.pk)
    Story.objects.filter(pk=instance.story.pk).update(like_count=F('like_count')+1)

@receiver(pre_delete, sender=StoryLike)
def _story_like_delete(sender, instance, **kwargs):
    Story.objects.filter(pk=instance.story.pk).update(like_count=F('like_count')-1)


class StoryComment(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    text = models.TextField(max_length=300)
    like_count = models.PositiveIntegerField()
    dt_created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}`s comment on {self.story.name}."


class StoryCommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(StoryComment, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("user", "comment"),)

    def __str__(self):
        return f"{self.user.username} likes {self.comment.user.username}`s comment on {self.comment.story.name}."

@receiver(post_save, sender=StoryCommentLike)
def _story_comment_like_save(sender, instance, **kwargs):
    StoryComment.objects.filter(pk=instance.comment.pk).update(like_count=F('like_count')+1)

@receiver(pre_delete, sender=StoryCommentLike)
def _story_comment_like_delete(sender, instance, **kwargs):
    StoryComment.objects.filter(pk=instance.comment.pk).update(like_count=F('like_count')-1)

#
#   Product
#

class Category(models.Model):
    name = models.CharField(unique=True, max_length=20)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=500)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(
        Story,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    dt_created = models.DateTimeField(auto_now_add=True)
    # stock
    price = models.DecimalField(max_digits=10, decimal_places=2)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('insane:product', args=[self.pk])


# ProductImage
def get_product_image(instance, filename):
    return f"images/{instance.product.owner.username}/{filename}"


class ProductImage(models.Model):
    image = models.ImageField(upload_to=get_product_image)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('image', 'product'),)

    def __str__(self):
        return f"{self.product.name}, {self.image}"

    def image_tag(self):
        return f'<img src="/static/{self.image}"/>'

    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


class ProductComment(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    text = models.TextField(max_length=300)
    like_count = models.PositiveIntegerField()
    dt_created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}`s comment on {self.product.name}."


class ProductCommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(ProductComment, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("user", "comment"),)

    def __str__(self):
        return f"{self.user.username} likes {self.comment.user.username}`s comment on {self.comment.product.name}."
