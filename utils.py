import socket
import whois

from typing import List
from datetime import datetime


def get_domain_by_ip(ip: str):
    try:
        return socket.gethostbyaddr(ip)
    except socket.herror:
        return None


def get_ip_by_fqdn(fqdn: str):
    try:
        return socket.gethostbyname(fqdn)
    except socket.gaierror:
        return None


def __datetime_to_str(obj: List[datetime] | datetime):
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


def get_whois_info(domain: str):
    info = whois.whois(domain)

    return {
        'registrar': info.registrar,
        'creation_date': __datetime_to_str(info.creation_date),
        'expiration_date': __datetime_to_str(info.expiration_date),
        'name_servers': info.name_servers,
        'name': info.name,
    }
