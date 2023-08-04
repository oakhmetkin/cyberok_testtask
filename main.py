from fastapi import FastAPI, Body
import uvicorn
from typing import List

import socket
import whois
import signal

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


def handle_shutdown(signum, frame):
    # DB conn closing...
    print("Received shutdown signal. Stopping...")
    raise SystemExit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown)
    uvicorn.run(app, host="127.0.0.1", port=8000)
