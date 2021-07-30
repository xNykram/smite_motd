import unittest
import pymssql

class DatabaseTest(unittest.TestCase):
    pass

if __name__ == '__main__':
    server = '51.68.140.249'
    db = 'smiteAPI'
    login = 'smiteAPI'
    passwd = 'smiteapi684'
    conn = pymssql.connect(server, login, passwd, db)
    
    unittest.main()
