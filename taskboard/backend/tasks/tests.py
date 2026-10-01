from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Task

User = get_user_model()


class TaskApiTests(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345!")
        self.bob = User.objects.create_user("bob", password="pass12345!")

    def login(self, username):
        res = self.client.post(
            "/api/auth/login/", {"username": username, "password": "pass12345!"}
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_requires_auth(self):
        self.assertEqual(self.client.get("/api/tasks/").status_code, 401)

    def test_create_and_list_own_tasks_only(self):
        Task.objects.create(owner=self.bob, title="Bob's task")
        self.login("alice")
        res = self.client.post("/api/tasks/", {"title": "Write docs"})
        self.assertEqual(res.status_code, 201)
        listing = self.client.get("/api/tasks/")
        self.assertEqual([t["title"] for t in listing.data], ["Write docs"])

    def test_cannot_touch_other_users_task(self):
        task = Task.objects.create(owner=self.bob, title="Private")
        self.login("alice")
        self.assertEqual(self.client.delete(f"/api/tasks/{task.id}/").status_code, 404)

    def test_register(self):
        res = self.client.post(
            "/api/auth/register/", {"username": "carol", "password": "longenough1!"}
        )
        self.assertEqual(res.status_code, 201)
        self.assertNotIn("password", res.data)
