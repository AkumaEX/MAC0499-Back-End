from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UploadFile
from .forms import ChoiceFileForm
from .forms import UploadFileForm


def create_uploaded_file():
    file = SimpleUploadedFile(name='test.xls', content=b'file_content')
    data = UploadFile.objects.create(file=file)
    return data.pk


def remove_uploaded_file():
    query_set = UploadFile.objects.filter(file__startswith='test')
    for query in query_set:
        query.file.delete(save=True)


class IndexViewTests(TestCase):

    def test_template(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        response = client.get(reverse('ml:index'))
        self.assertTemplateUsed(response, template_name='ml/index.html')

    def test_status_code(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        response = client.get(reverse('ml:index'))
        self.assertEqual(response.status_code, 200)

    def test_form(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        response = client.get(reverse('ml:index'))
        self.assertIsInstance(response.context.get('form'), ChoiceFileForm)

    def test_start_links(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        response = client.get(reverse('ml:index'))
        self.assertContains(response, reverse('ml:upload'))
        self.assertNotContains(response, reverse('ml:configure'))
        self.assertNotContains(response, reverse('ml:delete'))

    def test_links(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        create_uploaded_file()
        response = client.get(reverse('ml:index'))
        self.assertContains(response, reverse('ml:upload'))
        self.assertContains(response, reverse('ml:configure'))
        self.assertContains(response, reverse('ml:delete'))
        remove_uploaded_file()


class UploadViewTests(TestCase):

    def test_template(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        response = client.get(reverse('ml:upload'))
        self.assertTemplateUsed(response, template_name='ml/upload.html')

    def test_status_code(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        response = client.get(reverse('ml:upload'))
        self.assertEqual(response.status_code, 200)

    def test_post_redirection(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        file = SimpleUploadedFile(name='test.xls', content=b'file_content')
        response = client.post(
            path=reverse('ml:upload'),
            data={'name': file.name, 'file': file},
            format='multipart/form-data',
            follow=True
        )
        self.assertRedirects(
            response=response,
            expected_url=reverse('ml:index'),
            status_code=302,
            target_status_code=200
        )
        remove_uploaded_file()

    def test_form(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        response = client.get(reverse('ml:upload'))
        self.assertIsInstance(response.context.get('form'), UploadFileForm)


class ConfigureViewTest(TestCase):

    def test_status_code(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        response = client.get(reverse('ml:configure'))
        self.assertRedirects(
            response=response,
            expected_url=reverse('ml:index'),
            status_code=302,
            target_status_code=200
        )

    def test_redirection(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        pk = create_uploaded_file()
        response = client.post(
            path=reverse('ml:configure'),
            data={'pk': pk},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        remove_uploaded_file()


class DeleteViewTests(TestCase):

    def test_redirection(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        pk = create_uploaded_file()
        response = client.post(
            path=reverse('ml:delete'),
            data={'pk': pk},
            follow=True
        )
        self.assertRedirects(
            response=response,
            expected_url=reverse('ml:index'),
            status_code=302,
            target_status_code=200
        )
        remove_uploaded_file()


class TrainViewTests(TestCase):

    def test_get_redirection(self):
        client = Client()
        client.force_login(User.objects.get_or_create(username='test_user')[0])
        response = client.get(
            path=reverse('ml:train'),
            follow=True
        )
        self.assertRedirects(
            response=response,
            expected_url=reverse('ml:index'),
            status_code=302,
            target_status_code=200
        )
