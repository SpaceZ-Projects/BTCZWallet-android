
import os
import sqlite3

from toga import App



class TxsStorage:
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        if not os.path.exists(self.app.paths.data):
            os.makedirs(self.app.paths.data)
        self.data = os.path.join(self.app.paths.data, 'transactions.dat')


    def create_transactions_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS transactions (
                type TEXT,
                category TEXT,
                address TEXT,
                txid TEXT,
                amount REAL,
                blocks INTEGER,
                fee REAL,
                timestamp INTEGER
            )
            '''
        )
        conn.commit()
        conn.close()


    def insert_transaction(self, tx_type, category, address, txid, amount, blocks, fee, timestamp):
        print(blocks)
        self.create_transactions_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO transactions (type, category, address, txid, amount, blocks, fee, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', 
            (tx_type, category, address, txid, amount, blocks, fee, timestamp)
        )
        conn.commit()
        conn.close()


    def get_transaction(self, txid):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM transactions WHERE txid = ?',
                (txid,)
            )
            transaction = cursor.fetchone()
            conn.close()
            return transaction
        except sqlite3.OperationalError:
            return []
        

    def get_transactions(self, option = None):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            if option:
                cursor.execute(
                    'SELECT txid FROM transactions'
                )
                transactions = [row[0] for row in cursor.fetchall()]
            else:
                cursor.execute('SELECT * FROM transactions')
                transactions = cursor.fetchall()
            conn.close()
            return transactions
        except sqlite3.OperationalError:
            return []



class WalletStorage:
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        if not os.path.exists(self.app.paths.data):
            os.makedirs(self.app.paths.data)
        self.data = os.path.join(self.app.paths.data, 'wallet.dat')


    def create_addresses_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS addresses (
                taddress TEXT,
                zaddress TEXT,
                tbalance REAL,
                zbalance REAL
            )
            '''
        )
        conn.commit()
        conn.close()


    def insert_addresses(self, taddress, zaddress, tbalance, zbalance):
        self.create_addresses_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO addresses (taddress, zaddress, tbalance, zbalance)
            VALUES (?, ?, ?, ?)
            ''', 
            (taddress, zaddress, tbalance, zbalance)
        )
        conn.commit()
        conn.close()

    
    def get_addresses(self, address_type = None, balance = None):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            if address_type == "transparent":
                if balance:
                    cursor.execute('SELECT taddress, tbalance FROM addresses')
                else:
                    cursor.execute('SELECT taddress FROM addresses')
                data = cursor.fetchone()
            elif address_type == "shielded":
                if balance:
                    cursor.execute('SELECT zaddress, zbalance FROM addresses')
                else:
                    cursor.execute('SELECT zaddress FROM addresses')
                data = cursor.fetchone()
            else:
                cursor.execute('SELECT * FROM addresses')
                data = cursor.fetchall()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return []
        
    
    def update_balances(self, tbalance, zbalance):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE addresses
            SET tbalance = ?, zbalance = ?
            ''', (tbalance, zbalance)
        )
        conn.commit()
        conn.close()



class DeviceStorage:
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        if not os.path.exists(self.app.paths.data):
            os.makedirs(self.app.paths.data)
        self.data = os.path.join(self.app.paths.data, 'device.dat')


    def create_auth_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS mobile_auth (
                hostname TEXT,
                id TEXT,
                secret_key TEXT
            )
            '''
        )
        conn.commit()
        conn.close()


    def insert_auth(self, hostname, id, secret):
        self.create_auth_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO mobile_auth (hostname, id, secret_key)
            VALUES (?, ?, ?)
            ''', 
            (hostname, id, secret)
        )
        conn.commit()
        conn.close()


    def get_auth(self):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM mobile_auth')
            data = cursor.fetchone()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return None