from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import LoginForm


class IndexViewTests(TestCase):

    def test_login_required(self):
        client = Client()
        response = client.get(reverse('index:index'), follow=True)
        self.assertRedirects(
            response=response,
            expected_url='/login?next=/',
            status_code=302,
            target_status_code=200
        )

    def test_template(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        response = client.get(reverse('index:index'))
        self.assertTemplateUsed(response, template_name='index/index.html')

    def test_status_code(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        response = client.get(reverse('index:index'))
        self.assertEqual(response.status_code, 200)

    def test_links(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        response = client.get(reverse('index:index'))
        self.assertContains(response, reverse('ml:index'))
        # TODO: adicionar link para API


class LoginViewTests(TestCase):

    def test_template(self):
        client = Client()
        response = client.get(reverse('index:login_user'))
        self.assertTemplateUsed(response, template_name='index/login.html')

    def test_status_code(self):
        client = Client()
        response = client.get(reverse('index:login_user'))
        self.assertEqual(response.status_code, 200)

    def test_post_redirection(self):
        client = Client()
        User.objects.create_user(username='test_user', password='secret')
        response = client.post(
            path=reverse('index:login_user'),
            data={'username': 'test_user', 'password': 'secret'},
            follow=True
        )
        self.assertRedirects(
            response=response,
            expected_url=reverse('index:index'),
            status_code=302,
            target_status_code=200
        )

    def test_post_invalid_username(self):
        client = Client()
        User.objects.create_user(username='test_user', password='secret')
        response = client.post(
            path=reverse('index:login_user'),
            data={'username': 'invalid_username', 'password': 'secret'},
            follow=True
        )
        self.assertIsNotNone(response.context.get('error_message'))
        self.assertEqual(response.status_code, 200)

    def test_post_invalid_password(self):
        client = Client()
        User.objects.create_user(username='test_user', password='secret')
        response = client.post(
            path=reverse('index:login_user'),
            data={'username': 'test_user', 'password': 'invalid_password'},
            follow=True
        )
        self.assertIsNotNone(response.context.get('error_message'))
        self.assertEqual(response.status_code, 200)

    def test_post_empty_form(self):
        client = Client()
        User.objects.create_user(username='test_user', password='secret')
        response = client.post(
            path=reverse('index:login_user'),
            data={'username': '', 'password': ''},
            follow=True
        )
        self.assertIsNone(response.context.get('error_message'))
        self.assertEqual(response.status_code, 200)

    def test_form(self):
        client = Client(self)
        response = client.get(reverse('index:login_user'))
        self.assertIsInstance(response.context.get('form'), LoginForm)


class LogoutViewTests(TestCase):

    def test_redirection(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        response = client.get(reverse('index:logout_user'))
        self.assertRedirects(
            response=response,
            expected_url=reverse('index:login_user'),
            status_code=302,
            target_status_code=200
        )
