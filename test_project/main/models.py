# Python imports
import re

# Django imports
#from django.contrib.sitemaps import ping_google
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.conf import settings

class _Abstract(models.Model):     #microblog compatible.
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=140, unique=True)
    text = models.TextField(default='')
    rendered_text = models.TextField(default='', blank=True)

    def __unicode__(self):
        return self.title
        
    class Meta:
        abstract = True

class Channel(_Abstract):
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL)

    ENROLLMENTS = (
        (0, 'SELF', 'Self'),
        (1, 'AUTHOR', 'Author'),
    )

    public = models.BooleanField(default=True, help_text="If False, only followers will be able to see content.")

    enrollment = models.IntegerField(max_length=1, default=0, choices=ENROLLMENTS)

    class Meta:
        ordering = ['title']

class Post(_Abstract):
    SUMMARY_LENGTH = 50

    STATUSES = [
        (0, 'DRAFT',     'Draft',),
        (1, 'PUBLISHED', 'Published',),
    ]

    channel         = models.ForeignKey(Channel)
    author          = models.ForeignKey(settings.AUTH_USER_MODEL)
    status          = models.IntegerField(max_length=1, default=0, choices=STATUSES)
    custom_summary  = models.TextField(default='')
    created         = models.DateTimeField(auto_now_add=True, editable=False)
    modified        = models.DateTimeField(auto_now=True, editable=False)
    published       = models.DateTimeField(default=timezone.now())

    @property
    def teaser(self):
        "A small excerpt of text that can be used in the absence of a custom summary."
        return self.text[:Post.SUMMARY_LENGTH]

    @property
    def summary(self):
        "Returns custom_summary, or teaser if not available."
        if len(self.custom_summary) > 0:
            return self.custom_summary
        else:
            return self.teaser
    
    @property
    def time_diff(self):
        return self.modified - self.created

    class Meta:
        ordering = ['published']
