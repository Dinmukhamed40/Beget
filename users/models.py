from django.db import models
from django.contrib.auth.models import User

def user_directory_path(instance, filename):
    return f'avatars/user_{instance.user.id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='avatars')

    def __str__(self):
        return f'Профиль {self.user.username}'

class Game(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    genre = models.CharField(max_length=100, verbose_name="Жанр")
    rating = models.FloatField(verbose_name="Рейтинг")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to='game_covers/', default='default_game.png', verbose_name="Постер")
    release_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

class ChatMessage(models.Model):
    user = models.CharField(max_length=100)
    question = models.TextField()
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.question[:20]}"

class BotKnowledge(models.Model):
    category = models.CharField(max_length=100)
    keyword = models.CharField(max_length=100)
    answer = models.TextField()

    def __str__(self):
        return f"[{self.category}] {self.keyword}"