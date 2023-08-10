import socket
import whois

from typing import List
from datetime import datetime
from domain_parser import parse_domains


def get_domains_by_ip(ip: str) -> List[str]:
    domains = []

    try:
        domains = parse_domains(ip)
    except Exception:
        pass

    try:
        dmn = socket.gethostbyaddr(ip)[0]
        if dmn not in domains:
            domains.append(dmn)
    except Exception:
        pass
    
    return domains


def get_ip_by_fqdn(fqdn: str) -> str:
    try:
        return socket.gethostbyname(fqdn)
    except socket.gaierror:
        return None


def __datetime_to_str(obj: List[datetime] | datetime) -> List[str] | str:
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


def get_whois_info(domain: str) -> dict:
    info = whois.whois(domain)

    return {
        'registrar': info.registrar,
        'creation_date': __datetime_to_str(info.creation_date),
        'expiration_date': __datetime_to_str(info.expiration_date),
        'name_servers': info.name_servers,
        'name': info.name,
    }
