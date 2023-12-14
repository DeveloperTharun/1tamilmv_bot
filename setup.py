import os
import telegram
from telegram.ext import Updater
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
import requests
import re

TOKEN = 'YOUR_BOT_TOKEN'
CHANNEL_ID = '@your_channel_username'  # Replace with your actual channel username

bot = telegram.Bot(token=TOKEN)

def send_to_telegram(message):
    bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode='markdown')

def tamilmv():
    mainUrl = 'https://www.1tamilmv.phd/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'Connection': 'Keep-alive',
        'sec-ch-ua-platform': '"Windows"',
    }

    global movie_dict
    movie_dict = {}
    global real_dict
    real_dict = {}
    global movie_list
    movie_list = []

    num = 0

    web = requests.request("GET", mainUrl, headers=headers)
    soup = BeautifulSoup(web.text, 'lxml')
    linker = []
    badtitles = []

    temps = soup.find_all('div', {'class': 'ipsType_break ipsContained'})

    for i in range(16):
        title = temps[i].findAll('a')[0].text
        badtitles.append(title)
        links = temps[i].find('a')['href']
        content = str(links)
        linker.append(content)

    for element in badtitles:
        movie_dict[element.strip()] = None

    movie_list = list(movie_dict)

    # File to store processed magnet links
    processed_links_file = 'processed_links.txt'

    # Load previously processed magnet links
    processed_links = set()
    if os.path.exists(processed_links_file):
        with open(processed_links_file, 'r') as file:
            processed_links = set(file.read().splitlines())

    for url in linker:
        html = requests.request("GET", url)
        soup = BeautifulSoup(html.text, 'lxml')
        pattern = re.compile(r"magnet:\?xt=urn:[a-z0-9]+:[a-zA-Z0-9]{40}")
        bigtitle = soup.find_all('a')
        alltitles = []
        mag = []
        filelink = []  # Added this line to fix the NameError
        for i in soup.find_all('a', href=True):
            if i['href'].startswith('magnet'):
                mag.append(i['href'])

        for a in soup.findAll('a', {"data-fileext": "torrent", 'href': True}):
            filelink.append(a['href'])  # Added this line to fix the NameError

        for title in bigtitle:
            if title.find('span') is None:
                pass
            else:
                if title.find('span').text.endswith('torrent'):
                    alltitles.append(title.find('span').text[19:-8])

        for p in range(0, len(mag)):
            try:
                real_dict.setdefault(movie_list[num], [])
                update_message = f"*{alltitles[p]}* -->\n🧲 `{mag[p]}`\n🗒️->[Torrent file]({filelink[p]})"
                # Check if the magnet link is new
                if mag[p] not in processed_links:
                    real_dict[movie_list[num]].append(update_message)
                    # Send the update to Telegram
                    send_to_telegram(update_message)
                    # Add the magnet link to processed_links set
                    processed_links.add(mag[p])
            except:
                pass

        num = num + 1

    # Save processed magnet links back to the file
    with open(processed_links_file, 'w') as file:
        file.write('\n'.join(processed_links))

def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(tamilmv, 'interval', minutes=30)  # Adjust interval as needed
    scheduler.start()
    
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

if __name__ == '__main__':
    main()
