from fastapi import FastAPI
import uvicorn

from typing import List
import socket
import whois
from datetime import datetime

from db_helper import DBHelper
from logger import setup_logger


logger = setup_logger(__name__)
app = FastAPI()
db = DBHelper('cyberok.sqlite', logger)


@app.post('/get_domains_by_ips/')
async def get_domains_by_ips(ips: List[str]):
    logger.info(f'request to /get_domains_by_ips/, len of ips: {len(ips)}')

    domains = []
    
    for ip in ips:
        try:
            dmn = socket.gethostbyaddr(ip)
            domains.append(dmn[0])
        except socket.herror:
            domains.append(None)
    
    return domains


@app.post('/get_ips_by_fqdns/')
async def get_ips_by_fqdns(fqdns: List[str]):
    logger.info(f'request to /get_ips_by_fqdns/, len of fqdns: {len(fqdns)}')

    ips = []

    for fqdn in fqdns:
        ip = db.get_ip(fqdn)

        if not ip:
            try:
                ip = socket.gethostbyname(fqdn)
            except socket.gaierror:
                ip = None
            db.save_ip(fqdn, ip)

        ips.append(ip)

    return ips


def datetime_to_str(obj: List[datetime] | datetime):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    elif isinstance(obj, list):
        lst = []

        for d in obj:
            lst.append(d.strftime('%Y-%m-%dT%H:%M:%S'))

        return lst
    else:
        raise TypeError('Invalid type of obj! It must to be \
                        List[datetime] | datetime')


@app.post('/get_whois_info/')
async def get_whois_info(domains: List[str]):
    logger.info(f'request to /get_whois_info/, len of domains: {len(domains)}')

    ans = []

    for dmn in domains:
        dct = db.get_whois(dmn)

        if not dct:
            info = whois.whois(dmn)

            dct = {
                'registrar': info.registrar,
                'creation_date': datetime_to_str(info.creation_date),
                'expiration_date': datetime_to_str(info.expiration_date),
                'name_servers': info.name_servers,
                'name': info.name,
            }
            db.save_whois(dmn, dct)

        ans.append(dct)
    
    return ans


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
