"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app, delete_account
from service import talisman

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"

HTTPS_ENVIRON = {'wsgi.url_scheme': 'https'}


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)
        talisman.force_https = False

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ADD YOUR TEST CASES HERE ...
    def test_read_account(self):
        """ It should get an account data from database """
        # We firstly create an account in the database
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        savedAccount = response.get_json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Then we try to read it back and compare values
        response2 = self.client.get("/accounts/" + str(savedAccount["id"]))
        accountDB = response2.get_json()
        self.assertEqual(account.name, accountDB["name"])
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Now we search for non existent account
        response3 = self.client.get("/accounts/100")
        self.assertEqual(response3.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_account(self):
        """ It should update an account already saved in the database """
        # We firstly create an account in the database
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        savedAccount = response.get_json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Then we try to update its values
        account.name = "Georges"
        account.address = "Bonanjo Centre des affaires maritimes IGH BP 1588 Douala"
        account.email = "nguimbouseffa@yahoo.fr"
        response2 = self.client.put(
            BASE_URL+"/" + str(savedAccount["id"]),
            json=account.serialize(),
            content_type="application/json"
        )
        accountDB = response2.get_json()
        self.assertEqual(accountDB["name"], "Georges")
        self.assertEqual(accountDB["email"], "nguimbouseffa@yahoo.fr")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Now we search for non existent account
        response3 = self.client.get("/accounts/0")
        returned_data = response3.get_json()
        # self.assertRaises(ValueError, update_account, 1)
        self.assertEqual(response3.status_code, status.HTTP_404_NOT_FOUND)

    def test_account_not_found(self):
        """ It should check if not founded account is well handled """      
        response = self.client.get("/accounts/0")
        accountDB = response.get_json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_account(self):
        """ It should delete an account data from database """
        # We firstly create an account in the database      
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        savedAccount = response.get_json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Then we try to read it back and delete it 
        response2 = self.client.delete(
            BASE_URL + "/" + str(savedAccount["id"]),
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertRaises(ValueError, delete_account, savedAccount["id"])
        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_all_accounts(self):
        """ It should get HTTP_200_OK from all accounts as a list or dict """
        response = self.client.get("/accounts")
        accounts = response.get_json()
        # Testing for no accounts in database
        self.assertEqual(accounts, [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._create_accounts(5)
        response2 = self.client.get("/accounts")
        accounts = response2.get_json()

        # Testing for 5 accounts added in database and returned in list or dict
        self.assertEqual(len(accounts), 5)
    
    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        response = self.client.delete(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_web_security_headers(self):
        """ Calls the root URL passing in environ_overrides=HTTPS_ENVIRON as param """
        response = self.client.get("/", environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers.get("X-Frame-Options"), "SAMEORIGIN")
        self.assertEqual(response.headers.get("X-XSS-Protection"), "1; mode=block")
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("Content-Security-Policy"), "default-src \'self\'; object-src \'none\'")
        self.assertEqual(response.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")

    def test_web_security_origin(self):
        """ Tests Flask Cors calling the root URL passing in environ_overrides=HTTPS_ENVIRON as param """
        response = self.client.get("/", environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "*")
