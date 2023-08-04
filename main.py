from fastapi import FastAPI, Body
from typing import List

import socket
import whois

app = FastAPI()


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
        try:
            ip = socket.gethostbyname(fqdn)
        except socket.gaierror:
            ip = None

        ips.append(ip)

    return ips


@app.post('/get_whois_info/')
async def get_whois_info(domains: List[str]):
    ans = []

    for dmn in domains:
        info = whois.whois(dmn)

        ans.append({
            'registrar': info.registrar,
            'creation_date': info.creation_date,
            'expiration_date': info.expiration_date,
            'name_servers': info.name_servers,
            'name': info.name,
        })
    
    return ans
