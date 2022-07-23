# telegram-adder
Program to scrape telegram groups and channels and add them to other groups or channels

This program tries to use multiple telegram user accounts to add members to groups or channels.

It follows a round-robin pattern by using random clients from the pool of clients available and removing clients when flood error occurs.




USAGE
-------

pip install -r requirements.txt



TO SCRAPE GROUPS OR CHANNELS :

    # python3 teleScrapper.py
    
  
TO ADD MEMBERS TO A GROUP OR CHANNEL:

    To add Telegram accounts to the client pool, edit the config.json in the sessions folder with the required account details
    
    A demo is avialable in sessions folder

    # python3 addMembers.py
