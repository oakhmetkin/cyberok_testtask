import requests
from bs4 import BeautifulSoup
import re
import warnings
from typing import List


warnings.filterwarnings('ignore',
    category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

__URL = 'https://www.cy-pr.com/tools/oneip/'


def parse_domains(ip: str) -> List[str]:
    data = { 'ip': ip }
    res = requests.post(__URL, data=data, verify=False)
    soup = BeautifulSoup(res.content, "html.parser")

    table = soup.find("table", style='')

    comp = re.compile(r'\d. (.+)')

    domains = []

    for row in table.find_all("tr"):
        domain = row.find_all("td")[0].text.strip()
        matches = comp.findall(domain)
        if matches:
            domains.append(matches[0])

    return domains