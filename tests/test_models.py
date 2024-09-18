# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """ It should retrieve all information about an existing product """
        # Create and save a new product
        product = ProductFactory()
        product.id = None
        product.create()

        # Ensure that new product id is present
        self.assertIsNotNone(product.id)

        # Fetch the product back from the database
        fetch = Product.find(product.id)

        # Ensure that fetch product's properties are correct
        self.assertEqual(fetch.id, product.id)
        self.assertEqual(fetch.name, product.name)
        self.assertEqual(fetch.price, product.price)
        self.assertEqual(fetch.description, product.description)
        self.assertEqual(fetch.category, product.category)

    def test_update_a_product(self):
        """ It should update an existing product """
        # Create and save a new product
        product = ProductFactory()
        product.id = None
        product.create()

        # Update the new product description
        original_id = product.id
        product.description = "new_description"
        product.update()

        # Check if the updated product has the same id of the original
        self.assertEqual(product.id, original_id)

        # Check if there's only one product in the database
        products = Product.all()
        self.assertEqual(len(products), 1)

        # Check if the new product has been updated successfully
        updated_product = products[0]
        self.assertEqual(updated_product.id, product.id)
        self.assertEqual(updated_product.description, "new_description")

    def test_delete_a_product(self):
        """ It should delete an existing product """
        # Create and save a new product in the database
        new_product = ProductFactory()
        new_product.create()

        # Check if there is only one product before deleting
        self.assertEqual(len(Product.all()), 1)

        # Delete the product from the database
        new_product.delete()

        # Check if the product has been removed from the database
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """ It should return all existing products """
        # Check if the database has initially zero products
        products = Product.all()
        self.assertEqual(len(products), 0)

        # Create and save five products in the database
        for _ in range(5):
            product = ProductFactory()
            product.create()

        # Check if 5 products are added to the database
        self.assertEqual(len(Product.all()), 5)

    def test_find_product_by_name(self):
        """It should find a product by its name"""
        # Create and save a batch of 5 products
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()

        # Store the first product's name
        name = products[0].name

        # count products with the same name as the first product
        count = len([product for product in products if product.name == name])

        # Search products with the same name as the first product in the database
        occurrences = Product.find_by_name(name)

        # Check if the occurrences has the same count
        self.assertEqual(occurrences.count(), count)

        # Check if each occurrence has the same name as th0e first product
        for product in occurrences:
            self.assertEqual(product.name, name)

    def test_find_product_by_availability(self):
        """ It should find products by their availability """
        # Create and save a batch of 10 products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        # Retrieve the first name's availability
        available = products[0].available

        # Count the number of occurrences which
        # have the same availability as the first product
        count = len([product for product in products if product.available == available])

        # Check if all occurrences from the database
        # have the same count as the previous occurrences
        occurrences = Product.find_by_availability(available)
        self.assertEqual(occurrences.count(), count)

        # Check if all occurrences from the database
        # have the same availability as the first product
        for occurrence in occurrences:
            self.assertEqual(occurrence.available, available)

    def test_find_product_by_category(self):
        """ It should find products by a category """
        # Create and save a batch of 10 products in the database
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        # Retrieve the category of the first product in the products list
        category = products[0].category

        # Count the number of occurrences of the product that
        # have the same category in the list
        count = len([product for product in products if product.category == category])

        # Check if the founds products matches the expected count
        occurrences = Product.find_by_category(category)
        self.assertEqual(occurrences.count(), count)

        # Check if each occurrence is the same category
        for occurrence in occurrences:
            self.assertEqual(occurrence.category, category)