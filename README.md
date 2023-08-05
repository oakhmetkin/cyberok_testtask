# FQDN microservice

_CyberOK Internship task_


## Description

Service is built using Python and FastAPI. It provides next functionality:

- Get a list of IP addresses, return a list of domains associated with these addresses.
- Get a list of FQDNs, return a list of IP addresses.
- Get a list of second-level domains, return whois information for each domain.


## Configuring the service

- clone repo (```git clone <repo link>```)
- install require libraries (```pip install -r requirements.txt```)
- set environment variables (HOST, PORT, DB_PATH, DB_UPDATE_INTERVAL)
- run app (```python3 main.py```)


## API Description

### POST /get_domains_by_ips/

```json
// request:
// POST http://127.0.0.1:8000/get_ips_by_fqdns
// raw data:
[
    "8.8.8.8",
    "8.8.4.4"
]

// response:
[
    "dns.google",
    "dns.google"
]
```

### POST /get_ips_by_fqdns/

```json
// request:
// POST http://127.0.0.1:8000/get_ips_by_fqdns
// raw data:
[
    "google.com",
    "yandex.ru"
]

// response:
[
    "64.233.163.138",
    "5.255.255.77"
]
```

### POST /get_whois_info/

```json
// request:
// POST http://127.0.0.1:8000/get_whois_info
// raw data:
[
    "www.google.com",
    "mail.yahoo.com"
]

// response:
[
    {
        "registrar": "MarkMonitor Inc.",
        "creation_date": "1997-09-15T04:00:00",
        "expiration_date": "2028-09-14T04:00:00",
        "name_servers": [
            "NS1.GOOGLE.COM",
            "NS2.GOOGLE.COM",
            "NS3.GOOGLE.COM",
            "NS4.GOOGLE.COM"
        ],
        "name": null
    },
    {
        "registrar": "MarkMonitor Inc.",
        "creation_date": "1995-01-18T05:00:00",
        "expiration_date": "2024-01-19T05:00:00",
        "name_servers": [
            "NS1.YAHOO.COM",
            "NS2.YAHOO.COM",
            "NS3.YAHOO.COM",
            "NS4.YAHOO.COM",
            "NS5.YAHOO.COM"
        ],
        "name": null
    }
]
```