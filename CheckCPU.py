import psutil
import telepot
import time
import threading

class CheckStatus:
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3

def read_config():
    config = {}
    with open('config.txt', 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key.strip()] = value.strip()
    return config

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_ram_usage():
    return psutil.virtual_memory().percent

def get_disk_usage():
    return psutil.disk_usage('/').percent

def send_message(token, chat_id, message):
    bot = telepot.Bot(token)
    bot.sendMessage(chat_id, message, parse_mode='Markdown')  # Set parse_mode to 'Markdown'

def main(config, status):
    token = config.get('token')
    chat_id = config.get('chat_id')
    interval = int(config.get('interval', 60))  # default interval is 60 seconds
    machine_name = config.get('machine_name', 'This machine')  # Default to 'This machine' if not provided

    while status[0] != CheckStatus.STOPPED:
        if status[0] == CheckStatus.RUNNING:
            cpu_usage = get_cpu_usage()
            ram_usage = get_ram_usage()
            disk_usage = get_disk_usage()

            # Format message using Markdown
            message = f"*{machine_name}*\nCPU Usage: {cpu_usage}%\nRAM Usage: {ram_usage}%\nDisk Usage: {disk_usage}%"
            send_message(token, chat_id, message)

        time.sleep(interval)

def handle_message(msg, config, status):
    content_type, _, _ = telepot.glance(msg)
    if content_type == 'text':
        command = msg['text'].lower()
        if command == '/pause':
            status[0] = CheckStatus.PAUSED
            print("Status updated to PAUSED")
            send_message(config['token'], config['chat_id'], "Đã ngừng theo dõi CPU.")
        elif command == '/resume':
            status[0] = CheckStatus.RUNNING
            print("Status updated to RUNNING")
            send_message(config['token'], config['chat_id'], "Đã tiếp tục theo dõi CPU.")

if __name__ == "__main__":
    config = read_config()

    status = [CheckStatus.RUNNING]

    main_thread = threading.Thread(target=main, args=(config, status))
    main_thread.start()

    token = config.get('token')
    bot = telepot.Bot(token)
    bot.message_loop(lambda msg: handle_message(msg, config, status))
    while True:
        time.sleep(10)  # Keep the thread alive
