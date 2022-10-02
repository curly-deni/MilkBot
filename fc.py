import argparse
from selenium import webdriver
from time import sleep

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--link", type=str, help="link")
    args = parser.parse_args()

    firefox_options = webdriver.FirefoxOptions()
    firefox_options.headless = True

    input()
    browser = webdriver.Firefox(options=firefox_options)
    browser.get(args.link)
    sleep(5)
    print("ok")
    browser.quit()
    exit()
