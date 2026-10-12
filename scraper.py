from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scraper_utils import extract_product_data

from database import (
    create_connection,
    create_products_table,
    insert_product,
    close_connection
)


def create_driver():

    print("Creating Chrome driver...")

    options = Options()

    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)

    print("Chrome driver created.")

    return driver


def scrape_page(driver, page_number):

    url = f"https://www.amazon.in/s?k=laptop&page={page_number}"

    print("\n" + "=" * 80)
    print(f"Scraping page {page_number}")
    print("=" * 80)

    print("Opening:", url)

    driver.get(url)

    wait = WebDriverWait(driver, 15)

    try:

        wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div[data-component-type='s-search-result']"
                )
            )
        )

    except Exception:

        print("Products did not load on this page.")

        return []

    products = driver.find_elements(
        By.CSS_SELECTOR,
        "div[data-component-type='s-search-result']"
    )

    print("Products found on page:", len(products))

    product_data = []

    for product in products:

        data = extract_product_data(product)

        if data["name"]:
            product_data.append(data)

    print("Valid products scraped:", len(product_data))

    return product_data


def scrape_products(driver, target_count=150):

    all_products = []

    page_number = 1

    while len(all_products) < target_count:

        products = scrape_page(
            driver,
            page_number
        )

        if not products:

            print("No products found. Stopping scraper.")

            break

        all_products.extend(products)

        print(
            f"Total products collected so far: "
            f"{len(all_products)}"
        )

        page_number += 1

        if page_number > 20:

            print("Maximum page limit reached.")

            break

    return all_products[:target_count]


def save_products_to_database(products):

    connection = None

    try:

        connection = create_connection()

        create_products_table(connection)

        print("\nSaving products to PostgreSQL...")

        for index, product in enumerate(products, start=1):

            insert_product(
                connection,
                product
            )

            print(
                f"Saved product {index}/{len(products)}"
            )

        print("\nAll products processed successfully.")

    except Exception as error:

        print("Database error:", error)

    finally:

        if connection:

            close_connection(connection)


def main():

    print("Scraper started.")

    driver = create_driver()

    try:

        products = scrape_products(
            driver,
            target_count=150
        )

        print("\n" + "=" * 80)
        print("SCRAPING COMPLETED")
        print("=" * 80)

        print(
            "Total products scraped:",
            len(products)
        )

        save_products_to_database(products)

    finally:

        driver.quit()

        print("Browser closed.")


if __name__ == "__main__":

    main()