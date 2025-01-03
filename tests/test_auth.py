import unittest
from app import create_app, db
from app.models import *

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_registration(self):
        response = self.client.post("/auth/register", content_type="multipart/form-data", data={
            "email": "test@email.com",
            "password": "t35t@password",
            "password_confirm": "t35t@password",
            "first_name": "Best",
            "last_name": "Friend"
        })
        print(response)

        self.assertEqual(response.status, 200)
        user = Users.query.filter_by(first_name="Best").first()
        self.assertIsNotNone(user)

# Add more test methods as needed