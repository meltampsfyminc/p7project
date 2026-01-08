
from django.test import TestCase
from django.urls import reverse
from .models import Item
from django.contrib.auth.models import User

class KagamitanViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.item = Item.objects.create(name='Test Item', quantity=1, unit_price=100)

    def test_item_list_view(self):
        response = self.client.get(reverse('kagamitan:item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')
        self.assertTemplateUsed(response, 'kagamitan/item_list.html')

    def test_item_detail_view(self):
        response = self.client.get(reverse('kagamitan:item_detail', args=[self.item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')
        self.assertTemplateUsed(response, 'kagamitan/item_detail.html')

    def test_item_create_view(self):
        response = self.client.post(reverse('kagamitan:item_create'), {
            'name': 'New Item',
            'quantity': 2,
            'unit_price': 50
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Item.objects.filter(name='New Item').exists())

    def test_item_update_view(self):
        response = self.client.post(reverse('kagamitan:item_update', args=[self.item.pk]), {
            'name': 'Updated Item',
            'quantity': 1,
            'unit_price': 100
        })
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, 'Updated Item')

    def test_item_delete_view(self):
        response = self.client.post(reverse('kagamitan:item_delete', args=[self.item.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Item.objects.filter(pk=self.item.pk).exists())

    def test_kagamitan_csv_upload_view(self):
        response = self.client.get(reverse('kagamitan:kagamitan_csv_upload'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kagamitan/kagamitan_csv_upload.html')

    def test_item_list_by_category_view(self):
        self.item.location = 'Test Category'
        self.item.save()
        response = self.client.get(reverse('kagamitan:item_list_by_category', args=['Test Category']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')
        self.assertTemplateUsed(response, 'kagamitan/item_list.html')
