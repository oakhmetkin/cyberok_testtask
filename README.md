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

Response contains 2 fields: meta, answer. Answer contains requested data. 
Meta contains 2 fields: status, message. Status belongs { "fine", "good" }. 
"good" means all requested data retrieved. "fine" means that some data is 
waiting for DB updating.

### Methods

- POST /get_domains_by_ips/

```json
// request:
// POST http://127.0.0.1:8000/get_domains_by_ips
// raw data:
[
    "64.233.162.136",
    "169.46.57.243"
]

// response:
{
    "meta": {
        "status": "good",
        "message": "The request has been fully processed."
    },
    "answer": {
        "64.233.162.136": [
            "youtube.com",
            "li-in-f136.1e100.net"
        ],
        "169.46.57.243": [
            "wheather.com",
            "f3.39.2ea9.ip4.static.sl-reverse.com"
        ]
    }
}
```

- POST /get_ips_by_fqdns/

```json
// request:
// POST http://127.0.0.1:8000/get_ips_by_fqdns
// raw data:
[
    "google.com",
    "yandex.ru"
]

// response:
{
    "meta": {
        "status": "good",
        "message": "The request has been fully processed."
    },
    "answer": {
        "google.com": "64.233.165.113",
        "yandex.ru": "5.255.255.70"
    }
}
```

- POST /get_whois_info/

```json
// request:
// POST http://127.0.0.1:8000/get_whois_info
// raw data:
[
    "www.google.com",
    "mail.yahoo.com"
]

// response:
{
    "meta": {
        "status": "good",
        "message": "The request has been fully processed."
    },
    "answer": {
        "mail.yahoo.com": {
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
        },
        "www.google.com": {
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
        }
    }
}
```