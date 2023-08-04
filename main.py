from fastapi import FastAPI, Body
import uvicorn
from typing import List

import socket
import whois
import signal
from datetime import datetime

from db_helper import DBHelper


app = FastAPI()
db = DBHelper('cyberok.sqlite')


@app.post('/get_domains_by_ips/')
async def get_domains_by_ips(ips: List[str]):
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


def handle_shutdown(signum, frame):
    db.close()
    print("Received shutdown signal. Stopping...")
    raise SystemExit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown)
    uvicorn.run(app, host="127.0.0.1", port=8000)
