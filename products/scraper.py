from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time


def scrape_books(search_text):

    driver = webdriver.Chrome()

    products = []

    try:

        base_url = "https://books.toscrape.com/catalogue/page-{}.html"

        for page in range(1, 4):

            print(f"Scraping page {page}")

            url = base_url.format(page)

            driver.get(url)

            time.sleep(2)

            soup = BeautifulSoup(
                driver.page_source,
                "html.parser"
            )

            books = soup.find_all(
                "article",
                class_="product_pod"
            )

            for book in books:

                title = book.h3.a["title"]

                if search_text.lower() not in title.lower():

                    continue

                link = book.h3.a["href"]

                link = (
                    "https://books.toscrape.com/"
                    + link.replace("../", "")
                )

                price = book.find(
                    "p",
                    class_="price_color"
                ).text

                image = book.find(
                    "img"
                )["src"]

                image = (
                    "https://books.toscrape.com/"
                    + image.replace("../", "")
                )

                products.append({

                    "title": title,

                    "price": price,

                    "image": image,

                    "link": link

                })

        return products

    finally:

        driver.quit()


def scrape_flipkart(search_text):

    driver = webdriver.Chrome()

    products = []

    try:

        search_text = search_text.replace(
            " ",
            "%20"
        )

        url = (
            f"https://www.flipkart.com/search?q="
            f"{search_text}"
        )

        driver.get(url)

        time.sleep(5)

        try:

            close_btn = driver.find_element(

                By.XPATH,

                "//button[contains(text(),'✕')]"

            )

            close_btn.click()

            time.sleep(3)

            print("Popup Closed")

        except:

            print("No Popup Found")

        cards = driver.find_elements(

            By.CSS_SELECTOR,

            "div[data-id]"

        )

        print("Cards Found:", len(cards))

        for card in cards[:10]:

            try:

                title = card.find_element(

                    By.CSS_SELECTOR,

                    "div.RG5Slk"

                ).text

                price = card.find_element(

                    By.CSS_SELECTOR,

                    "div.hZ3P6w"

                ).text

                image = card.find_element(

                    By.TAG_NAME,

                    "img"

                ).get_attribute("src")

                link = card.find_element(

                    By.TAG_NAME,

                    "a"

                ).get_attribute("href")

                print({
                    "title": title,
                    "price": price,
                    "image": image,
                    "link": link
                })

                products.append({

                    "title": title,

                    "price": price,

                    "image": image,

                    "link": link

                })

            except Exception as e:

                print("ERROR:", e)

        return products

    finally:

        driver.quit()


def scrape_croma(search_text):

    driver = webdriver.Chrome()

    products = []

    try:

        search_text = search_text.replace(" ", "%20")

        url = (
            f"https://www.croma.com/searchB?"
            f"q={search_text}%3Arelevance"
            f"&text={search_text}"
        )

        driver.get(url)

        time.sleep(8)

        cards = driver.find_elements(
            By.CSS_SELECTOR,
            "li.product-item"
        )

        print("Croma Cards Found:", len(cards))

        for card in cards[:10]:

            try:

                title = card.find_element(
                    By.CSS_SELECTOR,
                    "h3.product-title a"
                ).text

                price = card.find_element(
                    By.CSS_SELECTOR,
                    "span.plp-srp-new-amount"
                ).text

                img = card.find_element(By.TAG_NAME, "img")

                image = img.get_attribute("data-src")

                if not image:
                    image = img.get_attribute("src")

                link = card.find_element(
                    By.CSS_SELECTOR,
                    "h3.product-title a"
                ).get_attribute("href")

                products.append({

                    "title": title,

                    "price": price,

                    "image": image,

                    "link": link

                })

            except Exception as e:

                print("ERROR:", e)

        return products

    finally:

        driver.quit()