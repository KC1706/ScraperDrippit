import requests
from bs4 import BeautifulSoup
from selenium import webdriver
# from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import time
import os
from time import sleep
import json
import schedule
import psycopg2


def get_label(item):
    """Extract title from Zara product item"""
    try:
       
            name_elem = item.find("h2")
            if name_elem:
              
                return name_elem.text.strip()
    except:
        return None

def get_description(item):
    header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
    item_link = item.find("a", {"class": "product-link _item product-grid-product-info__name link"})["href"]
    print(f"item_link for description: {item_link}")
    # Fetch the product page
    response = requests.get(item_link, headers=header)
    
    if response.status_code == 200:
        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(response.content, "lxml")
        
        # Now you can find the description element
        description_elem = soup.find('div', class_='product-detail-description product-detail-info__description')
        
        if description_elem:
            print(description_elem.text.strip())
            return description_elem.text.strip()
        else:
            print("Description element not found.")
            return None
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return None


def get_prices(item):
    """Extract current and original prices from Zara product item as objects with currency."""
    try:
        price_elem = item.find('span', class_='price-current__amount')
        if not price_elem:
            return None, None
            
        current_price = price_elem.find('span').text.strip().replace('₹', '').replace(',', '')
        current_price_float = float(current_price)
        
        original_elem = item.find('span', class_='price-old__amount price__amount price__amount-old')
        original_price_float = None
        discount = None
        
        if original_elem:
            original_price = original_elem.find('span').text.strip().replace('₹', '').replace(',', '')
            original_price_float = float(original_price)
            if original_price_float > current_price_float:
                discount = round(((original_price_float - current_price_float) / original_price_float) * 100, 2)

        price_obj = {
            "default": current_price_float,
            "price_meta": {
                "CURRENCY": "INR",
                "OLD_PRICE": original_price_float,
                "DISCOUNT": discount
            }
        }

        return price_obj, None  # Second return value kept for backward compatibility

    except Exception as e:
        print(f"Error extracting prices: {e}")
        return None, None


def get_item_image_link(container):
    # Set up the WebDriver (using Chrome in this example)
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Consider not using headless mode if you're facing access issues
    # options.add_argument("--headless")

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Open the product page to get the real image URL
        product_link = container.find("a", {"class": "product-link _item product-grid-product-info__name link"})["href"]
        driver.get(product_link)
        time.sleep(5)  # Wait for JavaScript to load

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all image elements within the product detail images
        image_elements = soup.find_all('picture', class_='media-image')
        # Extract all image URLs from the srcset attributes
        image_urls = []
        for picture in image_elements:
            sources = picture.find_all('source')
            for source in sources:
                srcset = source.get('srcset', '')
                urls = [url.split(' ')[0] for url in srcset.split(',')]
                image_urls.extend(urls)

        # If no URLs were found in srcset, fall back to the img src
        if not image_urls:
            img_tag = soup.find('img', class_='media-image__image media__wrapper--media')
            if img_tag:
                image_urls.append(img_tag.get('src', ''))

        # Remove URLs that contain '375' and empty links from the list
        image_urls = [url for url in image_urls if '375' not in url and url]  # Filter out URLs with '375' and empty links

        return image_urls
    except Exception as e:
        print(f"Error fetching image URL with Selenium: {e}")
        return None
    finally:
        driver.quit()


def write_to_json(product, filename='products.json'):
    """Append a single product's details to a JSON file."""
    # Ensure the file exists and is a valid JSON array
    if not os.path.exists(filename):
        with open(filename, 'w') as json_file:
            json.dump([], json_file)  # Create an empty JSON array

    # Read existing products
    with open(filename, 'r') as json_file:
        products = json.load(json_file)

    # Append the new product
    products.append(product)

    # Write back to the file
    with open(filename, 'w') as json_file:
        json.dump(products, json_file, indent=4)

def get_all_info(container):
    label = get_label(container)
    price, _ = get_prices(container)
    item_link = container.find("a", {"class": "product-link _item product-grid-product-info__name link"})["href"]
    description = get_description(container)
    print(f"description of the item: {description}")
    item_image_link = get_item_image_link(container)

    product_info = {
        "label": label,
        "description": description,
        "price": price,
        "images": item_image_link if item_image_link else [],
        "meta": {
            "ITEM_LINK": item_link,
        },
    }
    
    return product_info






