import os
import unittest
from urllib.parse import urlencode
import uuid

from server import make_app, add_user, delete_user


class TestApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tearDownClass()
        app = make_app(db_path="test.db")
        app.testing = True
        cls.app = app

    @classmethod
    def tearDownClass(cls):
        if os.path.exists("test.db"):
            os.remove("test.db")

    def setUp(self):
        with self.app.app_context():
            add_user('jaidev', 'deshpande')
            add_user('IIT', 'Madras')
        self.machine_id = str(uuid.uuid4())

    def tearDown(self):
        with self.app.app_context():
            delete_user('jaidev')
            delete_user('IIT')

    def login(self, **kwargs):
        with self.app.test_client() as client:
            resp = client.get('/check', headers={'SEEK-CUSTOM-AUTH': urlencode(kwargs)})
        return resp

    def test_valid_login(self):
        """Check if a valid user can login."""
        resp = self.login(username='jaidev', password='deshpande', machine_id=self.machine_id)
        assert resp.status_code == 200
        assert resp.status == '200 OK'

    def test_invalid_machine_id_password(self):
        """Ensure that only valid machine_ids and passwords are used."""
        # Add a valid user first
        self.login(username='jaidev', password='deshpande', machine_id=self.machine_id)
        # Check if the same user can login with a fake machine ID
        resp = self.login(username='jaidev', password='deshpande', machine_id="foobar")
        assert resp.status_code == 401
        assert resp.status == '401 UNAUTHORIZED'

        # Or with a fake password
        resp = self.login(username='jaidev', password='foobar', machine_id=self.machine_id)
        assert resp.status_code == 401
        assert resp.status == '401 UNAUTHORIZED'

    def test_spoof_machine_id(self):
        """Check if a user with an invalid machine ID is blocked."""
        # Add a valid user first
        self.login(username='jaidev', password='deshpande', machine_id=self.machine_id)
        # Then add someone with the same machine ID
        resp = self.login(username='IIT', password='Madras', machine_id=self.machine_id)

        assert resp.status_code == 401
        assert resp.status == '401 UNAUTHORIZED'

    def test_bad_request(self):
        """Check if a bad request is handled."""
        resp = self.login(username='jaidev', password='deshpande')
        assert resp.status_code == 400
        assert resp.status == '400 BAD REQUEST'


if __name__ == "__main__":
    unittest.main()
