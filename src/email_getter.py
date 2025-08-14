import requests
import scrapy
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class ContactSpider(scrapy.Spider):
    name = "contact_spider"
    _emails = []

    def get_emails(self):
        return self._emails

    def parse(self, response):
        # Ищет email-адреса
        emails = response.css("::text").re(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        for email in emails:
            print(email)
            self._emails.append(email)


def get_links(base_url):
    session = requests.Session()
    response = session.get(base_url)  # получаем код страницы входа
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")
    result = []
    for link in links:
        if link.get("href") is not None:
            url = base_url + link.get("href").replace(base_url, "")
            result.append(url.replace("//", "/"))
    return result


def get_filtered_emails(staff:dict, base_url:str):
    def get_emails():
        settings = get_project_settings()
        settings.set("start_urls", get_links(base_url))

        process = CrawlerProcess(settings)
        process.crawl(ContactSpider)
        process.start()

        filtered_emails = {}
        for person in staff:
            first_name = person.split(" ")[0]
            last_name = person.split(" ")[1]
            for email in ContactSpider._emails:
                if first_name.lower() in email.lower() or last_name.lower() in email.lower():
                    filtered_emails["person"] = email

    return get_emails()


