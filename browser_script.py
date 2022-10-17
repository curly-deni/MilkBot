import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--link", type=str, help="link")
    parser.add_argument("-i", "--id", type=str, help="script id")
    parser.add_argument("-p", "--path", type=str, help="profile path")
    parser.add_argument("-g", "--gcp", type=int, help="gcp id")

    args = parser.parse_args()

    if None in [args.id, args.path, args.gcp]:
        from selenium import webdriver
        from time import sleep

        firefox_options = webdriver.FirefoxOptions()
        firefox_options.headless = True

        input()
        browser = webdriver.Firefox(options=firefox_options)
        browser.get(args.link)
        sleep(5)
        print("ok")
        browser.quit()
        exit()
    else:
        from modules.set_gcp import BrowserControl

        input()
        browser = BrowserControl(args.path)
        browser.set_gcp(args.gcp, args.id)
        browser.browser.quit()
        print("ok")
        exit()
