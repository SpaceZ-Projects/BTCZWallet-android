
import os
import sqlite3

from toga import App



class AddressesStorage:
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        if not os.path.exists(self.app.paths.data):
            os.makedirs(self.app.paths.data)
        self.data = os.path.join(self.app.paths.data, 'addresses.dat')


    def create_address_book_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS address_book (
                name TEXT,
                address TEXT
            )
            '''
        )
        conn.commit()
        conn.close()


    def insert_book(self, name, address):
        self.create_address_book_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO address_book (name, address)
            VALUES (?, ?)
            ''', 
            (name, address)
        )
        conn.commit()
        conn.close()


    def get_address_book(self, option=None, name = None):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            if name:
                cursor.execute(
                    'SELECT address FROM address_book WHERE name = ?',
                    (name,)
                )
                address = cursor.fetchone()
                conn.close()
                return address
            
            if option == "address":
                cursor.execute('SELECT address FROM address_book')
                addresses = [row[0] for row in cursor.fetchall()]
            elif option == "name":
                cursor.execute('SELECT name FROM address_book')
                addresses = [row[0] for row in cursor.fetchall()]
            else:
                cursor.execute('SELECT * FROM address_book')
                addresses = cursor.fetchall()
            conn.close()
            return addresses
        except sqlite3.OperationalError:
            return []
        

    def delete_address_book(self, address):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                '''
                DELETE FROM address_book WHERE address = ?
                ''', 
                (address,)
            )
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Error deleting item: {e}")



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
            return None
        

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
        
    
    def update_transaction(self, txid, blocks):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE transactions
            SET blocks = ? WHERE txid = ?
            ''', (blocks, txid)
        )
        conn.commit()
        conn.close()



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

    
    def create_server_info_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS server_info (
                height INTEGER,
                currency TEXT,
                price REAL
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


    def insert_info(self, height, currency, price):
        self.create_server_info_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO server_info (height, currency, price)
            VALUES (?, ?, ?)
            ''', 
            (height, currency, price)
        )
        conn.commit()
        conn.close()


    def get_info(self, value = None):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            if value:
                cursor.execute(f'SELECT {value} FROM server_info')
            else:
                cursor.execute(f'SELECT * FROM server_info')
            data = cursor.fetchone()
            conn.close()
            return data
        except sqlite3.OperationalError:
            return None

    
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


    def update_info(self, height, currency, price):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE server_info
            SET height = ?, currency = ?, price = ?
            ''', (height, currency, price)
        )
        conn.commit()
        conn.close()



class MessagesStorage:
    def __init__(self, app:App):
        super().__init__()

        self.app = app
        if not os.path.exists(self.app.paths.data):
            os.makedirs(self.app.paths.data)
        self.data = os.path.join(self.app.paths.data, 'messages.dat')


    def create_identity_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS identity (
                address TEXT
            )
            '''
        )
        conn.commit()
        conn.close()


    def create_contacts_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS contacts (
                category TEXT,
                contact_id TEXT,
                username TEXT
            )
            '''
        )
        conn.commit()
        conn.close()


    def create_pending_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS pending (
                category TEXT,
                id TEXT,
                username TEXT
            )
            '''
        )
        conn.commit()
        conn.close()


    def create_messages_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT,
                author TEXT,
                message TEXT,
                amount REAL,
                timestamp INTEGER
            )
            '''
        )
        conn.commit()
        conn.close()

    def create_unread_messages_table(self):
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS unread_messages (
                id TEXT,
                author TEXT,
                message TEXT,
                amount REAL,
                timestamp INTEGER
            )
            '''
        )
        conn.commit()
        conn.close()


    def insert_identity(self, address):
        self.create_identity_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO identity (address)
            VALUES (?)
            ''', 
            (address,)
        )
        conn.commit()
        conn.close()


    def get_identity(self):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute('SELECT address FROM identity')
            data = cursor.fetchone()
            conn.close()
            return data[0]
        except sqlite3.OperationalError:
            return None
        

    def add_contact(self, category, contact_id, username):
        self.create_contacts_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO contacts (category, contact_id, username)
            VALUES (?, ?, ?)
            ''',
            (category, contact_id, username)
        )
        conn.commit()
        conn.close()


    def add_pending(self, category, id, username):
        self.create_pending_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO pending (category, id, username)
            VALUES (?, ?, ?)
            ''',
            (category, id, username)
        )
        conn.commit()
        conn.close()


    def message(self, id, author, message, amount, timestamp):
        self.create_messages_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO messages (id, author, message, amount, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ''', 
            (id, author, message, amount, timestamp)
        )
        conn.commit()
        conn.close()


    def unread_message(self, id, author, message, amount, timestamp):
        self.create_unread_messages_table()
        conn = sqlite3.connect(self.data)
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO unread_messages (id, author, message, amount, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ''', 
            (id, author, message, amount, timestamp)
        )
        conn.commit()
        conn.close()


    def get_contacts(self, option = None):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            if option == "contact_id":
                cursor.execute('SELECT contact_id FROM contacts')
                contacts = [row[0] for row in cursor.fetchall()]
            elif option is None:
                cursor.execute('SELECT * FROM contacts')
                contacts = cursor.fetchall()
            conn.close()
            return contacts
        except sqlite3.OperationalError:
            return []
        

    def get_pending(self, option = None):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            if option == "id":
                cursor.execute("SELECT id FROM pending")
                contacts = [row[0] for row in cursor.fetchall()]
            elif option is None:
                cursor.execute('SELECT * FROM pending')
                contacts = cursor.fetchall()
            conn.close()
            return contacts
        except sqlite3.OperationalError:
            return []
        

    def get_messages(self, contact_id = None):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            if contact_id:
                cursor.execute(
                    'SELECT author, message, amount, timestamp FROM messages WHERE id = ?',
                    (contact_id,)
                )
                messages = cursor.fetchall()
            else:
                cursor.execute('SELECT timestamp FROM messages')
                messages = [row[0] for row in cursor.fetchall()]
            conn.close()
            return messages
        except sqlite3.OperationalError:
            return []
        

    def get_unread_messages(self, contact_id=None):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            if contact_id:
                cursor.execute(
                    'SELECT author, message, amount, timestamp FROM unread_messages WHERE id = ?',
                    (contact_id,)
                )
                messages = cursor.fetchall()
            else:
                cursor.execute('SELECT timestamp FROM unread_messages')
                messages = [row[0] for row in cursor.fetchall()]
            conn.close()
            return messages
        except sqlite3.OperationalError:
            return []


    def delete_contact(self, contact_id):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                '''
                DELETE FROM contacts WHERE contact_id = ?
                ''', 
                (contact_id,)
            )
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Error deleting contact: {e}")


    def delete_pending(self, id):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                '''
                DELETE FROM pending WHERE id = ?
                ''', 
                (id,)
            )
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Error deleting pending contact: {e}")


    def delete_unread(self, contact_id):
        try:
            conn = sqlite3.connect(self.data)
            cursor = conn.cursor()
            cursor.execute(
                '''
                DELETE FROM unread_messages WHERE id = ?
                ''', 
                (contact_id,)
            )
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Error deleting request: {e}")



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