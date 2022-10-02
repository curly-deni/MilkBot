from modules.set_gcp import BrowserControl
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", type=str, help="script id")
    parser.add_argument("-p", "--path", type=str, help="profile path")
    parser.add_argument("-g", "--gcp", type=int, help="gcp id")
    args = parser.parse_args()

    if None in [args.id, args.path, args.gcp]:
        print("error")
        exit()

    input()
    browser = BrowserControl(args.path)
    browser.set_gcp(args.gcp, args.id)
    browser.browser.quit()
    print("ok")
    exit()
