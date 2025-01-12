import requests
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import time
import os
from time import sleep


def get_title(item):
    """Extract title from Zara product item"""
    try:
       
            name_elem = item.find("h2")
            if name_elem:
              
                return name_elem.text.strip()
    except:
        return None



def get_prices(item):
    """Extract current and original prices from Zara product item"""
    try:
        price_elem = item.find('span', class_='price-current__amount')
        if not price_elem:
            return None, None
            
        current_price = price_elem.find('span').text.strip().replace('₹', '').replace(',', '')
        
        original_elem = item.find('span', class_='price-old__amount price__amount price__amount-old')
        original_price = original_elem.find('span').text.strip().replace('₹', '').replace(',', '') if original_elem else current_price

        return float(current_price), float(original_price)
    except:
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
        print(f"Searching image in link: {product_link}")
        driver.get(product_link)
        time.sleep(5)  # Wait for JavaScript to load

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print(soup)

        # Find all image elements within the product detail images
        image_elements = soup.find_all('picture', class_='media-image')
        print(f"image_elements: {image_elements}")
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

        return image_urls[0]
    except Exception as e:
        print(f"Error fetching image URL with Selenium: {e}")
        return None
    finally:
        driver.quit()









def get_all_info(container):
    """
    Calls get_title, get_target_gender, get_prices, get_item_image_link, get_colors
    to get the important information for the current item.
    :param container: The item container for the current item
    :return: title, gender, current_price, old_price, item_link, image_link, and colors
    """

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Go through each item container
    title = get_title(container)
    # gender = get_target_gender(container)
    current_price, old_price = get_prices(container)
    item_link = container.find("a", {"class": "product-link _item product-grid-product-info__name link"})["href"]
   
    item_image_link = get_item_image_link(container)
    
    return title, current_price, old_price, item_link,item_image_link


def write_to_csv(category_links, categories):
    """
    Given the list of links for the subcategories of the men and women's clothing section of Nike,
    grab the product information and write to CSV files in the nike_scraped folder.
    """


    if not os.path.exists("zara_scraped"):
        os.makedirs("zara_scraped")

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    category_index = 0
    for category in category_links:
        print("Starting section: " + categories[category_index])

     
        category_name = categories[category_index]
        category_split = category_name.split("_")
        file_path = os.path.join("zara_scraped", f"zara_{category_split[1]}_{category_split[0]}.csv")
        
        with open(file_path, "w") as f:
            headers = "Name, Gender, Price, Sale Price, Colors, Item Link, Image Link, Subcategory, Brand \n"
            f.write(headers)
            for link in category:
                print(f"Searching link: {link}")
                category_client = requests.get(link, headers=header)
                category_soup = BeautifulSoup(category_client.content, "lxml")
                item_containers = category_soup.findAll("div", {"class": "product-grid-product-info"})
                
                index=0
             
                while(index<len(item_containers)):
                   
                    
                    title, current_price, old_price, \
                        item_link,image_link= get_all_info(item_containers[index])
                    index=index+1
                

                    f.write(title + ","  +str(image_link) +  "," + str(current_price) + "," + str(old_price) +
                             ", " + str(item_link) +
                            "," + "Zara" + "\n")

        print("Finished section: " + categories[category_index])
        category_index = category_index + 1


def fetch_url_with_retries(url, headers, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                sleep(delay)
            else:
                raise


def main():
    """
    Using modules requests and BeautifulSoup, scrape the Nike website for the clothing sections
    of both men and women, creating a .csv file for each subcategory of the clothing sections.
    The program currently only grabs the lazily loaded products, and creates 21 different .csv files.

    :return: None
    """
    start_time = time.time()

    print("Starting to scrape Zara's website. Average runtime is around twenty minutes.")

    
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
    
    categories = [
                  "women_tops",
                  "women_bottoms",
                  "men_tops",
                  "men_bottoms",
                  ]

    write_to_csv(clothing_category_links, categories)

    time_taken = round(time.time() - start_time)
    time_minutes = time_taken // 60
    time_seconds = time_taken % 60
    print("Finished scraping Nike in", str(time_minutes) + " minutes and " + str(time_seconds) + " seconds.")


if __name__ == "__main__":
    main()
