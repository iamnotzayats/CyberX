import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Users(AbstractUser):
    first_name = None
    last_name = None

    USERNAME_FIELD = 'username'

    class Meta:
        ordering = ('username',)


def generate_unique_slug(klass, field):
    origin_slug = slugify(field)
    unique_slug = origin_slug
    numb = 1
    while klass.objects.filter(slug=unique_slug).exists():
        unique_slug = f'{origin_slug}-{numb}'
        numb += 1
    return unique_slug


def news_image_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    now = timezone.now()

    if instance.news:
        base = instance.news.slug or slugify(instance.news.title) or "news"
    else:
        base = "news"

    unique_id = uuid.uuid4().hex[:8]
    return f"images/news/{now:%Y/%m/%d}/{base}-{unique_id}{ext}"


def disciplines_image_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    unique_id = uuid.uuid4().hex[:8]
    base = slugify(instance.name) or "discipline"
    return f"images/disciplines/{base}-{unique_id}{ext}"


class NewsPicture(models.Model):
    image = models.ImageField(upload_to=news_image_upload_to, null=True, blank=True)
    news = models.ForeignKey(
        'News',
        on_delete=models.CASCADE,
        related_name='pictures',
    )

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f'{self.news.title} - {self.image}'


class NewsCategory(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Badge(models.Model):
    name = models.CharField(max_length=100)
    priority = models.PositiveSmallIntegerField(default=100)

    class Meta:
        ordering = ('priority', 'name')

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=200, unique=True, null=False, blank=False)
    content = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=200, unique=True, null=False, blank=False)
    pub_date = models.DateTimeField(auto_now_add=True)

    categories = models.ManyToManyField(NewsCategory, blank=True, related_name='news_set')
    badge = models.ManyToManyField(Badge, blank=True, related_name='news_set')

    class Meta:
        ordering = ('-pub_date',)

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            self.slug = generate_unique_slug(News, self.title)
        super().save(*args, **kwargs)

    @property
    def main_image(self):
        return self.pictures.first()

    def __str__(self):
        return self.title


class Disciplines(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to=disciplines_image_upload_to, null=True, blank=True)

    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"

    def __str__(self):
        return self.name