import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Room, Message

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Ensure the room exists
        await self.get_or_create_room(self.room_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Be tolerant: never crash the consumer on bad payloads
        try:
            payload = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            await self.send_json({"type": "error", "error": "Invalid JSON"})
            return

        author = (payload.get("author") or "anonymous").strip()[:64]
        content = (payload.get("content") or "").strip()

        if not content:
            await self.send_json({"type": "error", "error": "Empty message"})
            return

        try:
            msg = await self.create_message(self.room_name, author, content)
        except Exception:
            logger.exception("Failed to create message")
            await self.send_json({"type": "error", "error": "Server error saving message"})
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "id": msg["id"],
                "author": msg["author"],
                "content": msg["content"],
                "created_at": msg["created_at"],
            },
        )

    async def chat_message(self, event):
        await self.send_json(event)

    async def send_json(self, data: dict):
        await self.send(text_data=json.dumps(data, ensure_ascii=False))

    @database_sync_to_async
    def get_or_create_room(self, name: str):
        Room.objects.get_or_create(name=name)

    @database_sync_to_async
    def create_message(self, room_name: str, author: str, content: str):
        room, _ = Room.objects.get_or_create(name=room_name)
        msg = Message.objects.create(room=room, author=author, content=content)
        return {
            "id": msg.id,
            "author": msg.author,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
        }