def fetch_url_with_retries(url, headers, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            return response
        except requests.exceptions.RequestException as e:
            # print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                sleep(delay)
            else:
                raise


def scrape_and_update():
    """Function to scrape Zara's website and update database."""
    # Get database connection
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return

    # Create table if it doesn't exist
    create_products_table(conn)
    
    # Your existing scraping code...
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    clothing_links = [
        "https://www.zara.com/in/en/woman-blazers-l1055.html?v1=2417363",
        "https://www.zara.com/in/en/woman-dresses-l1066.html?v1=2417457&regionGroupId=80",
        "https://www.zara.com/in/en/woman-outerwear-l1184.html?v1=2418641&regionGroupId=80",
        "https://www.zara.com/in/en/woman-jackets-l1114.html?v1=2418596&regionGroupId=80",
        "https://www.zara.com/in/en/woman-tshirts-l1362.html?v1=2416537&regionGroupId=80",
        "https://www.zara.com/in/en/woman-outerwear-vests-l1204.html?v1=2416383&regionGroupId=80",
        "https://www.zara.com/in/en/woman-tops-l1322.html?v1=2417539&regionGroupId=80",
        "https://www.zara.com/in/en/woman-knitwear-l1152.html?v1=2418540&regionGroupId=80",
        "https://www.zara.com/in/en/woman-shirts-l1217.html?v1=2416489&regionGroupId=80",
        "https://www.zara.com/in/en/woman-sweatshirts-l1320.html?v1=2535415&regionGroupId=80" ,
        "https://www.zara.com/in/en/woman-skirts-l1299.html?v1=2416418&regionGroupId=80",
        "https://www.zara.com/in/en/woman-jeans-l1119.html?v1=2416541&regionGroupId=80",
        "https://www.zara.com/in/en/woman-trousers-l1335.html?v1=2418507&regionGroupId=80",
        "https://www.zara.com/in/en/man-outerwear-l715.html?v1=2415758&regionGroupId=80",
        "https://www.zara.com/in/en/man-knitwear-l681.html?v1=2416830&regionGroupId=80",
        "https://www.zara.com/in/en/man-sweatshirts-l821.html?v1=2416797&regionGroupId=80",
        "https://www.zara.com/in/en/man-tshirts-l855.html?v1=2415607&regionGroupId=80",
        "https://www.zara.com/in/en/man-polos-l733.html?v1=2415614&regionGroupId=80",
        "https://www.zara.com/in/en/man-trousers-l838.html?v1=2415660&regionGroupId=80",
        "https://www.zara.com/in/en/man-jeans-l659.html?v1=2415695&regionGroupId=80",
    ]

    clothing_category_links = [clothing_links[0:10],
                               clothing_links[10:13],
                               clothing_links[13:18],
                               clothing_links[18:20],]

    try:
        # Clear existing products
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE products RESTART IDENTITY")
        conn.commit()

        for category in clothing_category_links:
            for link in category:
                category_client = requests.get(link, headers=header)
                category_soup = BeautifulSoup(category_client.content, "lxml")
                item_containers = category_soup.findAll("div", {"class": "product-grid-product-info"})
                
                for container in item_containers:
                    product_info = get_all_info(container)
                    if product_info:
                        insert_product_to_db(conn, product_info)
                        print(f"Inserted product: {product_info['label']}")

        print("Finished scraping and updating database.")
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        conn.close()

# Schedule the scraping to run every 24 hours
schedule.every(24).hours.do(scrape_and_update)

DATABASE_URL = "postgresql://stylo:zer1Ayhuumvdi0WiyFeNcjq7NrwEbLIc@dpg-cte6h3a3esus73br6idg-a.singapore-postgres.render.com/stylo"

def get_db_connection():
    try:
        connection = psycopg2.connect(
            DATABASE_URL,
            sslmode='require',
            connect_timeout=10
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def create_products_table(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    label TEXT,
                    description TEXT,
                    price_default FLOAT,
                    price_currency TEXT,
                    price_old FLOAT,
                    price_discount FLOAT,
                    images TEXT[],
                    item_link TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
        print("Products table created successfully")
    except Exception as e:
        print(f"Error creating table: {e}")

def insert_product_to_db(conn, product):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO products (
                    label, description, price_default, price_currency, 
                    price_old, price_discount, images, item_link
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                product['label'],
                product['description'],
                product['price']['default'],
                product['price']['price_meta']['CURRENCY'],
                product['price']['price_meta']['OLD_PRICE'],
                product['price']['price_meta']['DISCOUNT'],
                product['images'],
                product['meta']['ITEM_LINK']
            ))
        conn.commit()
    except Exception as e:
        print(f"Error inserting product: {e}")

if __name__ == "__main__":
    # Make sure you have psycopg2 installed
    try:
        import psycopg2
        from psycopg2.extras import Json
    except ImportError:
        print("Please install psycopg2: pip install psycopg2-binary")
        exit(1)

    scrape_and_update()  # Initial run
    while True:
        schedule.run_pending()
        time.sleep(1)
