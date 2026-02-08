# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .models import Room, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # 1) Refuse les frames vides
        if not text_data:
            await self.send(text_data=json.dumps({"type": "error", "error": "Empty message"}))
            return

        # 2) JSON valide ?
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"type": "error", "error": "Invalid JSON"}))
            return

        # 3) Champ "message" présent et non vide ?
        message_content = (data.get("message") or "").strip()
        if not message_content:
            await self.send(text_data=json.dumps({"type": "error", "error": "Empty message"}))
            return

        author = (data.get("author") or "anonymous").strip()

        # 4) Sauvegarde DB (Room + Message)
        room, _ = await Room.objects.aget_or_create(name=self.room_name)
        msg = await Message.objects.acreate(
            room=room,
            author=author,
            content=message_content,
            created_at=timezone.now(),
        )

        # 5) Broadcast aux membres du groupe WS
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "id": msg.id,
                "author": msg.author,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
