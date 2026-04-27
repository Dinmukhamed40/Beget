from django.contrib import admin
from .models import Game, Profile, ChatMessage, BotKnowledge

admin.site.register(Game)
admin.site.register(Profile)
admin.site.register(ChatMessage)
admin.site.register(BotKnowledge)