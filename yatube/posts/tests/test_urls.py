from django.test import Client, TestCase
from ..models import Group, Post, User


class PostURLTests(TestCase):
    succes = 200

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
        )

    def setUp(self):
        self.guest_client = Client()  # Создаем неавторизованный клиент
        self.authorized_client = Client()  # Создаем второй клиент
        self.authorized_client.force_login(PostURLTests.author)

    def test_posts_for_guest(self):
        responses = {
            '/': self.succes,
            '/group/test-slug/': self.succes,
            '/profile/HasNoName/': self.succes,
            f'/posts/{self.post.pk}/': self.succes,
        }
        for adress in responses:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, self.succes)

    def test_posts_create_for_auth(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, self.succes)

    def test_posts_edit_for_author(self):
        """Страница /posts/<post_id>/edit/ доступна только авторизованному
        пользователю."""
        self.author = User.objects.get(username=self.author)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, self.succes)

    def test_posts_create_redirect_for_guest(self):
        """Страница /create/ перенаправляет неавторизованного пользователя."""
        response = self.guest_client.get('/create/')
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_posts_edit_redirect_for_guest(self):
        """Страница /posts/<post_id>/edit перенаправляет неавторизованного
        пользователя."""
        response = self.guest_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.pk}/edit/'
        )

    def test_unexisting_page(self):
        """Страница /unexisting_page/ должна выдать ошибку."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            f"/group/{self.group.slug}/": "posts/group_list.html",
            f"/profile/{self.author.username}/": "posts/profile.html",
            f"/posts/{self.post.id}/": "posts/post_detail.html",
            f"/posts/{self.post.id}/edit/": "posts/create_post.html",
            "/create/": "posts/create_post.html",
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
