from modules.g_app import AstralSheetScriptApi
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", type=str, help="script id")
    args = parser.parse_args()

    if args.id is None:
        print("error: where is script id?")
        exit()

    API = AstralSheetScriptApi(args.id)

    input()

    try:
        result = API.deploy(args.id)

        if "error" in result:
            print(f"error: {result}\n")
        else:
            print(result["deploymentId"])

    except Exception as ex:
        print(f"error: {ex}\n")
