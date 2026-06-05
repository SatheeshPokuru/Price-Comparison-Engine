from selenium import webdriver

from bs4 import BeautifulSoup

import time
 

def scrape_books(search_text):

    driver = webdriver.Chrome()

    base_url = "https://books.toscrape.com/catalogue/page-{}.html"
    time.sleep(3)
    
    html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")

    books = soup.find_all("article", class_="product_pod")

    products = []

    products = []

    for page in range(1, 4):

        print(f"Scraping page {page}")

        url = base_url.format(page)

        driver.get(url)

        time.sleep(2)

        html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")

        books = soup.find_all("article", class_="product_pod")

        for book in books:

            title = book.h3.a["title"]

            link = book.h3.a["href"]

            link = "https://books.toscrape.com/" + link.replace("../", "")

            if search_text:

                if search_text.lower() not in title.lower():

                    continue

            price = book.find("p", class_="price_color").text

            image = book.find("img")["src"]

            image = "https://books.toscrape.com/" + image.replace("../", "")

            products.append({

                "title": title,

                "price": price,

                "image": image,

                "link": link

            })

    driver.quit()

    return products