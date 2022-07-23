from telethon import sync, TelegramClient, events, connection
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import (
    InputPeerEmpty,
    InputPeerChannel,
    ChannelParticipantsSearch,
)
from telethon.tl.functions.channels import GetParticipantsRequest
import os
import json
import sys


class Scrapper:
    def __init__(self):
        self.app_id = "APP ID NUMBER"
        self.app_hash = "APP HASH"
        self.app_name = "APP NAME"
        self.session_name = "SESSION NAME"
        self.phone = "PHONE NUMBER WITH COUNTRY CODE"
        self.client = self.groups = None
        self.aggressive = False  # change to true to scrape all members from a group
        self.members_from_group_limit = (
            200  # maximum number of people to scrape from a group
        )
        self.config_file = "config.json"

    def setupClient(self):
        try:
            self.client = TelegramClient(self.session_name, self.app_id, self.app_hash)
            self.client.connect()
            if not self.client.is_user_authorized():
                self.client.start(phone=self.phone)

            if self.client.is_user_authorized():
                print(f"[+] Client - {self.phone} successfully connected")
            else:
                print(f"[+] Client - {self.phone} failed to connect \n exiting...")
                sys.exit()
        except Exception as e:
            print(e)
            sys.exit()

    def cleanUp(self):
        self.client.disconnect()

    def saveData(self, data, filename):
        with open(filename, "w") as f:
            f.write(json.dumps(data, indent=4))

    def getMembers(self, targets):
        if os.path.exists("members.json"):
            os.remove("members.json")

        for target in targets:
            print("\n[*] Scrapping Memebers from group ", self.groups[target]["title"])

            offset = 0
            limit = 200
            target_grp = InputPeerChannel(
                self.groups[target]["id"], self.groups[target]["access_hash"]
            )

            try:

                while True:

                    participants = self.client(
                        GetParticipantsRequest(
                            target_grp,
                            ChannelParticipantsSearch(""),
                            offset,
                            min(self.members_from_group_limit-offset, limit),
                            hash=0,
                        )
                    )

                    if not participants.users:
                        break

                    offset += len(participants.users)

                    users = [
                        {
                            "name": (user.first_name if user.first_name else "")
                            + " "
                            + (user.last_name if user.last_name else ""),
                            "username": user.username if user.username else "",
                            "id": user.id,
                            "hash": user.access_hash,
                            "groupId": self.groups[target]["id"],
                            "groupTitle": self.groups[target]["title"],
                        }
                        for user in participants.users
                    ]

                    print("[+] Scrapped user count ", offset)

                    if os.path.exists("members.json"):
                        with open("members.json", "r") as f:
                            prev_data = f.read()

                        if prev_data:
                            prev_data = json.loads(prev_data)
                            prev_data += users
                            input(len(prev_data))
                            with open("members.json", "w") as f:
                                f.write(json.dumps(prev_data, indent=4))
                    else:
                        with open("members.json", "w") as f:
                            f.write(json.dumps(users, indent=4))
                            
                    if offset >= self.members_from_group_limit and not self.aggressive:
                        break

                print("[+] successfully scraped group members")

            except Exception as e:
                print(e, "- getMembers method")
                print("[+] Partially/Failed scrapping group members")

    def scrapeData(self):
        if self.client is None:
            self.setupClient()

        print("[*] Getting Data ... \n")

        if os.path.exists("groups.json"):
            ans = input(
                "Found groups.json file, Do you want to add members from these groups[y/n]"
            )
            if ans.lower() == "y":
                with open("groups.json", "r") as f:
                    self.groups = json.loads(f.read())

        if not self.groups:
            last_date = None
            chunk_size = 200

            res = self.client(
                GetDialogsRequest(
                    offset_date=last_date,
                    offset_id=0,
                    offset_peer=InputPeerEmpty(),
                    limit=chunk_size,
                    hash=0,
                )
            )
            res = res.to_dict()

            self.groups = [
                chat
                for chat in res.get("chats")
                if chat.get("megagroup") is not None
                and chat.get("access_hash") is not None
            ]

            print(f"[*] Saving Group metedata to {self.config_file}\n")
            meta_data = [
                {
                    "id": grp["id"],
                    "access_hash": grp["access_hash"],
                    "title": grp["title"],
                    "megagroup": grp["megagroup"],
                }
                for grp in self.groups
            ]
            self.saveData(data=meta_data, filename="groups.json")

        for i, grp in enumerate(self.groups):
            print(
                f"[{i}] {grp['title']} ( {'Group' if grp['megagroup'] else 'Channel'} )"
            )

        targets = input(
            "\n[*] Please enter the index number of the groups you want to scrape sepereated by a space :"
        )
        targets = [int(i) for i in targets.split(" ")]

        if not len(targets):
            print("[-] No groups selected \n exiting")
            sys.exit()

        self.getMembers(targets)


def main():
    scrapper = Scrapper()
    scrapper.scrapeData()
    scrapper.cleanUp()


if __name__ == "__main__":
    main()
