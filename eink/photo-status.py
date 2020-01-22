#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import argparse
import os

import logging
from waveshare_epd import epd2in13bc
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

def draw_gauge(label, percent, screen_height, image_draw, font, start_width):
    spacer = 10
    image_draw.text((0, start_width), label, font = font, fill = 0)
    pct_size = image_draw.textsize(str(percent)+'%', font = font)
    image_draw.text((screen_height / 2 - pct_size[0], start_width), str(percent)+'%', font = font, fill = 0)
    image_draw.rectangle([screen_height / 2 + spacer, start_width, screen_height - 1, start_width + pct_size[1]], fill = 1, outline=0)
    image_draw.rectangle([screen_height / 2 + spacer + 1, start_width + 1, screen_height - ((screen_height / 2 - spacer - 3) * (100 - percent) / 100) - 2, start_width + pct_size[1] - 1], fill = 0, outline=1)
    return start_width + pct_size[1]

def draw_counter(value, screen_height, image_draw, font, start_width, end_width):
    value_size = image_draw.textsize(value, font = font)
    image_draw.text((screen_height / 2 - value_size[0] / 2, start_width + (end_width - start_width) / 2 - value_size[1] / 2), value, font = font, fill = 0)

def draw_screen(battery_percent, sd_free_percent, photo_count):
    try:
        logging.debug("Loading fonts")    
        font_file = os.path.join(resources_dir,'OCRA.ttf')
        font_small = ImageFont.truetype(font_file, 12)
        font_medium = ImageFont.truetype(font_file, 16)
        font_large = ImageFont.truetype(font_file, 40)

        logging.info("Initializing screen")
        epd = epd2in13bc.EPD()
        epd.init()
        time.sleep(1)
    
        logging.debug("Preparing image") 
        black_image = Image.new('1', (epd.height, epd.width), 255)  # 212*104
        red_image = Image.new('1', (epd.height, epd.width), 255)  # 212*104
        black_draw = ImageDraw.Draw(black_image)    
        red_draw = ImageDraw.Draw(red_image)

        if battery_percent <= 25:
            bat_end = draw_gauge('Batt.', battery_percent, epd.height, red_draw, font_medium, 0)
        else:
            bat_end = draw_gauge('Batt.', battery_percent, epd.height, black_draw, font_medium, 0)

        if sd_free_percent <= 15:
            sd_end = draw_gauge('SD', sd_free_percent, epd.height, red_draw, font_medium, bat_end + 5)
        else:
            sd_end = draw_gauge('SD', sd_free_percent, epd.height, black_draw, font_medium, bat_end + 5)

        draw_counter(str(photo_count), epd.height, black_draw, font_large, sd_end + 1, epd.width - 1)

        logging.info("Updating screen")

        epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
        time.sleep(2)
    
        logging.info("Sleep mode")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)
    
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd2in13bc.epdconfig.module_exit()
        exit()

def main():
    logging.basicConfig(level=logging.INFO)

    battery = 0
    sd = 0
    photos = 0
    
    parser = argparse.ArgumentParser(description='Update e-ink display with status information')
    parser.add_argument('-b', '--battery', type=int, required=True, help='Battery charge percentage (0-100)')
    parser.add_argument('-s', '--sd', type=int, required=True, help='Free storage space percentage (0-100)')
    parser.add_argument('-c', '--counter', type=int, required=True, help='Photo counter')
    
    args = parser.parse_args()

    draw_screen(args.battery, args.sd, str(args.counter))

if __name__ == "__main__":
    main()
