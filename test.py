import os
import unittest

import main
from parse  import parse_query

class MainTestCase(unittest.TestCase):

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
        assertTrue(  rv.status_code == 200 )
    
    def test_simple_parse(self):
        search = parse_query('Toyota Tacoma')
        assertTrue ( search.make == 'Toyota' )
        assertTrue ( search.model == 'Tacoma')
    
    def test_price_parse(self):
        search = parse_query('2000 to 2004 Toyota Tacoma under $9000.00 within 100 miles')
        assertTrue( search.make == 'Toyota')
        assertTrue( search.model == 'Tacoma')
        assertTrue('blue' in search.colors )
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()