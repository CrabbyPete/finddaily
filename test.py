import os
import main
import unittest
import tempfile

class TestCase(unittest.TestCase):

    def setUp(self):
        main.app.config['TESTING'] = True
        self.app = main.app.test_client()

    def signin(self, username, password):
        return self.app.post('/signin', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)


    def test_login_logout(self):
        rv = self.signin('peted','drd00m')
        assert 'My Account' in rv.data
    
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
