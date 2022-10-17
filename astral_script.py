from modules.g_app import AstralSheetScriptApi
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", type=str, help="script id")
    parser.add_argument("-d", "--deploy", help="deploy script", action="store_true")
    parser.add_argument("-n", "--next", help="next round", action="store_true")
    parser.add_argument("-r", "--run", help="run game", action="store_true")
    parser.add_argument("-s", "--stop", help="stop game", action="store_true")
    args = parser.parse_args()

    if args.id is None:
        print("error: where is script id?")
        exit()

    API = AstralSheetScriptApi(args.id)

    input()

    try:
        if args.deploy:
            result = API.deploy(args.id)
        if args.next:
            result = API.next_round()
        if args.run:
            result = API.start_game()
        if args.stop:
            result = API.end_game()

        if "error" in result:
            print(f"error: {result}\n")
        else:
            if args.deploy:
                print(result["deploymentId"])
            else:
                print(result)

    except Exception as ex:
        print(f"error: {ex}\n")
