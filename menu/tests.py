from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from branches.models import Branch

from .models import Category, MenuItem


class MenuModelTests(TestCase):
    def setUp(self):
        self.a = Branch.objects.create(name="A", city="x")
        self.b = Branch.objects.create(name="B", city="y")

    def test_same_category_name_allowed_in_different_branches(self):
        Category.objects.create(branch=self.a, name="مشويات")
        Category.objects.create(branch=self.b, name="مشويات")  # ما يفشل

    def test_duplicate_category_in_same_branch_rejected(self):
        Category.objects.create(branch=self.a, name="Drinks")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Category.objects.create(branch=self.a, name="drinks")

    def test_negative_price_rejected(self):
        cat = Category.objects.create(branch=self.a, name="x")
        item = MenuItem(category=cat, name="طبق", price=Decimal("-1"))
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_item_branch_comes_from_category(self):
        cat = Category.objects.create(branch=self.a, name="x")
        item = MenuItem.objects.create(category=cat, name="طبق", price=Decimal("1000"))
        self.assertEqual(item.branch, self.a)

    def test_category_with_items_cannot_be_deleted(self):
        from django.db.models import ProtectedError

        cat = Category.objects.create(branch=self.a, name="x")
        MenuItem.objects.create(category=cat, name="طبق", price=Decimal("1000"))
        with self.assertRaises(ProtectedError):
            cat.delete()
