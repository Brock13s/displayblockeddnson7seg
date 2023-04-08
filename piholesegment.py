from luma.core.interface.serial import spi, noop
from luma.led_matrix.device import max7219
from luma.led_matrix.device import sevensegment
from luma.core.legacy import show_message
from luma.core.legacy.font import proportional, CP437_FONT
#import requests
import threading
import time
import json
import subprocess

# Set up the MAX7219 display
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=1)
seg = sevensegment(device)

# Set up the Pi-hole API endpoint and API key
#api_endpoint = 'http://192.168.68.66/admin/api.php'
#api_key = '9b1a8a928675741a3bc2a87a4ff5ed0b22f86d695851e77e7ff9da8a6a90eb80'

# Keep track of the current blocked queries count
current_count = 0

# Define a function to handle display updates
def update_display():
    global current_count
    while True:
        # Retrieve the blocked queries count from Pi-hole
        try:
#            params = {'auth': api_key, 'summary': 'summary'}
#            response = requests.get(api_endpoint, params=params)
#            overall_stats = response.json()
            output = subprocess.check_output(["pihole", "-c", "-j"]).decode()
            overall_stats = json.loads(output)
            blocked_count = overall_stats['ads_blocked_today']
#            blocked_count = int(blocked_ads_str.replace(',', ''))
        except:
            # If there is an error retrieving the count, print an error message and skip this update
            print("Error retrieving blocked queries count")
            time.sleep(5)
            continue

        # If the blocked count has changed, update the display
        if blocked_count != current_count:
            current_count = blocked_count
            message = "{: >8}".format(str(blocked_count))
            print(message)
            if len(message) > seg.device.width:
                # If the message is too long to fit on the display, scroll it across the display
                show_message(seg.device, message, font=proportional(CP437_FONT), scroll_delay=0.05)
            else:
                # If the message fits on the display, display it directly
                seg.text = message

        time.sleep(1)

# Create a separate thread for display updates
update_thread = threading.Thread(target=update_display)
update_thread.daemon = True
update_thread.start()

# Keep the main thread running to handle user input or other tasks
while True:
    # Handle any user input or other tasks here
    time.sleep(1)
