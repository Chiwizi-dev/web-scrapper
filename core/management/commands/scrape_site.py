import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from core.models import Author, Tag, Quote

import time
import random
from datetime import datetime

from urllib.parse import urljoin
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Scrape items from the quotes site and save them"

    def handle(self, *args, **options):
        self.stdout.write("Starting product scraping...")

        base_url = "https://quotes.toscrape.com/"
        url = base_url

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        while url:
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                quotes = soup.find_all("div", class_="quote")

                for item in quotes:
                    text = item.find("span", class_="text").text

                    author = item.find("small", class_="author").text

                    author_slug = slugify(author)
                    author_object, _ = Author.objects.get_or_create(
                        slug=author_slug, author=author
                    )

                    quote_object, _ = Quote.objects.get_or_create(
                        text=text, author=author_object
                    )

                    about_link_tag = item.find("a", string="(about)")
                    if about_link_tag:
                        author_details_url = about_link_tag["href"]

                    tags_list = []
                    tags = item.find("div", class_="tags")
                    if tags:
                        for tag_link_tag in tags.find_all("a", class_="tag"):
                            tag_name = tag_link_tag.text
                            tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                            tags_list.append(tag_obj)

                        quote_object.tags.set(tags_list)
                        self.stdout.write(f"saved new quoteby {author}")

                next_page_link = soup.find("li", class_="next")

                if next_page_link and next_page_link.find("a"):
                    next_page_url = next_page_link.find("a")["href"]

                    url = urljoin(base_url, next_page_url)
                    time.sleep(1)

                else:
                    url = None
            except requests.exceptions.RequestException as e:
                self.stderr.write(self.style.ERROR(f"Error fetching page {url}: {e}"))

            # ******************DETAIL PAGE********************

        authors = Author.objects.all()

        for author in authors:
            if author.date_of_birth and author.birth_place and author.description:
                continue

            author_details_url = f"{base_url}/author/{author.slug}/"

            try:
                response = requests.get(author_details_url, headers=headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                # author_title = soup.find("h3", class_="author-title")

                # if author_title:
                #     author.author = author_title.text

                author_born_date = soup.find("span", class_="author-born-date")

                author_born_location = soup.find("span", class_="author-born-location")

                author_description = soup.find("div", class_="author-description")

                if author_born_date:
                    date_string = author_born_date.text.strip()
                    if date_string:
                        try:
                            author.date_of_birth = datetime.strptime(
                                date_string, "%B, %d, %Y"
                            ).date()
                        except ValueError as e:
                            self.stderr.write(
                                self.style.ERROR(
                                    f"Error parsing date for {author.author}: {e}"
                                )
                            )
                            author.date_of_birth = None
                    else:
                        author.date_of_birth = None
                else:
                    author.date_of_birth = None

                if author_born_location:
                    author.birth_place = author_born_location.text

                if author_description:
                    author.description = author_description.text

                author.save()

                self.stdout.write(f"Updated details for author: {author.author} object")

                time.sleep(random.randint(1, 5))

            except requests.exceptions.RequestException as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"Error fetching author page {author_details_url}: {e}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("Scraping complete!"))
