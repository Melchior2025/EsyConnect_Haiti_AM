# -*- coding: utf-8 -*-
"""Automated tests for the Business Detail page.

These tests cover:
1. Rendering of the Leaflet map when coordinates are present.
2. Fallback message when coordinates are missing.
3. Review form submission (rating + comment) handling, including validation.
4. Click‑tracking AJAX endpoints for WhatsApp and phone calls.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Business, Review

User = get_user_model()

class BusinessDetailTests(TestCase):
    def setUp(self):
        # Create a user and a business with full data
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.business = Business.objects.create(
            name='Test Business',
            category=None,
            address='123 Rue Test',
            phone='50912345678',
            latitude='12.34',
            longitude='-56.78',
            is_active=True,
        )
        self.client = Client()

    def test_map_shows_when_coordinates_present(self):
        """The detail template should contain a Leaflet container when latitude & longitude exist."""
        response = self.client.get(reverse('business:business_detail', kwargs={'business_id': self.business.id}))
        self.assertEqual(response.status_code, 200)
        # Look for the div with id "map" which is added by the JS script
        self.assertContains(response, 'id="map"', html=False)
        # Ensure the JS initialisation script receives the coordinates
        self.assertContains(response, f"{{'lat': {self.business.latitude}, 'lng': {self.business.longitude}}}", html=False)

    def test_fallback_message_when_no_coordinates(self):
        """If a business has no lat/lon, the template should render the fallback text."""
        self.business.latitude = None
        self.business.longitude = None
        self.business.save()
        response = self.client.get(reverse('business:business_detail', kwargs={'business_id': self.business.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'coordinates unavailable', msg_prefix='Fallback message missing')

    def test_review_form_successful_submission(self):
        """Submitting a valid review should create a Review instance and return a success message."""
        self.client.login(username='testuser', password='testpass')
        post_data = {
            'rating': 5,
            'comment': 'Excellent service!',
        }
        response = self.client.post(
            reverse('business:business_detail', kwargs={'business_id': self.business.id}),
            data=post_data,
            follow=True,
        )
        # The view redirects back to the same page on success
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Review.objects.filter(business=self.business, user=self.user).exists())
        self.assertContains(response, 'Merci', msg_prefix='Success toast/message not found')

    def test_review_form_missing_rating(self):
        """Submitting without a rating should display an error message and not create a Review."""
        self.client.login(username='testuser', password='testpass')
        post_data = {
            'comment': 'Missing rating',
        }
        response = self.client.post(
            reverse('business:business_detail', kwargs={'business_id': self.business.id}),
            data=post_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.filter(business=self.business, user=self.user).exists())
        self.assertContains(response, 'Veuillez choisir une note', msg_prefix='Error message missing')

    def test_ajax_track_click_whatsapp(self):
        """POST to the track_click endpoint for WhatsApp should increment the counter."""
        initial = self.business.whatsapp_clicks or 0
        url = reverse('business:track_click', kwargs={'business_id': self.business.id, 'action_type': 'whatsapp'})
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.business.refresh_from_db()
        self.assertEqual(self.business.whatsapp_clicks, initial + 1)

    def test_ajax_track_click_call(self):
        """POST to the track_click endpoint for a phone call should increment the counter."""
        initial = self.business.call_count or 0
        url = reverse('business:track_click', kwargs={'business_id': self.business.id, 'action_type': 'call'})
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.business.refresh_from_db()
        self.assertEqual(self.business.call_count, initial + 1)
