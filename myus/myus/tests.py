from http import HTTPStatus

from django.urls import reverse
from django.test import TestCase

from myus.models import Hunt, Puzzle

class TestViewHunt(TestCase):
    """ Test the view_hunt endpoint

    The tests related to the handling of URLs with IDs and slugs should be taken as general tests for the redirect_from_hunt_id_to_hunt_id_and_slug decorator
    """

    def setUp(self):
        self.hunt = Hunt.objects.create(name="Test Hunt", slug="test-hunt")
        self.view_name = "view_hunt"

    def test_view_hunt_with_id_and_slug_success(self):
        """ Visiting the view_hunt endpoint with both ID and slug in the URL displays the requested page """
        res = self.client.get(reverse(self.view_name, args=[self.hunt.id, self.hunt.slug]))
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "view_hunt.html")

    def test_view_hunt_with_id_only_redirects_to_id_and_slug(self):
        """ Visiting the view_hunt endpoint with only ID in the URL redirects to the URL with ID and slug """
        res = self.client.get(reverse(self.view_name, args=[self.hunt.id]))
        self.assertRedirects(res, reverse(self.view_name, args=[self.hunt.id, self.hunt.slug]))

    def test_view_hunt_with_id_and_wrong_slug_redirects_to_id_and_correct_slug(self):
        """ Visiting the view_hunt endpoint with ID and the wrong slug in URL redirects to URL with ID and correct slug """
        res = self.client.get(reverse(self.view_name, args=[self.hunt.id, "the-wrong-slug"]))
        self.assertRedirects(res, reverse(self.view_name, args=[self.hunt.id, self.hunt.slug]))


class TestViewPuzzle(TestCase):
    """ Test the view_puzzle endpoint

    The tests related to the handling of URLs with IDs and slugs should be taken as general tests for the force_url_to_include_both_hunt_and_puzzle_slugs decorator
    """
    def setUp(self):
        self.hunt = Hunt.objects.create(name="Test Hunt", slug="test-hunt")
        self.puzzle = Puzzle.objects.create(name="Test Puzzle", slug="test-puzzle", hunt=self.hunt)
        self.view_name = "view_puzzle"
        self.correct_url = reverse(self.view_name, args=[self.hunt.id, self.hunt.slug, self.puzzle.id, self.puzzle.slug])

    def test_view_puzzle_with_ids_and_slugs_success(self):
        """ Visiting the view_puzzle endpoint with hunt and puzzle IDs and slug in the URL displays the requested page """
        res = self.client.get(self.correct_url)
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(res, "view_puzzle.html")

    def test_view_puzzle_with_no_hunt_slug_redirects_to_full_url(self):
        """ Visiting the view_puzzle endpoint with no hunt_slug in the URL redirects to the full URL """
        res = self.client.get(reverse(self.view_name, args=[self.hunt.id, self.puzzle.id, self.puzzle.slug]))
        self.assertRedirects(res, self.correct_url)

    def test_view_puzzle_with_no_puzzle_slug_redirects_to_full_url(self):
        """ Visiting the view_puzzle endpoint with no puzzle_slug in the URL redirects to the full URL """
        res = self.client.get(reverse(self.view_name, args=[self.hunt.id, self.hunt.slug, self.puzzle.id]))
        self.assertRedirects(res, self.correct_url)

    def test_view_puzzle_with_no_hunt_or_puzzle_slug_redirects_to_full_url(self):
        """ Visiting the view_puzzle endpoint with no hunt_slug or puzzle_slug in the URL redirects to the full URL """
        res = self.client.get(reverse(self.view_name, args=[self.hunt.id, self.puzzle.id]))
        self.assertRedirects(res, self.correct_url)

    def test_view_puzzle_with_ids_and_wrong_slugs_redirects_to_ids_and_correct_slugs(self):
        """ Visiting the view_puzzle endpoint with IDs and the wrong slugs in URL redirects to URL with IDs and correct slugs """
        res = self.client.get(reverse(self.view_name, args=[self.hunt.id, "wrong-hunt-slug", self.puzzle.id, "wrong-puzzle-slug"]))
        self.assertRedirects(res, self.correct_url)
