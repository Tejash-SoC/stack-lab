from rest_framework import viewsets

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """Full CRUD on the signed-in user's own tasks. Optional ?status=todo filter."""

    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = Task.objects.filter(owner=self.request.user)
        status = self.request.query_params.get("status")
        return qs.filter(status=status) if status else qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
