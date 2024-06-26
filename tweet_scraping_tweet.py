import re
import json
from selenium import webdriver
from selenium.webdriver import ChromeOptions
import chromedriver_binary
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from functools import wraps
import urllib.request
import os

options = ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument('--lang=ja-JP')
#options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("detach", True)

def main():
    preurl = "https://twitter.com" #You need to visit the site once to load the cookies.
    target_url = 'https://twitter.com/rasuko_okuma' #exampleURL
    driver = webdriver.Chrome(options=options)
    driver.get(preurl)
    

    #Cookieの読み込み.
    json_open = open('ChromeCookie.txt', 'r')
    cookies = json.load(json_open)
 
    for cookie in cookies:
        tmp = {"name": cookie["name"], "value": cookie["value"]}
        driver.add_cookie(tmp)

    driver.get(target_url)
    time.sleep(6)

        
    while True: 
        tweetScraper(driver)
        driver.execute_script("window.scrollBy(0,window.innerHeight)")
        time.sleep(2)
    


def count(f):
    @wraps(f)
    def wrapper(*args,**keyargs):
        v = f(*args,**keyargs)
        wrapper.count += 1
        return v
    wrapper.count = 1
    return wrapper


IDs = []

@count
def tweetScraper(driver):
    tweets = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
    tweet_with_all_attributes = {}

    destDiectory = 'results/rasuko_okuma2/'

    for tweet in tweets:
        #1つのツイートに対しての処理.
        #本文を取得
        text_elements = tweet.find_elements(By.CSS_SELECTOR, '[data-testid="tweetText"]') #１つのツイート内に複数の本文を所持.
        tweet_texts = {}

        for m,text_element in enumerate(text_elements):
            tweet_text = []
            for element in text_element.find_elements(By.CSS_SELECTOR, '*'): #./node()
                #１つの本文に対する処理.
                #alt属性の絵文字を適切に処理
                if element.tag_name == 'img':
                    tweet_text.append(element.get_attribute('alt'))
                else:
                    tweet_text.append(element.text)    

            tweet_text = " ".join(tweet_text)
            tweet_texts[m] = re.sub('\s',' ',tweet_text)    

            
        #The tweet body is represented by 0, and the quoted retweet body by 1.
        #Retrieve markers such as pinned, retweets, etc.
        try:
            social_context = tweet.find_element(By.CSS_SELECTOR,'[data-testid="socialContext"]').text

        except:
            social_context = None

        
        try:
            video_thumbnail = tweet.find_element(By.CSS_SELECTOR,'video').get_attribute('poster')

        except:
            video_thumbnail = None

        top_right = tweet.find_element(By.CSS_SELECTOR,'[data-testid="Tweet-User-Avatar"]')

        tweetUserLink = top_right.find_element(By.CSS_SELECTOR,'a').get_attribute('href')
        userID = re.search(r'(?<=/)([^/]+$)',tweetUserLink).group(0)
        
        tweetUserAvatar = top_right.find_element(By.CSS_SELECTOR,'img').get_attribute('src')

        top_left = tweet.find_element(By.CSS_SELECTOR,'[data-testid="User-Name"]')

        tweetID = top_left.find_element(By.CSS_SELECTOR,'[href*="status"]').get_attribute('href')
        tweetID = re.search(r'\d{15,}', tweetID).group(0)

        tweetDate = top_left.find_element(By.CSS_SELECTOR,'time').get_attribute('datetime')

        try:
            attached_url = tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"] > a').get_attribute('href')

        except:
            attached_url = None

        try:
            tweetPhoto = tweet.find_elements(By.CSS_SELECTOR, '[data-testid="tweetPhoto"] img')
            tweetPhoto = [i.get_attribute('src') for i in tweetPhoto]
            tweetPhoto = [re.sub(r'&.*','',j) for j in tweetPhoto] #"Get the highest quality image."

        except:
            tweetPhoto = None

        impressions = tweet.find_element(By.CSS_SELECTOR,'[role="group"]').get_attribute('aria-label')

        
    
        if tweetID not in IDs:
            tweet_with_all_attributes[tweetID] = { "socialcontext" : social_context, "tweetUser" : { "link" : tweetUserLink, "AvatarPhoto" : tweetUserAvatar}, "tweetDate" : tweetDate, "tweet" : tweet_texts, "attachedURL" : attached_url, "tweetPhoto" : tweetPhoto, "videoThumnail" : video_thumbnail, "impressions" : impressions }
            IDs.append(tweetID)
            print(f'　　{tweetID}を追加しました')

            
            if(tweetPhoto):
                for n,x in enumerate(tweetPhoto):
                    try:
                        photoName = f'{tweetID}-{n}-@{userID}-[{tweet_texts[0][0:40].replace("/","／")}...].png'
                    except: 
                        photoName = f'{tweetID}-{n}-@{userID}-[nulltext].png'

                    dest = destDiectory + 'photo/'
                    
                    if not os.path.exists(dest):
                        os.makedirs(dest)

                    destPathPhoto = dest + photoName
                    image_downloader(x,destPathPhoto,n,tweetID)

                  



    jsonName = f'result{tweetScraper.count}.json'    
    destPathJson = destDiectory + 'json/'
    #destDiectoryは最後に/付き.--最後の'/'を忘れないこと.
    if not os.path.exists(destPathJson):
        os.makedirs(destPathJson)

    destPathJson = destPathJson + jsonName
    

    with open(destPathJson, mode='wt', encoding='utf-8') as f:
        json.dump(tweet_with_all_attributes, f, ensure_ascii=False, indent=2)



def  image_downloader(url,path,n,tweetID,max_retries=10):
    retry_count = 0
    while retry_count < max_retries:
        try:
            urllib.request.urlretrieve(url, path)
            print(f"Downloaded {tweetID}-{n} successfully.")
            return True
        
        except Exception as e:
            print(f"Error downloading {tweetID}-{n}: {e}")
            retry_count += 1
            print(f"Retrying... ({retry_count}/{max_retries})")
            time.sleep(1)  
    print(f"Max retries reached for {tweetID}-{n}. Skipping...")
    return False



    

        
    

    
    




 

            


















if __name__ == '__main__':
    main()