from base.bot import qaz
import discord
import dotenv
import os

dotenv.load_dotenv()


def main():
    token = os.getenv("TOKEN")
    if not token:
        raise ValueError("TOKEN Environment variable is not set")

    print("[+] Creating bot instance.")
    bot = qaz()
    print("[+] Bot instance created, starting connection.")
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("[!] Bot Token is invalid, check again.")
        return
    except discord.ConnectionClosed:
        print("[!] Discord conn closed.")
        return
    except Exception as e:
        print(f"[!] Error starting bot: {e}")
        return


if __name__ == "__main__":
    main()
