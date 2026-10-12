from selenium.webdriver.common.by import By


def get_text(element):
    try:
        return element.text.strip()
    except Exception:
        return ""


def get_attribute(element, attribute):
    try:
        return element.get_attribute(attribute) or ""
    except Exception:
        return ""


def clean_text(text):
    if not text:
        return ""

    return " ".join(text.split())


def find_element_text(product, selectors):

    for selector in selectors:

        try:
            element = product.find_element(
                By.CSS_SELECTOR,
                selector
            )

            text = clean_text(get_text(element))

            if text:
                return text

        except Exception:
            continue

    return ""


def find_element_attribute(product, selectors, attribute):

    for selector in selectors:

        try:
            element = product.find_element(
                By.CSS_SELECTOR,
                selector
            )

            value = get_attribute(
                element,
                attribute
            )

            if value:
                return value

        except Exception:
            continue

    return ""


def extract_product_data(product):

    name = find_element_text(
        product,
        [
            "h2 span",
            "h2",
            "h2 a span"
        ]
    )

    price = find_element_text(
        product,
        [
            ".a-price .a-offscreen",
            ".a-price-whole"
        ]
    )

    rating = find_element_text(
        product,
        [
            ".a-icon-alt"
        ]
    )

    reviews = find_element_text(
        product,
        [
            "span.a-size-base.s-underline-text",
            "a[aria-label*='ratings']",
            "a[aria-label*='rating']"
        ]
    )

    image = find_element_attribute(
        product,
        [
            "img.s-image"
        ],
        "src"
    )

    product_url = find_element_attribute(
        product,
        [
            "h2 a",
            "a.a-link-normal"
        ],
        "href"
    )

    return {
        "name": name,
        "price": price,
        "rating": rating,
        "reviews": reviews,
        "image": image,
        "product_url": product_url
    }