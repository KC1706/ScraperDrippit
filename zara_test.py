import requests
from bs4 import BeautifulSoup

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Example item link
item_link = "https://www.zara.com/in/en/zw-collection-linen-blend-dress-with-lace-trim-p07909586.html"

# Fetch the product page
response = requests.get(item_link, headers=header)

if response.status_code == 200:
    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.content, "lxml")
    
    # Now you can find the description element
    description_elem = soup.find('div', class_='product-detail-description product-detail-info__description')
    
    if description_elem:
        print(description_elem.text.strip())
    else:
        print("Description element not found.")
else:
    print(f"Failed to fetch the page. Status code: {response.status_code}")
# img_containers = category_soup.findAll("div", {"class": "media__wrapper media__wrapper--fill"})
# print(len(item_containers))
# print(len(img_containers))
# index=0

# img_containers = category_soup.findAll("div", {"class": "media__wrapper media__wrapper--fill"})
# img = img_containers[0].find("img")["src"]

# for product in item_containers:
#     try:
         
#                 name_elem = product.find("h2")
#                 price_elem = product.find('span', class_='price-current__amount')
#                 current_price = price_elem.find('span').text.strip().replace('₹', '').replace(',', '')
#                 original_elem = product.find('span', class_='price-old__amount price__amount price__amount-old')
#                 original_price = original_elem.find('span').text.strip().replace('₹', '').replace(',', '') if original_elem else current_price
#                 current_price, original_price = float(current_price), float(original_price)
#                 item_link = product.find("a", {"class": "product-link _item product-grid-product-info__name link"})["href"]
               

#                 if name_elem:
#                     print(f"{name_elem.text.strip()}, current_price: {current_price}, original_price: {original_price}, item_link: {item_link}, image_link: {image_link}")
#     except:
#         print("Product name not found")

# while(index<len(item_containers)):
#     try:
         
                # name_elem = item_containers[index].find("h2")
                # price_elem = item_containers[index].find('span', class_='price-current__amount')
                # current_price = price_elem.find('span').text.strip().replace('₹', '').replace(',', '')
                # original_elem = item_containers[index].find('span', class_='price-old__amount price__amount price__amount-old')
                # original_price = original_elem.find('span').text.strip().replace('₹', '').replace(',', '') if original_elem else current_price
                # current_price, original_price = float(current_price), float(original_price)
                # item_link = item_containers[index].find("a", {"class": "product-link _item product-grid-product-info__name link"})["href"]
    #             image_link = img_containers[index]


    #                 # print(f"{name_elem.text.strip()}, current_price: {current_price}, original_price: {original_price}, item_link: {item_link}, image_link: {image_link}")
    #             print(f"image_link: {image_link}")
    #             print("  ")
    # except:
    #     print("Product name not found")
    # index=index+1

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import time

# # Set up Chrome options
# options = Options()
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# # Consider not using headless mode if you're facing access issues
# # options.add_argument("--headless")

# # Initialize the WebDriver
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# try:
#     # Open the product page
#     product_link = "http://www.zara.com/in/en/zw-collection-cropped-blazer-p07522257.html"
#     driver.get(product_link)
#     time.sleep(5)  # Wait for the page to load completely

#     # Check if access is denied
#     if "Access Denied" in driver.page_source:
#         print("Access Denied. Consider using a proxy or adjusting headers.")
#     else:
#         # Proceed with extracting data
#         print("Page loaded successfully.")
#         # Add your data extraction logic here

# except Exception as e:
#     print(f"An error occurred: {e}")

# finally:
#     driver.quit()



# def write_to_csv(category_links, categories):
#     """
#     Given the list of links for the subcategories of the men and women's clothing section of Nike,
#     grab the product information and write to CSV files in the nike_scraped folder.
#     """


#     if not os.path.exists("zara_scraped"):
#         os.makedirs("zara_scraped")

#     header = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
#     }

#     category_index = 0
#     for category in category_links:
#         # print("Starting section: " + categories[category_index])

     
#         category_name = categories[category_index]
#         category_split = category_name.split("_")
#         file_path = os.path.join("zara_scraped", f"zara_{category_split[1]}_{category_split[0]}.csv")
        
#         with open(file_path, "w") as f:
#             headers = "Name, Description, Image, Link Price, Sale Price, Item Link \n"
#             f.write(headers)
#             for link in category:
#                 # print(f"Searching link: {link}")
#                 category_client = requests.get(link, headers=header)
#                 category_soup = BeautifulSoup(category_client.content, "lxml")
#                 item_containers = category_soup.findAll("div", {"class": "product-grid-product-info"})
                
#                 index=0
             
#                 while(index<len(item_containers)):
                   
                    
#                     title, description, current_price, old_price, \
#                         item_link,image_link= get_all_info(item_containers[index])
#                     index=index+1
                

#                     f.write(title + ","  +str(description)+ ","+ str(image_link) +  "," + str(current_price) + "," + str(old_price) +
#                              ", " + str(item_link) +
#                              "\n")

#         print("Finished section: " + categories[category_index])
#         category_index = category_index + 1


    # categories = [
    #               "women_tops",
    #               "women_bottoms",
    #               "men_tops",
    #               "men_bottoms",
    #               ]