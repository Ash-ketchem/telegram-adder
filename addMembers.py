from telethon import sync, TelegramClient, events, connection
from telethon.tl.types import InputPeerChannel, InputPeerUser
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors.rpcerrorlist import (
    PeerFloodError,
    UserPrivacyRestrictedError,
    FloodWaitError,
)
import time
import os
import json
from sys import exit
import random

from teleClients import TeleClients


class AddMembers:
    def __init__(self):
        self.client_int = TeleClients()
        self.clients = self.client_int.initClients()
        self.groups = []
        self.members_to_add = []
        self.max_memebers_to_add = 1000
        self.round_robin = True

    def addMembers(self):
        if not self.clients:
            print("[-] No clients connected \nexiting...")
            exit()

        if not os.path.exists("groups.json") or not os.path.exists("members.json"):
            print(
                "[-] groups.json not found\nplease use the scrapper to scrape group members first\nexiting..."
            )
            exit()

        with open("members.json", "r") as f:
            users = f.read()
            if users:
                self.members_to_add = json.loads(users)

        if not self.members_to_add:
            print("[-] No members found \nexiting...")
            exit()

        with open("groups.json", "r") as f:
            grps = f.read()
            if grps:
                self.groups = json.loads(grps)

        if not self.groups:
            print("[-] No groups found \nexiting...")
            exit()

        self.clients = [
            {"id": index, "client": client, "active": True, "state": "ready"}
            for index, client in enumerate(self.clients)
        ]

        print(f"[+] No .of working clients {len(self.clients)}\n")

        # removing clients from users list
        clients_ids = [client["client"].get_me().id for client in self.clients]
        self.members_to_add = [
            user for user in self.members_to_add if user["id"] not in clients_ids
        ]

        for i, grp in enumerate(self.groups):
            print(
                f"[{i}] {grp['title']} ( {'Group' if grp['megagroup'] else 'Channel'} )"
            )

        target = int(
            input(
                "\n[*] Please enter the index number of the group/channel you want to add members to :"
            )
        )
        target_entity = InputPeerChannel(
            self.groups[target]["id"], self.groups[target]["access_hash"]
        )
        print("\n\n")

        i = 0
        while i <= len(self.members_to_add):
            try:
                if not self.clients:
                    print("[- No active clients \nexiting...")
                    exit()

                if i % 20 == 0 and i != 0:
                    print("[*] Sleeping for 15 minutes")
                    time.sleep(15 * 60)

                print(
                    f"[*][{i}] adding to channel - ", self.members_to_add[i].get("name")
                )
                user_to_add = InputPeerUser(
                    int(self.members_to_add[i]["id"]),
                    int(self.members_to_add[i]["hash"]),
                )

                # find a working client
                client = list(
                    filter(
                        lambda client: client["active"] and client["state"] == "ready",
                        self.clients,
                    )
                )[random.choice(range(len(self.clients)))]
                client["client"](InviteToChannelRequest(target_entity, [user_to_add]))

            except PeerFloodError:
                print("[-] Peer flood error")
                # traceback.print_exc()
                print("[-] removing client")
                client["client"].disconnect()
                self.clients.pop(client["id"])
                print(f"[*] No .of remaining clients {len(self.clients)}\n")

            except UserPrivacyRestrictedError:
                print(f"[-][{i}] user privacy error")
                print("[*] continuing\n")
                self.members_to_add.pop(i)
                i += 1

            except FloodWaitError:
                print("[-] flood wait error")
                # traceback.print_exc()
                print("[-] removing client")
                client["client"].disconnect()
                self.clients.pop(client["id"])
                print(f"[*] No .of remaining clients {len(self.clients)}\n")

            except Exception as e:
                print(f"[-][{i}] ", e)
                print("[*] continuing\n")
                self.members_to_add.pop(i)
                i += 1

            else:
                print(
                    f"[+][{i}] Added member "
                    + self.members_to_add[i]["name"]
                    + " successfully !!"
                )
                self.members_to_add.pop(i)
                i += 1
                sleep_time = random.randint(60, 180)
                print(f"[*] sleeping {sleep_time} seconds\n")
                time.sleep(sleep_time)  # seeping between 1-3 minutes

        with open("members.json", "w") as f:
            print("[*] Removing added members from membors.json")
            f.write(json.dumps(self.members_to_add, indent=4))


if __name__ == "__main__":
    adder = AddMembers()
    adder.addMembers()
