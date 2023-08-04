import sqlite3
import json

import utils


def __singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@__singleton
class DBHelper:

    def __init__(self, path: str, logger=None) -> None:
        self.logger = logger
        self.connected = False
        self.connect(path)

    def connect(self, path):
        if self.connected:
            return
        
        try:
            self.__con = sqlite3.connect(path)
            self.__cur = self.__con.cursor()
            self.connected = True
            self.logger.info('New connection to database')
            self.init_tables()
        except sqlite3.Error:
            self.logger.error(f'Error connecting to database')
    
    def close(self):
        self.__con.close()
        self.connected = False
        self.logger.info('Database connection closed')
    
    def init_tables(self) -> None:
        whois_table = '''
CREATE TABLE IF NOT EXISTS whois (
    id INTEGER PRIMARY KEY,
    domain TEXT,
    value TEXT
)
'''
        self.__cur.execute(whois_table)
        
        fqdn_ip_table = '''
CREATE TABLE IF NOT EXISTS fqdn_ip (
    id INTEGER PRIMARY KEY,
    fqdn TEXT,
    ip TEXT
)
'''
        self.__cur.execute(fqdn_ip_table)
        self.__con.commit()
        self.logger.info('Tables are initialized (or already existed)')
    
    # whois
    def get_whois(self, dmn: str) -> dict:
        res = self.__cur.execute(f'SELECT value FROM whois WHERE domain="{dmn}"')
        val = res.fetchone()

        if val:
            return json.loads(val[0])
        else:
            return None

    def save_whois(self, dmn: str, dct: dict) -> None:
        val = json.dumps(dct)
        self.__cur.execute(f'''
INSERT INTO whois (domain, value) VALUES ('{dmn}', '{val}')
''')
        self.__con.commit()

    def update_whois(self, dmn: str, dct: dict, commit: bool = False) -> None:
        val = json.dumps(dct)
        self.__cur.execute(f'''
UPDATE whois SET value='{val}' WHERE domain='{dmn}'
''')
        if commit:
            self.__con.commit()

    # FQDN & ip
    def get_ip(self, fqdn) -> str:
        res = self.__cur.execute(f'SELECT ip FROM fqdn_ip WHERE fqdn="{fqdn}"')
        ans = res.fetchone()

        if ans:
            return ans[0]
        else:
            return None
    
    def save_ip(self, fqdn: str, ip: str) -> None:
        self.__cur.execute(f'INSERT INTO fqdn_ip (fqdn, ip) \
                           VALUES ("{fqdn}", "{ip}")')
        self.__con.commit()
    
    def update_ip(self, fqdn:str, ip: str, commit: bool=True) -> None:
        self.__cur.execute(f'UPDATE fqdn_ip SET ip="{ip}" WHERE fqdn="{fqdn}"')
        if commit:
            self.__con.commit()

    def update_db(self):
        # updating 'fqdn_ip' table
        res = self.__cur.execute(f'SELECT fqdn FROM fqdn_ip')
        fqdns = list(map(lambda it: it[0], res.fetchall()))

        for fqdn in fqdns:
            self.update_ip(fqdn, utils.get_ip_by_fqdn(fqdn), False)
        
        self.logger.info(f'{len(fqdns)} rows updated in fqdn_ip')

        # updating 'whois' table
        res = self.__cur.execute(f'SELECT domain FROM whois')
        domains = list(map(lambda it: it[0], res.fetchall()))

        for dmn in domains:
            self.update_whois(dmn, utils.get_whois_info(dmn), False)
        
        self.logger.info(f'{len(domains)} rows updated in whois')
        
        self.__con.commit()
