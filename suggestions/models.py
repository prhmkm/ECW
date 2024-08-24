from django.db import models

class SuggestionSample(models.Model):
    user = models.ForeignKey("dashboard.User", related_name='octuserS' , on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    isSeen = models.BooleanField(default=False)
    def __str__(self):
        return self.title + "/" + self.description
