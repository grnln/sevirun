from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='articles/')

    def __str__(self):
        return self.title

class DisplayCase(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.article.id)