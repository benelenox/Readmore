import json
from channels.generic.websocket import WebsocketConsumer
from channels import layers
from asgiref.sync import async_to_sync
from .models import UserExt, ClubChat, Club
from datetime import datetime

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = 'club_chat_%s' % self.room_id
        
        self.user = UserExt.objects.get(pk=self.scope['user'].id)
        self.club = Club.objects.get(pk=int(self.room_id))

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        
        new_chat = ClubChat()
        new_chat.chat_message = f"{self.user.username} has joined the chat"
        new_chat.chat_destination = self.club
        new_chat.chat_type = "info"
        new_chat.save()
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'message': f"{self.user.username} has joined the chat",
                'user': "",
                'time': datetime.strftime(datetime.now(), "%m/%d/%Y %I:%M %p"),
                'type': 'join'
            }
        )

    def disconnect(self, close_code):
        # Leave room group
        new_chat = ClubChat()
        new_chat.chat_message = f"{self.user.username} has left the chat"
        new_chat.chat_destination = self.club
        new_chat.chat_type = "info"
        new_chat.save()

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'message': f"{self.user.username} has left the chat",
                'user': self.user.username,
                'time': datetime.strftime(datetime.now(), "%m/%d/%Y %I:%M %p"),
                'type': 'leave'
            }
        )
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        new_chat = ClubChat()
        new_chat.chat_user = self.user
        new_chat.chat_message = message
        new_chat.chat_destination = self.club
        new_chat.save()
        
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
                'time': datetime.strftime(new_chat.chat_time, "%m/%d/%Y %I:%M %p")
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        user = event['user']
        time = event['time']
        type = event['type']
        
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'user': user,
            'time': time,
            'type': type
        }))
    
    def join(self, event):
        self.send(text_data=json.dumps(event))
    
    def leave(self, event):
        self.send(text_data=json.dumps(event))