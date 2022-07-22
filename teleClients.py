from telethon import sync, TelegramClient, events, connection
import json
import os


class TeleClients:
    def __init__(self):
        self.config_file = "config.json"
        self.clients = []
        self.active_clients = []
        self.base_path = "sessions"

    def initClients(self):
        config_file = os.path.join(self.base_path, self.config_file)

        if not os.path.exists("sessions") or not os.path.exists(config_file):
            print("[-] Required session files missing /n exiting...")
            return None

        with open(config_file, "r") as f:
            data = f.read()

        if data:
            self.clients = json.loads(data)
            for client in self.clients:
                try:
                    tele_client = TelegramClient(
                        os.path.join(
                            self.base_path,
                            client.get("session_name")
                            if client.get("session_name")
                            else client["phone"],
                        ),
                        client["app_id"],
                        client["app_hash"],
                    )
                    tele_client.connect()
                    if not tele_client.is_user_authorized():
                        tele_client.start(phone=client["phone"])

                    if tele_client.is_user_authorized():
                        print(f'[+] Client - {client["phone"]} successfully connected')
                        self.active_clients.append(tele_client)
                    else:
                        print(
                            f'[+] Client - {client["phone"]} failed to connect \n exiting...'
                        )
                except Exception as e:
                    print(e)
                    continue

            return self.active_clients
