import re
import json
from selenium import webdriver
from selenium.webdriver import ChromeOptions
import chromedriver_binary
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time


options = ChromeOptions()
#options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument('--lang=ja-JP')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("detach", True)

def main():
    preurl = "https://twitter.com"
    target_url = 'https://twitter.com/usadapekora' #exampleURL
    driver = webdriver.Chrome(options=options)
    driver.get(preurl)

    #Cookieの読み込み.
    json_open = open('ubuntuChromeCookie.txt', 'r')
    cookies = json.load(json_open)
 
    for cookie in cookies:
        tmp = {"name": cookie["name"], "value": cookie["value"]}
        driver.add_cookie(tmp)

    driver.get(target_url)
    time.sleep(6)

    profielFinder(driver)

    


def profielFinder(driver):
    profiels = {}
    
    userName = driver.find_element(By.XPATH,'//*[@data-testid="UserName"]')
    userName = emojiHunter(userName.get_attribute("outerHTML"))
    userName = userName.split('@')
    profiels['UserName'] = userName[0]
    profiels['UserID'] = userName[1]
    
    try:
        userDescription = driver.find_element(By.XPATH,'//*[@data-testid="UserDescription"]')
        userDescription = emojiHunter(userDescription.get_attribute("outerHTML"))
        profiels['UserDescription'] = userDescription

    except NoSuchElementException:
        profiels['UserDescription'] = None

    try:
        userLocation = driver.find_element(By.XPATH,'//*[@data-testid="UserLocation"]')
        userLocation = emojiHunter(userLocation.get_attribute("outerHTML"))
        profiels['UserLocation'] = userLocation
    
    except NoSuchElementException:
        profiels['UserLocation'] = None

    try:
        userUrl = driver.find_element(By.XPATH,'//*[@data-testid="UserUrl"]').get_attribute("href")
        profiels['UserUrl'] = userUrl

    except NoSuchElementException:
        profiels['UserUrl'] = None

    try:
        userBirthdate = driver.find_element(By.XPATH,'//*[@data-testid="UserBirthdate"]').text
        userBirthdate = re.findall(r'\d+月\d+日',userBirthdate)[0]
        profiels['UserBirthdate'] = userBirthdate

    except NoSuchElementException:
        profiels['UserBirthdate'] = None

    userJoinDate = driver.find_element(By.XPATH,'//*[@data-testid="UserJoinDate"]').text
    userJoinDate = re.findall(r'\d+年\d+月',userJoinDate)[0]
    profiels['UserJoinDate'] = userJoinDate

    profiels['headerPhoto'] = f"https://twitter.com/{profiels['UserID']}/header_photo"
    profiels['avaterPhoto'] = f"https://twitter.com/{profiels['UserID']}/photo"
    
    with open('result6.json', mode='wt', encoding='utf-8') as f:
        json.dump(profiels, f, ensure_ascii=False, indent=2)

           
            

        
#正規表現のゴリ押しでhtmlからテキストと絵文字を取り出す.
#絵文字がalt属性として記述されているから.textでは取得できない.
def emojiHunter(text):
    text = re.findall(r'>[^<]+<|alt="[^"]+"',text)
    text = [re.sub(r'^>|<$', '', str(x)) for x in text]
    text = [re.sub(r'^(alt=")|"$','',str(y)) for y in text]
    text = [re.sub(r'\n','　',str(z)) for z in text]
    text = ''.join(text)
    #text = zwj(text)
    return text


    

    


    
    



if __name__ == '__main__':
    main()