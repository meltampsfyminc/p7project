from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
import unittest

class NationalMenuTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

    def test_gusali_list_loads(self):
        response = self.client.get(reverse('gusali:building_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gusali/building_list.html')

    def test_lupa_list_loads(self):
        response = self.client.get(reverse('lupa:land_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lupa/land_list.html')

    def test_plants_list_loads(self):
        response = self.client.get(reverse('plants:plant_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plants/plant_list.html')

    def test_kagamitan_list_loads(self):
        response = self.client.get(reverse('kagamitan:item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kagamitan/item_list.html')

    def test_vehicles_list_loads(self):
        # Allow failure if app not yet ready
        try:
            url = reverse('vehicles:vehicle_list')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'vehicles/vehicle_list.html')
        except Exception as e:
            self.fail(f"Vehicles list failed: {e}")

    def test_gusali_search(self):
        response = self.client.get(reverse('gusali:building_list'), {'q': 'test'})
        self.assertEqual(response.status_code, 200)

    def test_lupa_search(self):
        response = self.client.get(reverse('lupa:land_list'), {'q': 'test'})
        self.assertEqual(response.status_code, 200)
