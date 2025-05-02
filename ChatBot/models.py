from django.db import models

class ChatMessage(models.Model):
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chatbot_chatmessage'
        
    def __str__(self):
        return f"User: {self.user_message[:30]}..."
