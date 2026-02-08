from django.shortcuts import render
from rest_framework import generics

from .models import Room, Message
from .serializers import RoomSerializer, MessageSerializer


def index(request):
    return render(request, "chat/index.html")


class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all().order_by("name")
    serializer_class = RoomSerializer


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        return Message.objects.filter(room_id=room_id).order_by("created_at")[:200]
