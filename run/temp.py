#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import requests
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in13_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.INFO)

try:
    logging.info("temp cpu")
    
    epd = epd2in13_V2.EPD()

    # Drawing on the image
    font15 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font40 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 40)

    
    # # partial update
    logging.info("4.show time...")
    time_image = Image.new('1', (epd.height, epd.width), 255)
    time_draw = ImageDraw.Draw(time_image)
    
    epd.init(epd.FULL_UPDATE)
    epd.displayPartBaseImage(epd.getbuffer(time_image))
    
    epd.init(epd.PART_UPDATE)
    num = 0
    failedtimes = 0
    while (True):
        try:
            response = requests.get("http://10.10.10.1:3000/signalk/v1/api/vessels/self/navigation", timeout=10)
        except Exception as e:
            logging.info("Godmiljaar")
            
            if failedtimes == 0:
                logging.info(failedtimes)
                epd.init(epd.FULL_UPDATE)
                imageclear = Image.new('1', (epd.height, epd.width), 255)
                drawclear = ImageDraw.Draw(imageclear)
                drawclear.text((15, 40), "Where is WALVS?", font = font24, fill = 0)
                epd.display(epd.getbuffer(imageclear))
            failedtimes = failedtimes + 1
            time.sleep(30)
            continue
        
        
        
        epd.init(epd.PART_UPDATE)
        time_draw.rectangle((15, 15, 250, 115), fill = 255)
        
        #response = requests.get("http://10.10.10.1:3000/signalk/v1/api/vessels/self/navigation")      
        temp = response.json()
        failedtimes = 0
        #logging.info(temp)
        speedstring = str(temp["averageSpeedOverGround"]["value"])[:5] + " kts"
        time_draw.text((15, 15), str(speedstring), font = font40, fill = 0)
        
        #coursestring = "C: " + str(temp["courseOverGroundTrue"]["value"])
        coursestring = str(temp["gnss"]["antennaAltitude"]["value"])

        time_draw.text((15, 70), str(coursestring[:10]), font = font40, fill = 0)
        epd.displayPartial(epd.getbuffer(time_image))
        time.sleep(2)
        num = num + 1
        if(num == 30):
            epd.init(epd.FULL_UPDATE)
            epd.Clear(0xFF)
            #imageclear = Image.new('1', (epd.height, epd.width), 255)
            #epd.display(epd.getbuffer(imageclear))
            num=0

    logging.info("Clear...")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
    
    logging.info("Goto Sleep...")
    epd.sleep()
    time.sleep(3)
    epd.Dev_exit()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in13_V2.epdconfig.module_exit()
    exit()
