from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from note.models import Note
from .serializers import (NoteListSerializer, NoteDetailSerializer, NoteCreateSerializer,
                          NoteUpdateSerializer, )


class NoteListView(generics.ListAPIView):
    search_fields = (
        "description",
    )

    serializer_class = NoteListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(
            user=self.request.user
        )

class NoteDetailView(generics.RetrieveAPIView):
    serializer_class = NoteDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(
            user=self.request.user
        )

class NoteCreateView(generics.CreateAPIView):
    serializer_class = NoteCreateSerializer
    permission_classes = [IsAuthenticated]

class NoteUpdateView(generics.UpdateAPIView):
    serializer_class = NoteUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["put"]

    def get_queryset(self):
        return Note.objects.filter(
            user=self.request.user
        )

class NotePartialUpdateView(generics.UpdateAPIView):
    serializer_class = NoteUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def get_queryset(self):
        return Note.objects.filter(
            user=self.request.user
        )

class NoteDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ["delete"]

    def get_queryset(self):
        return Note.objects.filter(
            user=self.request.user
        )