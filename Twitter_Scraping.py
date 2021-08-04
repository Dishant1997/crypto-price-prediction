import re
import csv
from getpass import getpass
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from msedge.selenium_tools import Edge, EdgeOptions
import time
import datetime
import pymongo


user = "abimortel@gmail.com"
my_password = "abimortel@"

def get_tweet_data(card):
    """Extract data from tweet card"""
    username = card.find_element_by_xpath('.//span').text
    try:
        handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
    except NoSuchElementException:
        return

    try:
        postdate = card.find_element_by_xpath('.//time').get_attribute('datetime')
    except NoSuchElementException:
        return

    comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    responding = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    text = comment + responding
    reply_cnt = card.find_element_by_xpath('.//div[@data-testid="reply"]').text
    retweet_cnt = card.find_element_by_xpath('.//div[@data-testid="retweet"]').text
    like_cnt = card.find_element_by_xpath('.//div[@data-testid="like"]').text

    # get a string of all emojis contained in the tweet
    """Emojis are stored as images... so I convert the filename, which is stored as unicode, into 
    the emoji character."""
    emoji_tags = card.find_elements_by_xpath('.//img[contains(@src, "emoji")]')
    emoji_list = []
    for tag in emoji_tags:
        filename = tag.get_attribute('src')
        try:
            emoji = chr(int(re.search(r'svg\/([a-z0-9]+)\.svg', filename).group(1), base=16))
        except AttributeError:
            continue
        if emoji:
            emoji_list.append(emoji)
    emojis = ' '.join(emoji_list)

    tweet = (username, handle, postdate, text, emojis, reply_cnt, retweet_cnt, like_cnt)
    return tweet

def twitter():
    today = datetime.datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    DD = datetime.timedelta(days=1)
    earlier = today - DD
    earlier_str = earlier.strftime("%Y-%m-%d")

    # application variables

    search_term = "(bitcoin OR cryptocurrency OR crypto) -retweet -giveaway (#btc OR #bitcoin) min_replies:50 min_faves:500 min_retweets:20 until:" + today_str + " since:" + earlier_str
    # since:2021-07-12 until:2021-07-14

    # create instance of web driver
    options = EdgeOptions()
    options.use_chromium = True
    driver = Edge(options=options)

    # navigate to login screen
    driver.get('https://www.twitter.com/login')
    driver.maximize_window()
    time.sleep(10)
    username = driver.find_element_by_xpath('//input[@name="session[username_or_email]"]')
    username.send_keys(user)

    password = driver.find_element_by_xpath('//input[@name="session[password]"]')
    password.send_keys(my_password)
    password.send_keys(Keys.RETURN)
    sleep(1)

    # find search input and search for term
    search_input = driver.find_element_by_xpath('//input[@aria-label="Search query"]')
    search_input.send_keys(search_term)
    search_input.send_keys(Keys.RETURN)
    sleep(1)

    # navigate to historical 'latest' tab
    driver.find_element_by_link_text('Latest').click()

    # get all tweets on the page
    data = []
    tweet_ids = set()
    last_position = driver.execute_script("return window.pageYOffset;")
    scrolling = True

    while scrolling:
        page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
        for card in page_cards[-15:]:
            tweet = get_tweet_data(card)
            if tweet:
                tweet_id = ''.join(tweet)
                if tweet_id not in tweet_ids:
                    tweet_ids.add(tweet_id)
                    data.append(tweet)

        scroll_attempt = 0
        while True:
            # check scroll position
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(2)
            curr_position = driver.execute_script("return window.pageYOffset;")
            if last_position == curr_position:
                scroll_attempt += 1

                # end of scroll region
                if scroll_attempt >= 3:
                    scrolling = False
                    break
                else:
                    sleep(2)  # attempt another scroll
            else:
                last_position = curr_position
                break

    # close the web driver
    driver.close()

    # Data into MongoDB

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["cryptoCurrencyMarket"]
    mycol = mydb["bitcoin_tweets"]

    for i in data:
        jsn = {}
        jsn["UserName"] = i[0]
        jsn["Handle"] = i[1]
        jsn["Timestamp"] = i[2]
        jsn["Emojis"] = i[3]
        jsn["Comments"] = i[4]
        jsn["Likes"] = i[5]
        jsn["Retweets"] = i[6]
        print(jsn)
        x = mycol.insert_one(jsn)

if __name__ == "__main__":

    while True:
        twitter()
        time.sleep(3600)