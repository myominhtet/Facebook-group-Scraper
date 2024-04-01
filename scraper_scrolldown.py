#python3 scraper.py mee589731@gmail.com mee12345@ https://www.facebook.com/groups/1436956330229869 --group
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
import requests
import uuid
import re
import csv
from argparse import ArgumentParser
parser = ArgumentParser()
def is_valid_url(url):
    # Regular expression to validate URLs
    url_regex = r"^(http|https)://[^\s/$.?#].[^\s]*$"
    return re.match(url_regex, url) is not None

if __name__ == "__main__":
    parser.add_argument("--username", type=str, help="Username for authentication")
    parser.add_argument("--password", type=str, help="Password for authentication")
    parser.add_argument("--link", type=str, help="Link to the group, page, or profile")

    parser.add_argument("--group", action="store_true", help="Scrape as a group")
    parser.add_argument("--page", action="store_true", help="Scrape as a page")
    parser.add_argument("--profile", action="store_true", help="Scrape as a profile")
    args = parser.parse_args()

    if not any([args.group, args.page, args.profile]):
        parser.error("Please specify --group, --page, or --profile")

    if args.group and (args.page or args.profile):
        parser.error("Cannot specify both --group and --page/--profile")

    if not is_valid_url(args.link):
        parser.error("Invalid link format. Please provide a valid URL.")

    # Your scraping logic goes here
    print("Username:", args.username)
    print("Password:", args.password)
    print("Link:", args.link)
    print("Group:", args.group)
    print("Page:", args.page)
    print("Profile:", args.profile)


chrome_options = Options()

chrome_options.add_argument("--incognito")
chrome_options.add_argument("--window-size=1920 x 1080")

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='/bin/chromedriver')

driver.get('https://www.facebook.com/login/')
time.sleep(1)

Group = True

dir = './scraped_data/'
if not os.path.exists(dir):
    os.makedirs(dir)
    
user = driver.find_element_by_xpath('//*[@id="email"]').send_keys(args.username)
password = driver.find_element_by_xpath('//*[@id="pass"]').send_keys(args.password)
submit = driver.find_element_by_xpath('//*[@id="loginbutton"]').click()
time.sleep(1)

# driver.get('https://www.facebook.com/MyanmarCelebrityTV')#page
driver.get(args.link)#group
# driver.get('https://www.facebook.com/thetnaingoo123514')#profile
time.sleep(1)

#clicking group feed order
sorting_svg = driver.find_element(By.CSS_SELECTOR, '.x19dipnz.x1lliihq.x1k90msu.x2h7rmj.x1qfuztq[title="sort group feed by"]')
driver.execute_script("arguments[0].setAttribute('title', 'New posts')", sorting_svg)
sorting_svg.click()

#wait and click New posts
time.sleep(1)
# Find the element for "New posts" by its class name
new_posts_element = driver.find_element(By.XPATH, "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x41vudc x6prxxf xvq8zen xk50ysn xzsf02u x1yc453h' and contains(text(), 'New posts')]")

# Click the "New posts" element
new_posts_element.click()

#real time updating and scraping
downloaded_images = set()
data = []
total_images_saved = 0
total_text_saved = 0

def extract_new_posts():
    global downloaded_images
    global data
    global total_images_saved
    global total_text_saved
    for i in range (1):
        # Scroll to load more posts
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        # Find all posts
        posts = driver.find_elements(By.CSS_SELECTOR, ".x78zum5.xdt5ytf.xz62fqu.x16ldp7u")

        # Loop through the posts and extract data
        for post in posts:
            # Text extraction
            post_html = post.get_attribute('outerHTML')
            soup = BeautifulSoup(post_html, 'html.parser')
            div_elements = soup.find_all('div')

            # Extract text containing 'Mee'
            extracted_text = [div.get_text() for div in div_elements if 'Mee' in div.get_text()]
            for text in extracted_text:
                if text not in data:
                    data.append(text)
                    total_text_saved += 1
                    print("Text added")

            # Image extraction
            image_elements = driver.find_elements(By.CSS_SELECTOR, "img.x1ey2m1c.xds687c.x5yr21d.x10l6tqk.x17qophe.x13vifvy.xh8yej3.xl1xv1r")

            # Loop through each image element
            for image_element in image_elements:
                image_src = image_element.get_attribute("src")
                if image_src in downloaded_images:
                    continue
                response = requests.get(image_src)
                if response.status_code == 200:
                    image_id = uuid.uuid4().hex[:8]  # Generate a random 8-character hex string
                    file_name = f"image_{image_id}.jpg"
                    
                    with open(dir+file_name, "wb") as file:
                        file.write(response.content)
                        print("Image saved as ", file_name)
                        total_images_saved += 1
                    downloaded_images.add(image_src)
                else:
                    print("Fail to fetch the image")

    # Use JavaScript to click all "See more" buttons
    js_script = """
    var buttons = document.querySelectorAll('.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.xt0b8zv.xzsf02u.x1s688f');
    buttons.forEach(function(button) {
        if (button.textContent == 'See more') {
            button.click();
        }
    });
    """
    driver.execute_script(js_script)

        
    return data


# Main loop for real-time monitoring
while True:
    new_data = extract_new_posts()
    # Perform text cleaning after all text has been extracted
    cleaned_data = [text.replace('Mee', '').encode('utf-8').decode('utf-8') for text in new_data]
    cleaned_data = [text.replace('\n', '').encode('utf-8').decode('utf-8') for text in cleaned_data]
    cleaned_data = [re.sub(r'[~!*•.=@#$%^&*()_+?/<|\\]', '', text).encode('utf-8').decode('utf-8') for text in cleaned_data]
    cleaned_data = [text.strip().encode('utf-8').decode('utf-8') for text in cleaned_data]
    
    # Write data to CSV file
    with open(dir+'data.csv', 'w', newline='', encoding='utf-8') as F:
        writer = csv.writer(F)
        writer.writerow(['text'])
        for item in cleaned_data:
            writer.writerow([item])
    print("Total images saved:", total_images_saved)
    print("Total text saved:", total_text_saved)
    print("Use Ctrl+C to stop the program")
    time.sleep(10)



