import psycopg2


DB_NAME = "amazon_ecommerce"
DB_USER = "postgres"
DB_PASSWORD = "yug"
DB_HOST = "localhost"
DB_PORT = "5432"


def create_connection():
    connection = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    print("PostgreSQL connected successfully.")

    return connection


def create_products_table(connection):

    cursor = connection.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        price TEXT,
        rating TEXT,
        reviews TEXT,
        image TEXT,
        product_url TEXT UNIQUE
    );
    """

    cursor.execute(query)

    connection.commit()

    cursor.close()

    print("Products table is ready.")


def insert_product(connection, product):

    cursor = connection.cursor()

    query = """
    INSERT INTO products (
        name,
        price,
        rating,
        reviews,
        image,
        product_url
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (product_url)
    DO NOTHING;
    """

    cursor.execute(
        query,
        (
            product["name"],
            product["price"],
            product["rating"],
            product["reviews"],
            product["image"],
            product["product_url"]
        )
    )

    connection.commit()

    cursor.close()


def close_connection(connection):

    if connection:
        connection.close()

        print("PostgreSQL connection closed.")