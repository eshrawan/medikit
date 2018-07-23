"""
a program for a working model that sets and gives reminders for specialized mdeicines. it can be used
for individuals, families, and works to model a system of foolproof medicine usage in the government. 

author: @eshrawan

Copyright 2018, Eshita Shrawan, All Rights Reserved.
"""

# importing necessary odules and packages
import pygame
import csv
import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO
import re
import pyttsx
import datetime, time
import evdev
import cv2
import numpy
from evdev import InputDevice, categorize  
import threading
import os
from glob import glob
import serial
from smbus import SMBus
from subprocess import check_output, CalledProcessError
import subprocess
from pyfingerprint.pyfingerprint import PyFingerprint
from urllib2 import Request,urlopen,URLError,HTTPError

site = 'http://www.iotgecko.com/IOTHit.aspx?Id=e.shrawan@gmail.com&Pass=4496&Data=' #adding for cloud storage

port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=0.5)

dates = ('01','02','03','04','05','06','07','08','09','10',
        '11','12','13','14','15','16','17','18','19','20',
        '21','22','23','24','25','26','27','28','29','30','31')

months = ('01','02','03','04','05','06','07','08','09','10','11','12')

hours = ('00','01','02','03','04','05','06','07','08','09','10',
         '11','12','13','14','15','16','17','18','19','20',
         '21','22','23')

minutes = ('00','01','02','03','04','05','06','07','08','09','10',
           '11','12','13','14','15','16','17','18','19','20',
           '21','22','23','24','25','26','27','28','29','30',
           '31','32','33','34','35','36','37','38','39','40',
           '41','42','43','44','45','46','47','48','49','50',
           '51','52','53','54','55','56','57','58','59',)

days = ('Mon','Tue','Wed','Thu','Fri','Sat','Sun')
t = 0
medicine_dosage = []
medicine_names = []
patient_names = []
med_taken=['time']
patient_no = []
patient_id = ''
no_medicine = 0
no_dosage = 0
n = 0
dosag = {}
snooze_time = 9999
diff=0
diff2=0
global destination
snooze = False
not_snooze = False
num = None
global start1
edit_date = True
edit_month = False
edit_year = False
edit_hour = False
edit_minute = False
edit_day = False
flag=0
path = None

ok = "OK"
rcv = None

global sys
global dia
global pulse
global cap
## datestring=' %d/%m/%Y %H:%M'
date = (int)(datetime.datetime.now().strftime('%d')) - 1
month = (int)(datetime.datetime.now().strftime('%m')) - 1
year = (int)(datetime.datetime.now().strftime('%Y')) 
hour = (int)(datetime.datetime.now().strftime('%H')) 
minute = (int)(datetime.datetime.now().strftime('%M')) 
day = (int)(datetime.datetime.now().strftime('%d')) - 1
datestring='%H:%M'


def get_usb_devices():
    sdb_devices = map(os.path.realpath, glob('/sys/block/sd*'))
    usb_devices = (dev for dev in sdb_devices
        if 'usb' in dev.split('/')[5])
    return dict((os.path.basename(dev), dev) for dev in usb_devices)

def get_mount_points(devices=None):
    devices = devices or get_usb_devices() # if devices are None: get_usb_devices
    output = check_output(['mount']).splitlines()
    is_usb = lambda path: any(dev in path for dev in devices)
    usb_info = (line for line in output if is_usb(line.split()[0]))
    return [(info.split()[0], info.split()[2]) for info in usb_info]



def printit():
    threading.Timer(1.0, printit).start()
    lcd.set_cursor(0,0)
    lcd.message(datetime.datetime.now().strftime(datestring))



                            
scancodes = {
    # Scancode: ASCIICode
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 14: u'BKSP', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 28: u'ENTER',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L',
    44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 57: u' ', 106: u'RIGHT', 108: u'DOWN', 105: u'LEFT', 103: u'UP',
    82: u'0',79: u'1',80: u'2',81: u'3',75: u'4',76: u'5',77: u'6',71: u'7',72: u'8',73: u'9',96: u'R_ENTER',111: u'DEL'
}



# internet connection via GSM
def check_connectivity():
    try:
        urlopen(site,timeout = 2)
        return True
    except:
        return False


def connect_wifi() :
    lcd.clear()
    lcd.message('connecting to \ninternet')
    time.sleep(1)
    
    t1 = datetime.now()
    while not check_connectivity():
        t2 = datetime.now()
        delta = t2 - t1
        time_elapse = delta.total_seconds()
        if time_elapse > 10:
            lcd.clear()
            lcd.message('Error: Check\nInternet Connecn ')
            print "error check you internet connection"
            main = False
            while GPIO.input(button) == True:
                lcd.clear()
                lcd.message('Press reset to\nrestart')
                time.sleep(0.5)
            break
def hit_link(id,name,med_taken,med_name,health_status,doc_name,doc_no):
       link=site+med_taken+'*'+med_name+'*'+id+'*'+name+'*'+health_status+'*'+doc_name+'*'+doc_no+'*'+datetime.datetime.now().strftime('%d/%m/%Y*%H:%M')
       link=link.replace(' ','')
       print'link=',link
       
       while True:
                req = Request(link)
                try:
                    response = urlopen(req,timeout = 10)
                    no_error = True
                                
                except:
                    print "error opening site"
                    lcd.clear()
                    lcd.message('Error: Check\nInternet Connecn ')
                    time.sleep(2)
                    error = True
                    no_error = False
                   
                if no_error:
                    html = str(response.read())
                    lcd.clear()
                    lcd.message('data updated..')
                    time.sleep(2)
                    print data
                    break
        
        
# patient enrollment


def enrol_patient():
          global data_location  
          buff=[]
          k=''
          flag=0
          k=enroll()
          patient_buff = []
          if k.find('*')>=0:
                lcd.clear()
                lcd.message(' Patient Enrollment')
                lcd.set_cursor(0,1)
                lcd.message('Patient already\n\nexist at id=')
                lcd.message(k[0:-1])                
                print k[0:-1]
                time.sleep(2)
                flag=2

          elif k!='zero':
                patient_buff.append(k)
                print patient_buff
                c=2
                lcd.clear()
                lcd.show_cursor(1)
                lcd.message(' Patient Enrollment')
                lcd.set_cursor(0,1)
                lcd.message('Names of Patient:')
                p_name = keyboard(0,c,data_type='all')
                print p_name
                patient_buff.append(p_name)
                print patient_buff
                lcd.clear()
                lcd.message('  Patient Enrollment      ')
                lcd.set_cursor(0,1)
                lcd.message('Patient Mob no:')
                p_no = keyboard(0,c,data_type='num')
                patient_buff.append(p_no)
                lcd.clear()
                lcd.message('  Patient Enrollment      ')
                lcd.set_cursor(0,1)
                lcd.message('Doctor name:')
                p_name = keyboard(0,c,data_type='all')
                patient_buff.append(p_name)
                lcd.clear()
                lcd.message('  Patient Enrollment      ')
                lcd.set_cursor(0,1)
                lcd.message('Doctor Mob no:')
                p_no = keyboard(0,c,data_type='num')
                patient_buff.append(p_no)
                print patient_buff
                with open(os.path.join(data_location,'patient_list.csv'), 'rb') as f:
                        reader = csv.reader(f)
                        # read file row by row
                        for row in reader:
                            print row
                            buff.append(row)
                print buff
                buff.append(patient_buff)
                with open(os.path.join(data_location,'patient_list.csv'), 'wb') as csvfile:
                        filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        for row in buff:
                            print row
                            filewriter.writerow(row)
                flag=1
          if flag == 1:
             while True:
                
                lcd.clear()
                lcd.message('Enter number of\nMedicines:')
                lcd.set_cursor(0,3)
                lcd.message('Press ESC to go back')
                lcd.show_cursor(1)
                num = keyboard(10,1,data_type='num')
                lcd.show_cursor(0)
                lcd.clear()
                if not num:
                    lcd.message('    SET Reminder    ')
                else:    
                    no_medicine = int(num,base=10)
                    lcd.message('Names of Medicines:')
                    lcd.show_cursor(1)
                    print 'num =' ,no_medicine
                    medicine_names = [None] * no_medicine
                    print 'medicine_names= ',medicine_names
                    c = 1
                    for x in range(0,no_medicine):
                        print x
                        if c>3:
                            lcd.clear()
                            lcd.message('Names of Medicines:')
                            c = 1  
                        lcd.set_cursor(0,c)
                        lcd.message(str(x+1) + ')')
                        name = keyboard(2,c,data_type='all')
                        medicine_names[x] = name
                        c = c+1
                    menu = 1
                    print 'medicine_names= ',medicine_names
                   
                    lcd.clear()
                    lcd.message('Enter number of \ndosage: ')
                    lcd.show_cursor(1)
                    lcd.set_cursor(0,3)
                    lcd.message('Press ESC to go back')
                    lcd.show_cursor(1)
                    num = keyboard(7,1,data_type='num')
                    lcd.clear()
                    lcd.show_cursor(0) 
                    if not num:
                        lcd.message('    SET Reminder    ')
                    else:
                        lcd.message('Set Time for dosage:')
                        lcd.show_cursor(1)
                        no_dosage = int(num,base=10)
                        print 'num of dosage =' ,no_dosage
                        medicine_dosage = [None] * no_dosage
                        print 'medicine_dosage= ',medicine_dosage

                        print 'ok this is it'
                        c = 1
                        for x in range(0,no_dosage):
                            print x
                            if c>3:
                                lcd.clear()
                                lcd.message('Time for dosage:')
                                c = 1     
                            lcd.set_cursor(0,c)
                            lcd.message(str(x+1) + ')')
                            edit_hour = True
                            edit_minute = False
                            hour = (int)(datetime.datetime.now().strftime('%H'))
                            minute = (int)(datetime.datetime.now().strftime('%M'))
                            lcd.set_cursor(2,c)
                            lcd.message(datetime.datetime.now().strftime(datestring))
                            lcd.set_cursor(3,c)
                            
                            while True:
                                key = keyboard(0,0,data_type='arrow')
                                if key == 'UP':
                                    if edit_hour:


                                        if hour < 23:
                                            hour = hour + 1
                                        else:
                                            hour = 0
                                        lcd.set_cursor(2,c)
                                        lcd.message(hours[hour])
                                        lcd.set_cursor(3,c)
                                    if edit_minute:
                                        if minute < 59:
                                            minute = minute + 1
                                        else:
                                            minute = 0
                                        lcd.set_cursor(5,c)
                                        lcd.message(minutes[minute])
                                        lcd.set_cursor(6,c)

                                elif key == 'DOWN':
                                    if edit_hour:
                                        if hour > 0:
                                            hour = hour - 1
                                        else:
                                            hour = 23
                                        lcd.set_cursor(2,c)
                                        lcd.message(hours[hour])
                                        lcd.set_cursor(3,c)
                                    if edit_minute:
                                        if minute > 0:
                                            minute = minute - 1
                                        else:
                                            minute = 59
                                        lcd.set_cursor(5,c)
                                        lcd.message(minutes[minute])
                                        lcd.set_cursor(6,c)
                                    
                                elif key == 'RIGHT' or key == 'LEFT':
                                    if edit_hour:
                                        lcd.set_cursor(6,c)
                                        edit_hour = False
                                        edit_minute = True
                                    elif edit_minute:
                                        lcd.set_cursor(3,c)
                                        edit_hour = True
                                        edit_minute = False
                                                
                                elif key == 'ENTER' or key == 'R_ENTER':
                                    medicine_dosage[x] = hours[hour] + ':' + minutes[minute]
                                    c = c+1
                                    break

                    lcd.clear()
                    lcd.message('Press DEL to delet\nMedicine from Dose\nPress ENTR to save\nPress any key ->')
                    speak('Press delete to remove Medicine from Dose, Press ENTR to save')
                    key = keyboard(0,0,data_type='arrow')
                    no_dosage = len(medicine_dosage)
                    for x in range(0,no_dosage):
                        #dose_medicines = [None] * len(medicine_names)
                        dose_medicines = list(medicine_names)
                        print 'medicine_names= ',medicine_names    
                        print 'dose_medicines= ', dose_medicines
                        lcd.clear()
                        lcd.message(medicine_dosage[x] + ' Dose Medicines')
                        lists = len(dose_medicines)
                        temp_r = 0
                        if lists<=3:
                            v=lists
                        else:
                            v=3
                        remove_num = 0
                        xr = 1
                        while True:
                            q=1
                            for w in range(temp_r,v):
                                lcd.set_cursor(0,q)
                                lcd.message(str(w+1) + ')' + dose_medicines[w])
                                q=q+1
                            lcd.show_cursor(1)
                            lcd.blink(1)
                            while True:
                                lcd.set_cursor(0,xr)
                                print 'remove_num =', remove_num , 'xr=' ,xr
                                key = keyboard(0,0,data_type='arrow')
                                if key == 'DOWN' and remove_num < lists-1:
                                    xr=xr+1
                                    remove_num = remove_num + 1
                                    if xr>3:
                                        temp_r = remove_num
                                        v = temp_r + 3
                                        if v>lists:
                                            v=lists
                                        xr = 1
                                        break
                                elif key == 'UP' and remove_num > 0:
                                    xr=xr-1
                                    remove_num = remove_num - 1
                                    if xr<1:
                                        temp_r = remove_num - 2
                                        v = temp_r + 3
                                        if v<3:
                                            v=3
                                        xr = 3
                                        break
                                elif key == 'ENTER' or key == 'R_ENTER':
                                    dosag['dose'+str(x)] = dose_medicines
                                    new_buff=[]
                                    med_buff=[]
                                    med_buff.append(k)
                                    med_buff.append(medicine_dosage[x])
                                    x=len(dose_medicines)
                                    for y in range(0,x):
                                            med_buff.append( dose_medicines[y])

                                    with open(os.path.join(data_location,'med_list.csv'), 'rb') as f:
                                            reader = csv.reader(f)
                                            # read file row by row
                                            for row in reader:
                                                print row
                                                new_buff.append(row)
                                    print new_buff
                                    new_buff.append(med_buff)
                                    with open(os.path.join(data_location,'med_list.csv'), 'wb') as csvfile:
                                            filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                                            for row in new_buff:
                                                print row
                                                filewriter.writerow(row)
                                    break

                                elif key == 'DEL':
                                    del dose_medicines[remove_num]
                                    lists = len(dose_medicines)
                                    print 'medicine_names length= ', lists
                                    print 'medicine_names= ',medicine_names    
                                    temp_r = 0
                                    if lists<=3:
                                        v=lists
                                    else:
                                        v=3
                                    remove_num = 0
                                    xr = 1
                                    break
                            if key == 'ENTER' or key == 'R_ENTER':
                                break
                            lcd.clear()
                            lcd.message(medicine_dosage[x] + 'dose Medicines')
                lcd.show_cursor(0)
                break
          elif flag == 2 :
                    k=k.replace('*','')
                    menu = 1
                    lcd.clear()
                    lcd.message(' Add/Remove Medcine ')
                    while True:
                        backup_of_p_list=[]
                        edited_p_list=[]
                        backup_of_med_list=[]
                        edited_med_list=[]
                        if menu == 1: 
                            print 'getting med_list back_up'
                            with open(os.path.join(data_location,'med_list.csv'), 'rb') as f:
                                            reader = csv.reader(f)
                                            # read file row by row
                                            for row in reader:
                                                print row
                                                backup_of_med_list.append(row)
                                                
                            with open(os.path.join(data_location,'patient_list.csv'), 'rb') as f:
                                            reader = csv.reader(f)
                                            # read file row by row
                                            for row in reader:
                                                print row
                                                backup_of_p_list.append(row)
                                                
                            print 'backup_of_med_list=',backup_of_med_list
                            print 'backup_of_p_list=',backup_of_p_list
# editing list and working with csv file for info storage
                            lcd.show_cursor(0)
                            lcd.blink(0) 
                            lcd.set_cursor(0,1)
                            lcd.message('=>Edit Medcine Dose       ')
                            lcd.set_cursor(0,2)
                            lcd.message('Delete ID      ')
                            lcd.set_cursor(0,3)
                            lcd.message('Back                ')
                            key = keyboard(0,0,data_type='arrow')
                            if key == 'UP': 
                                menu = 3
                            elif key == 'DOWN':
                                menu = 2
                            elif key == 'ENTER' or key == 'R_ENTER':

                                
                                destination = str(usb[0])
                                destination = destination[15:-2]+'/medication reminder'
                                data_location=destination+'/patient data'
                                print 'USB drive  found'
                                print 'usb at=',destination
                                if not os.path.isdir(destination):
                                       try:
                                         print "medication folder created "  
                                         os.makedirs(destination)
                                       except OSError:
                                         pass

                                if not os.path.isdir(data_location):
                                       try:
                                         print "data folder created "  
                                         os.makedirs(data_location)
                                       except OSError:
                                         pass

                               


                                count=0
                                print 'id to edit ,k=',k
                                print '\nnew med_list='
                                with open(os.path.join(data_location,'patient_list.csv'), 'wb') as csvfile:
                                        filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                                        for row in backup_of_p_list:
                                                 filewriter.writerow(row)
                                            

                                
                                count=0
                                print 'id to edit ,k=',k
                                print '\nnew med_list='
                                with open(os.path.join(data_location,'med_list.csv'), 'wb') as csvfile:
                                        filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                                        for row in backup_of_med_list:
                                            if count==0:
                                                filewriter.writerow(row)                                                
                                            if count>=1 and row[0]!=k:
                                                    print row
                                                    filewriter.writerow(row)
                                            count=count+1

                                            
                                while True:
                                    lcd.clear()
                                    lcd.message('Enter number of\nMedicines:')
                                    lcd.set_cursor(0,3)
                                    lcd.message('Press ESC to go back')
                                    lcd.show_cursor(1)
                                    num = keyboard(10,1,data_type='num')
                                    lcd.show_cursor(0)
                                    lcd.clear()
                                    if not num:
                                        lcd.message('    SET Reminder    ')
                                    else:    
                                        no_medicine = int(num,base=10)
                                        lcd.message('Names of Medicines:')
                                        lcd.show_cursor(1)
                                        print 'num =' ,no_medicine
                                        medicine_names = [None] * no_medicine
                                        print 'medicine_names= ',medicine_names
                                        c = 1
                                        for x in range(0,no_medicine):
                                            print x
                                            if c>3:
                                                lcd.clear()
                                                lcd.message('Names of Medicines:')
                                                c = 1  
                                            lcd.set_cursor(0,c)
                                            lcd.message(str(x+1) + ')')
                                            name = keyboard(2,c,data_type='all')
                                            medicine_names[x] = name
                                            c = c+1
                                        menu = 1
                                        print 'medicine_names= ',medicine_names
                                       
                                        lcd.clear()
                                        lcd.message('Enter number of \ndosage: ')
                                        lcd.show_cursor(1)
                                        lcd.set_cursor(0,3)
                                        lcd.message('Press ESC to go back')
                                        lcd.show_cursor(1)
                                        num = keyboard(7,1,data_type='num')
                                        lcd.clear()
                                        lcd.show_cursor(0) 
                                        if not num:
                                            lcd.message('    SET Reminder    ')
                                        else:
                                            lcd.message('Set Time for dosage:')
                                            lcd.show_cursor(1)
                                            no_dosage = int(num,base=10)
                                            print 'num of dosage =' ,no_dosage
                                            medicine_dosage = [None] * no_dosage
                                            print 'medicine_dosage= ',medicine_dosage

                                            print 'ok this is it'
                                            c = 1
                                            for x in range(0,no_dosage):
                                                print x
                                                if c>3:
                                                    lcd.clear()
                                                    lcd.message('Time for dosage:')
                                                    c = 1     
                                                lcd.set_cursor(0,c)
                                                lcd.message(str(x+1) + ')')
                                                edit_hour = True
                                                edit_minute = False
                                                hour = (int)(datetime.datetime.now().strftime('%H'))
                                                minute = (int)(datetime.datetime.now().strftime('%M'))
                                                lcd.set_cursor(2,c)
                                                lcd.message(datetime.datetime.now().strftime(datestring))
                                                lcd.set_cursor(3,c)
                                                
                                                while True:
                                                    key = keyboard(0,0,data_type='arrow')
                                                    if key == 'UP':
                                                        if edit_hour:


                                                            if hour < 23:
                                                                hour = hour + 1
                                                            else:
                                                                hour = 0
                                                            lcd.set_cursor(2,c)
                                                            lcd.message(hours[hour])
                                                            lcd.set_cursor(3,c)
                                                        if edit_minute:
                                                            if minute < 59:
                                                                minute = minute + 1
                                                            else:
                                                                minute = 0
                                                            lcd.set_cursor(5,c)
                                                            lcd.message(minutes[minute])
                                                            lcd.set_cursor(6,c)

                                                    elif key == 'DOWN':
                                                        if edit_hour:
                                                            if hour > 0:
                                                                hour = hour - 1
                                                            else:
                                                                hour = 23
                                                            lcd.set_cursor(2,c)
                                                            lcd.message(hours[hour])
                                                            lcd.set_cursor(3,c)
                                                        if edit_minute:
                                                            if minute > 0:
                                                                minute = minute - 1
                                                            else:
                                                                minute = 59
                                                            lcd.set_cursor(5,c)
                                                            lcd.message(minutes[minute])
                                                            lcd.set_cursor(6,c)
                                                        
                                                    elif key == 'RIGHT' or key == 'LEFT':
                                                        if edit_hour:
                                                            lcd.set_cursor(6,c)
                                                            edit_hour = False
                                                            edit_minute = True
                                                        elif edit_minute:
                                                            lcd.set_cursor(3,c)
                                                            edit_hour = True
                                                            edit_minute = False
                                                                    
                                                    elif key == 'ENTER' or key == 'R_ENTER':
                                                        medicine_dosage[x] = hours[hour] + ':' + minutes[minute]
                                                        c = c+1
                                                        break

                                        lcd.clear()
                                        lcd.message('Press DEL to delet\nMedicine from Dose\nPress ENTR to save\nPress any key ->')
                                        speak('Press delete to remove Medicine from Dose, Press ENTR to save')
                                        key = keyboard(0,0,data_type='arrow')
                                        no_dosage = len(medicine_dosage)
                                        for x in range(0,no_dosage):
                                            #dose_medicines = [None] * len(medicine_names)
                                            dose_medicines = list(medicine_names)
                                            print 'medicine_names= ',medicine_names    
                                            print 'dose_medicines= ', dose_medicines
                                            lcd.clear()
                                            lcd.message(medicine_dosage[x] + ' Dose Medicines')
                                            lists = len(dose_medicines)
                                            temp_r = 0
                                            if lists<=3:
                                                v=lists
                                            else:
                                                v=3
                                            remove_num = 0
                                            xr = 1
                                            while True:
                                                q=1
                                                for w in range(temp_r,v):
                                                    lcd.set_cursor(0,q)
                                                    lcd.message(str(w+1) + ')' + dose_medicines[w])
                                                    q=q+1
                                                lcd.show_cursor(1)
                                                lcd.blink(1)
                                                while True:
                                                    lcd.set_cursor(0,xr)
                                                    print 'remove_num =', remove_num , 'xr=' ,xr
                                                    key = keyboard(0,0,data_type='arrow')
                                                    if key == 'DOWN' and remove_num < lists-1:
                                                        xr=xr+1
                                                        remove_num = remove_num + 1
                                                        if xr>3:
                                                            temp_r = remove_num
                                                            v = temp_r + 3
                                                            if v>lists:
                                                                v=lists
                                                            xr = 1
                                                            break
                                                    elif key == 'UP' and remove_num > 0:
                                                        xr=xr-1
                                                        remove_num = remove_num - 1
                                                        if xr<1:
                                                            temp_r = remove_num - 2
                                                            v = temp_r + 3
                                                            if v<3:
                                                                v=3
                                                            xr = 3
                                                            break
                                                    elif key == 'ENTER' or key == 'R_ENTER':
                                                        dosag['dose'+str(x)] = dose_medicines
                                                        new_buff=[]
                                                        med_buff=[]
                                                        med_buff.append(k)
                                                        med_buff.append(medicine_dosage[x])
                                                        x=len(dose_medicines)
                                                        for y in range(0,x):
                                                                med_buff.append( dose_medicines[y])

                                                        with open(os.path.join(data_location,'med_list.csv'), 'rb') as f:
                                                                reader = csv.reader(f)
                                                                # read file row by row
                                                                for row in reader:
                                                                    print row
                                                                    new_buff.append(row)
                                                        print new_buff
                                                        new_buff.append(med_buff)
                                                        with open(os.path.join(data_location,'med_list.csv'), 'wb') as csvfile:
                                                                filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                                                                for row in new_buff:
                                                                    print row
                                                                    filewriter.writerow(row)
                                                        
                                                        
                                                        break

                                                    elif key == 'DEL':
                                                        del dose_medicines[remove_num]
                                                        lists = len(dose_medicines)
                                                        print 'medicine_names length= ', lists
                                                        print 'medicine_names= ',medicine_names    
                                                        temp_r = 0
                                                        if lists<=3:
                                                            v=lists
                                                        else:
                                                            v=3
                                                        remove_num = 0
                                                        xr = 1
                                                        break
                                                if key == 'ENTER' or key == 'R_ENTER':
                                                    break
                                                lcd.clear()
                                                lcd.message(medicine_dosage[x] + 'dose Medicines')
                                    lcd.show_cursor(0)
                                    lcd.blink(0)            

                                    lcd.clear()
                                    lcd.message(' Add/Remove Medcine ')
                                    break

                            if menu == 2:
                                lcd.set_cursor(0,1)
                                lcd.message('Edit Medcine Dose       ')
                                lcd.set_cursor(0,2)
                                lcd.message('=>Delete ID      ')
                                lcd.set_cursor(0,3)
                                lcd.message('Back            ')  
                                key = keyboard(0,0,data_type='arrow')
                                if key == 'UP': 
                                    menu = 1
                                elif key == 'DOWN':
                                    menu = 3
                                elif key == 'ENTER' or key == 'R_ENTER':
                                    lcd.clear()
                                    lcd.message('    Delete ID    ')

                                    lcd.set_cursor(0,1)
                                    lcd.message('Deleting patient')
                                    lcd.set_cursor(0,2)
                                    lcd.message('data')
                                    count=0
                                    print '\n\nnew patient_list='
                                    with open(os.path.join(data_location,'patient_list.csv'), 'wb') as csvfile:
                                            filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                                            for row in backup_of_p_list:
                                                if count==0:
                                                       filewriter.writerow(row)
                                                elif count>=1 and row[0]!=k:
                                                        print row
                                                        filewriter.writerow(row)
                                                count=count+1

                                    time.sleep(2)
                                    lcd.set_cursor(0,1)
                                    lcd.message('Deleting dosage')
                                    lcd.set_cursor(0,2)
                                    lcd.message('data')
                                    backup_of_p_list=[]
                                    count=0
                                    
                                    print '\n\nnew med_list='
                                    with open(os.path.join(data_location,'med_list.csv'), 'wb') as csvfile:
                                            filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                                            for row in backup_of_med_list:
                                                if count==0:
                                                       filewriter.writerow(row)
                                                elif count>=1 and row[0]!=k:
                                                        print row
                                                        filewriter.writerow(row)
                                                count=count+1
                                    del_finger(1,k)
                                    time.sleep(2)
                                    menu = 1
                                    lcd.clear()
                                    lcd.message('Data deleted')
                                    break
                            if menu == 3:
                                lcd.set_cursor(0,1)
                                lcd.message('Edit Medcine Dose       ')
                                lcd.set_cursor(0,2)
                                lcd.message('Delete ID      ')
                                lcd.set_cursor(0,3)
                                lcd.message('=>Back              ')
                                key = keyboard(0,0,data_type='arrow')
                                if key == 'UP': 
                                    menu = 2
                                elif key == 'DOWN':
                                    menu = 1
                                elif key == 'ENTER' or key == 'R_ENTER':
                                    menu = 1
                                    break
def capture_video(id_dose):
        print 'creating video'
        global cap
        global data_location 
        global video_location
##        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_name=video_location+'/'+id_dose+'_'+str(datetime.datetime.now().strftime('%d%m%Y'))+'.avi'
        out = cv2.VideoWriter(video_name,fourcc, 20.0, (640,480))
        GPIO.output(in1,True)
        GPIO.output(in2,False)
        time.sleep(2)
        GPIO.output(in1,False)
        GPIO.output(in2,False)
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret==True:
##                frame = cv2.flip(frame,0)

                # write the flipped frame
                out.write(frame)

##                cv2.imshow('frame',frame)             
                if GPIO.input(sleep)==False :
                    # Release everything if job is finished
                    GPIO.output(in2,True)
                    GPIO.output(in1,False)
                    time.sleep(2)
                    GPIO.output(in1,False)
                    GPIO.output(in2,False)
##                    cap.release()
                    out.release()
                    print 'video created'
                    
##                    cv2.destroyAllWindows()
                    break
            else:
                
                 cap = cv2.VideoCapture(0)
                 out = cv2.VideoWriter(video_name,fourcc, 20.0, (640,480))

        
##        cv2.destroyAllWindows()

def take_medicine():
    
    global sys
    global dia
    global pulse
    
    val=search_finger()
    if (val>= 0):
            now_tim = (int)(re.sub(pattrn,'',datetime.datetime.now().strftime('%H:%M')),base=10)
            med_taken.append(int(77))
            positive_diff=0
            taken=0
            updated=0
            data_list=[]
            data_list.append('0')
            print 'len of med_taken=',len(med_taken)
            print ' med_taken=',med_taken
            
            last_index_med_taken = len(med_taken)-1
            print 'last_index_med_taken=',last_index_med_taken
            with open(os.path.join(data_location,'med_list.csv'), 'rb') as f:
                            reader = csv.reader(f)
                            index=0
                            
                            med_tim_near_to_current_time=''
                            # read file row by row
                            for row in reader:
                                index=index+1
                                if row[1]!='time':   
                                      if row[0]==val:
                                           print 'row=',row
                                           pattrn1 = re.compile('\W')
                                           med_tim=0
                                           med_tim = (int)(re.sub(pattrn,'',row[1]),base=10)
                                           positive_diff=now_tim-med_tim
                                           
                                           print ' difference=',positive_diff
                                           if positive_diff<0:
                                               positive_diff=positive_diff*-1
                                               print 'positive diff=',positive_diff
                                           if ((med_taken[last_index_med_taken])==77) or ((med_taken[last_index_med_taken])>positive_diff):
                                                        med_taken[last_index_med_taken]=positive_diff
                                                        med_tim_near_to_current_time=med_tim
                                                        data_list=row
                                 
                                


            for q in range(len(med_taken)):
                     print 'q=',q 
                     if q>=1:
                         if med_tim_near_to_current_time==( med_taken[q]) : # a== time of medicine to be taken
                             print 'a is equal'
                             taken = 1
            if taken == 0:
                    med_taken[last_index_med_taken]=  med_tim_near_to_current_time
                    print ' med_taken[last_index_med_taken]',med_taken
                    print 'data_list=',data_list
                    medicine1_list=[]
                    
                    for d in range(len(data_list)):
                        if d>=2:
                            medicine1_list.append(data_list[d])
                            print 'list of med=',data_list[d]

                    print 'medicine list=',medicine1_list
                    lcd.clear()
                    lcd.message('  Health Check-up  ')
                    lcd.set_cursor(0,1)
                    lcd.message('Monitoring....\n\n\nPress button to skip')
                    GPIO.output(relay,False)
                    print 'Press button to skip'
                    time.sleep(0.5)
                    sys='           '
                    dia='           '
                    pulse='         '
                    j=0
                    while GPIO.input(sleep)==True:
                            if port.inWaiting() > 0:
                                rcv = port.readall().strip()
                                print "rcv=" , rcv
                                
                                while rcv[j]!=',':
                                    j=j+1
                                
                                sys=rcv[0:j]
                                j=j+1
                                k=j
                                
                                while rcv[j]!=',':
                                    j=j+1
                                dia=rcv[k:j]
                                j=j+1
                                k=j    

                                pulse=rcv[k:len(rcv)]
                                lcd.clear()
                                lcd.message('    Health Status\nSys='+sys+'\ndia='+dia+'\nPulse/Min='+pulse)
                                print 'Health Status\nSys='+sys+'\ndia='+dia+'\nPulse/Min='+pulse
                                time.sleep(4)
                                break
                            

                  
                    os.system("sudo mpg123 -q Store_Door.mp3 &")
                    time.sleep(2)
                    lcd.clear()
                    lcd.message("It's time for dose")
                    print ("It's time for dose")
                    speak("It's time for dose")
                    m=''
                    list_ind=0
                    for g in medicine1_list:
                        lcd.set_cursor(0,list_ind+1)
                        m=str(list_ind+1)+str(medicine1_list[list_ind])
                        lcd.message(m)
                        list_ind=list_ind+1
                    time.sleep(0.5)

                        

                    print 'lengh of medicine_list=',len(medicine1_list)
                    lcd.clear()
                    lcd.message("Take your medicines")
                    print 'take your medicines'

                    print 'creating hit link'
                    print 'sys=',sys
                    print 'dia=',dia
                    print 'pulse=',pulse
                    print 'temp=',str(round((adc(0)/0.68),1))
                    

                    time.sleep(2)
                    h=sys+','+dia+','+pulse+','+str(round((adc(0)/0.68),1))
                   
                    capture_video(str( str(val)+'_'+str(med_taken[last_index_med_taken])))

                    with open(os.path.join(data_location,'patient_list.csv'), 'rb') as f:
                                        reader = csv.reader(f)
                                        index1=0
                                        # read file row by row
                                        for row in reader:
                                                if val== row[0]:
                                                      detail=row
                                                      break
                                                    
                    m=''
                    print 'creating m list'
                    o=0
                    for f in (medicine1_list):

                        m=m+medicine1_list[o]
                        o=o+1                        
                        if len(medicine1_list)>o:
                            m=m+','
                        
                    
                    print 'hit link',str(val)+detail[1]+'1'+m+h+detail[3]+detail[4]
                    print 'creating m list'
                    hit_link(str(val),detail[1],'1',m,h,detail[3],detail[4])
                    
                                        
                    
            else:
                lcd.clear()
                lcd.message('dose already taken'+str( med_taken[last_index_med_taken-1]))
                time.sleep(1) 
                            
                           
    else :
        lcd.clear()
        lcd.message('No match found! ')
        time.sleep(1)
        
# for collecting fingerpints
        
def search_finger():
    try:
        print('Waiting for finger...')
        lcd.clear()
        lcd.message('Waiting for finger..')
        ## Wait that finger is read
        while (finger.readImage() == False):           
            pass

        ## Converts read image to characteristics and stores
        finger.convertImage(0x01)

        ## Searches template
        result = finger.searchTemplate()
        positionNumber = result[0]
        accuracyScore = result[1]
        if (positionNumber == -1):
            print('No match found!')
            lcd.clear()
            lcd.message('No match found! ')
            
           # exit(0)
        else:
            print('Found template at position #' + str(positionNumber))
            print('The accuracy score is: ' + str(accuracyScore))
            lcd.clear()
            lcd.message('match found!')
            lcd.set_cursor(0,1)
            lcd.message('Patient id='+ str(positionNumber))
            return str(positionNumber)
    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
##        exit(1)


def del_finger(g,b):
    try:
        data=""
        if(g==1):
##            positionNumber = input('Please enter the template position you want to delete: ')
            positionNumber = int(b)

            if ( finger.deleteTemplate(positionNumber) == True ):
                print('Template deleted!')
        else:
            for i in range(0,25):
                 if ( finger.deleteTemplate(i) == True ):
                    print('Template deleted!')

    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        exit(1)

def enroll():
        global data_location 
             
        print('Waiting for finger...')
        lcd.clear()
        lcd.message(' Patient Enrollment      ')
        lcd.set_cursor(0,1)
        lcd.message('Register fingerprint')
        lcd.set_cursor(0,2)
        lcd.message('Waiting for finger..')
        ## Wait that finger is read
        while ( finger.readImage() == False  ):
              
            pass

        ## Converts read image to characteristics and stores it in charbuffer 1
        finger.convertImage(0x01)

        ## Checks if finger is already enrolled
        result = finger.searchTemplate()
        positionNumber = result[0]

        if ( positionNumber >= 0 ):
            print('Template already exists at position #' + str(positionNumber))
            lcd.clear()
            lcd.message('  Patient Enrollment      ')
            lcd.set_cursor(0,1)
            lcd.message('Already Registered')
            time.sleep(2)
            return str(positionNumber)+str('*')
            #exit(0)

        else:
            print('Remove finger...')
            lcd.clear()
            lcd.message('  Patient Enrollment      ')
            lcd.set_cursor(0,1)
            lcd.message('Remove finger...')
            time.sleep(2)
            print('Waiting for same finger again...')
            lcd.clear()
            lcd.message('  Patient Enrollment      ')
            lcd.set_cursor(0,1)
            lcd.message('Waiting for same')
            lcd.set_cursor(0,2)
            lcd.message('finger again...')
            time.sleep(2)
            ## Waiting till that finger is read again
            while(finger.readImage() == False):
                pass

            ## Converts read image to characteristics and stores it in charbuffer 2
            finger.convertImage(0x02)

            ## Compares the charbuffers
            if ( finger.compareCharacteristics() == 0 ):
                lcd.clear()
                lcd.message('  Patient Enrollment      ')
                lcd.set_cursor(0,1)
                lcd.message('Fingers do not match')
                time.sleep(2)
                print('Fingers do not match')
                return 'zero'
            else:
                ## Creates a template
                finger.createTemplate()

                ## Saves template at new position number
                positionNumber = finger.storeTemplate()
                lcd.clear()
                lcd.message(' Patient Enrollment ')
                lcd.set_cursor(0,1)
                lcd.message('Finger enrolled')
                lcd.set_cursor(0,2)
                lcd.message('successfully!')
                lcd.set_cursor(0,3)
                lcd.message('enrolled id=')
                lcd.message(str(positionNumber))
                time.sleep(2)
                print('Finger enrolled successfully!')
                print('New template position #' + str(positionNumber))
                return str(positionNumber)          
def adc(chn):
    if chn == 0:
        bus.write_byte(0x48,0x40)
    if chn == 1:
        bus.write_byte(0x48,0x41)
    if chn == 2:
        bus.write_byte(0x48,0x42)
    if chn == 3:
        bus.write_byte(0x48,0x43)
    bus.read_byte(0x48)

    return int(bus.read_byte(0x48))

# Working with GSM module

def send_cmd(cmd,response=None,t=0.5):
    port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=t)
    cmd = cmd + "\r\n"
    port.write(cmd)
    rcv = port.readall().strip()
    print "rcv = ", rcv
    if response:
        print rcv.endswith(response)
        return rcv.endswith(response)


def send_sms(name,num,d):
    GPIO.output(relay,True)
    print "sending sms to ",num
    
    if d==0:
        text='hello,'+name+' its time for your medicine'
    else:
        text='hello,'+name+' its patient\'s medicine time '
    lcd.clear()
    lcd.message('sending sms to\n'+name+'\n'+num)
    time.sleep(2)
    send_cmd("AT+CMGF=1",ok)
    if send_cmd("AT+CMGS=\""+num+'\"','>'):
        if send_cmd(text+"\x1a",ok,5):
            print "sms send"
        else:
            print "cant send sms....check your balance"
        
def get_data():
    rcv = ""
    print "data available"
    rcv = port.readall().strip()
    print "rcv=" , rcv   
    check_data(rcv)
    port.flushInput()

def init_gsm():
    print 'init gsm'
    lcd.clear()
    lcd.message('GSm Initiallizing..')
  
    time.sleep(0.5)
    while True:
        if send_cmd("AT",ok):
            print "gsm connected"
            break
        else:
            print "gsm not connected"
        
    send_cmd("ATE0",ok)
    lcd.set_cursor(0,1)
    lcd.message('Connected     ')
    time.sleep(0.5)
    
def check_data(data):
    
    if data.find("+CLIP") > 0:
        index1 = data.find('\"') + 1
        index2 = data.find(',') - 1
        number = data[index1:index2]
        print "receiving call from ",number
        time.sleep(1)
        send_cmd("ATH",ok)


    if data.find("+CMT") > 0:
        index1 = data.find('\"') + 1
        index2 = data.find(',') - 1
        sms_number = data[index1:index2]
        index3 = data.rfind('"') + 1
        sms = data[index3:]
        print "number: ",sms_number
        print "sms: ", sms
        
def speak(text):
    os.system("pico2wave --lang=en-US -w sample.wav \"" + text + "\" && aplay sample.wav")


def keyboard(c,r,data_type):
    key_lookup=0
    if data_type == 'arrow':
        for event in dev.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                data = evdev.categorize(event)  # Save the event temporarily to introspect it
                if data.keystate == 1:  # Down events only
                    key_lookup = scancodes.get(data.scancode) or None#'UNKNOWN:{}'.format(data.scancode)  # Lookup or return UNKNOWN:XX
                    if key_lookup:
                        if key_lookup == 'UP' or key_lookup == 'DOWN' or key_lookup == 'ENTER' or key_lookup == 'R_ENTER' or key_lookup == 'LEFT' or key_lookup == 'RIGHT' or key_lookup == 'ESC' or key_lookup == 'DEL':
                                return key_lookup
            
    else:
        lcd.set_cursor(c,r)
        c_limit = c
        in_data=""
        for event in dev.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                data = evdev.categorize(event)  # Save the event temporarily to introspect it
                if data.keystate == 1:  # Down events only
                    key_lookup = scancodes.get(data.scancode) or None #u'UNKNOWN:{}'.format(data.scancode)  # Lookup or return UNKNOWN:XX
                    if key_lookup:
                        if key_lookup.isdigit() or key_lookup == 'ENTER' or key_lookup == 'BKSP' or key_lookup == 'R_ENTER' or data_type == 'all':
                            print key_lookup
                            if key_lookup == 'ENTER' or key_lookup == 'R_ENTER':
                                in_data=in_data.strip()
                                return in_data
                            elif key_lookup == 'BKSP':
                                if c>c_limit:     
                                    c = c-1
                                    print len(in_data)
                                    if len(in_data)> 0:
                                        in_data = in_data[:(len(in_data)-1)]# + ' '
                                    lcd.set_cursor(c,r)
                                    lcd.message(' ')
                                    lcd.set_cursor(c,r)
                            else:
                                data = u'You Pressed the {} key!'.format(key_lookup)
                                print data , key_lookup # Print it all out!
                                lcd.message(key_lookup)
                                in_data += key_lookup
                                c = c+1
                        elif key_lookup == 'ESC':
                                return None
                        else:
                            print "unknown.."
                            

reset = 23
sleep = 24
r_led = 7
relay=25
in1 = 13
in2 = 6
relay=8

GPIO.setup(reset,GPIO.IN)
GPIO.setup(sleep,GPIO.IN)
GPIO.setup(r_led,GPIO.OUT)


GPIO.setup(relay,GPIO.OUT)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)

GPIO.output(relay,True)
GPIO.output(r_led,False)

GPIO.output(in1,False)
GPIO.output(in2,False)

# Raspberry Pi pin configuration:

lcd_rs        = 26  # this might be 21 in the Raspberry Pi model 2 
lcd_en        = 19
lcd_d4        = 21
lcd_d5        = 20
lcd_d6        = 16
lcd_d7        = 12
lcd_backlight = 5
# Define LCD column and row size for 16x2 LCD.
lcd_columns = 20
lcd_rows    = 4
              
# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)

lcd.set_backlight(0)
lcd.show_cursor(0)
bus = SMBus(1)
main = True
while GPIO.input(reset) == False:
            t2 = datetime.now()
            delta = t2 - t1
            time_elapse = delta.total_seconds()
            if time_elapse > 8:
                    reset = False
                    main = False
                    break


while main:
   # subprocess.call('vcgencmd display_power 0',shell=True)
    global destination
    global video_location
    global data_location
    global cap
    cap = cv2.VideoCapture(0)
    start1=0
    try:
        path = None
        lcd.clear()
        lcd.message('    Raspberry pi    \n       Based         \n Speaking Medication \n      Reminder')
        speak('rasberry pi Based Speaking Medication Reminder')
        time.sleep(3)
        lcd.clear()
        lcd.message('Searching for the\nfingerprint module')
        time.sleep(2)

        while True:
            try:
                finger = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
            
            except Exception as e:
                   print('fingerprint sensor\ncould not be\ninitialized!')
                   print('Exception message: ' + str(e))
                   lcd.clear()
                   lcd.message('fingerprint sensor\n not found')
                   while GPIO.input(reset):
                            lcd.set_cursor(0,2)
                            lcd.message('    Press reset     ')
                            time.sleep(0.5)
                            lcd.set_cursor(0,2)
                            lcd.message('                    ')
                            time.sleep(0.5)

            if( finger.verifyPassword() == True ):
                print('\nThe fingerprint sensor initialized!')
                del_finger(0,0)
                break

            if( finger.verifyPassword() == False ):
                raise ValueError('\nThe given fingerprint sensor password is wrong!')

        lcd.clear()
        lcd.message('Searching for the\ncamera')
        time.sleep(2)
        if not cap.isOpened():
            main = False
            print "can't open the camera"
            lcd.clear()
            lcd.message('Error:Camera not\nFound')
            time.sleep(2)
            lcd.clear()
            lcd.message('Connect Camera &\nrestart')
            while True:
                None

        else:
            main = True
            print "camera found"
            lcd.clear()
            lcd.message('Found Camera')
            time.sleep(2)    

        init_gsm()
        
        lcd.clear()
        lcd.message('Searching for the\nUSB drive')
        time.sleep(2)
        usb=get_mount_points()
        if (len(usb)) <=0:
            print 'USB drive not found'
            lcd.clear()
            lcd.message('USB drive not found')
            time.sleep(2)
            lcd.clear()
            lcd.message('  Connect USB drive  ')
            while GPIO.input(reset):
                lcd.set_cursor(0,2)
                lcd.message('    Press reset     ')
                time.sleep(0.5)
                lcd.set_cursor(0,2)
                lcd.message('                    ')
                time.sleep(0.5)
        else:
            destination = str(usb[0])
            destination = destination[15:-2]+'/medication reminder'
            data_location=destination+'/patient data'
            video_location=destination+'/videos'
            print 'USB drive  found'
            print 'usb at=',destination
            if not os.path.isdir(destination):
                   try:
                     print "medication folder created "  
                     os.makedirs(destination)
                   except OSError:
                     pass

            if not os.path.isdir(data_location):
                   try:
                     print "data folder created "  
                     os.makedirs(data_location)
                   except OSError:
                     pass

            if not os.path.isdir(video_location):
                   try:
                     print "video folder created "  
                     os.makedirs(video_location)
                   except OSError:
                     pass

            with open(os.path.join(data_location,'patient_list.csv'), 'wb') as csvfile:
                    filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    filewriter.writerow(['ID', 'Patient Name', 'Patient Mobile. no', 'Doctor Name', 'Doctor Mobile. no'])
            with open(os.path.join(data_location,'med_list.csv'), 'wb') as csvfile:
                    filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    filewriter.writerow(['ID', 'Time', 'Medicine'])
            lcd.clear()
            lcd.message('USB drive found')
            time.sleep(2)
        
        lcd.clear()
        lcd.message('Searching for the\nKeyboard')
        time.sleep(2)
        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        for device in devices:
             d_name = device.name
             d_phys = device.phys
             if (d_name.find('Keykoard')>0 or d_name.find('Keyboard')>0) and d_phys.find('input0')>0:
                 path = device.fn
                 print 'got keyboard at ', path
                 break

        if not path:
            print 'keyboard not found'
            lcd.clear()
            lcd.message('keyboard not found')
            time.sleep(2)
            lcd.clear()
            lcd.message('  Connect Keyboard  ')

            while GPIO.input(reset)==False:
                lcd.set_cursor(0,2)
                lcd.message('    Press reset     ')
                time.sleep(0.5)
                lcd.set_cursor(0,2)
                lcd.message('                    ')
                time.sleep(0.5)
                
        else:
            lcd.clear()
            lcd.message('Found Keyboard')
            time.sleep(2)
            dev = InputDevice(path)
            print 'dev=' ,dev
            main_menu = True
            lcd.clear()
            lcd.message('     Main Menu      ')
            menu = 1
            while main_menu:
                if menu == 1:
                    lcd.set_cursor(0,1)
                    lcd.message('=>START             ')
                    lcd.set_cursor(0,2)
                    lcd.message('SET Reminder        ')
                    if start1==0 :
                        key = keyboard(0,0,data_type='arrow')
                    if key == 'UP':
                        menu = 3
                    elif  key == 'DOWN':
                        menu = 2
                    elif start1==1 or key == 'ENTER' or key == 'R_ENTER' :
                        start1 = 1
                        start2=1
                        lcd.clear()
                        t=0
                        ##getting time in a list
                        with open(os.path.join(data_location,'med_list.csv'), 'rb') as f:
                            reader = csv.reader(f)
                            index=0
                            my_time=[]  
                            # read file row by row
                            for row in reader:
                                   my_time.append(row[1])
                            print my_time
                        med_list=[]
                        index1=0
                        diff=0
                        diff2=0
                        print "med dos=",medicine_dosage
                        if len(my_time) > 1: # and len(medicine_names) > 0:
                            for n in range(len(my_time)):
                                pattrn = re.compile('\W')
                                a=0
                                print 't=',t
                                print 'n=',n
                                if n!=0:
                                    a = (int)(re.sub(pattrn,'',my_time[n]),base=10)
                                    diff=a-b
                                    if (diff2==0 or diff<diff2) :
                                        if diff>0:
                                              diff2=diff
                                              print 'diff2=',diff2  
                                              print 'mytime=',my_time[n]
                                              size=int(len(med_taken))
                                              if int(size)<=1:
                                                        print 'frm else t=',t  
                                                        t=n
                                                          
                                              else:
                                                  print 'med_taken=',med_taken
                                                  print 'med_taken len=',size
                                                  for z in range(len(med_taken)):
                                                     print 'z=',z 
                                                     if z>=1:
                                                         if a==( med_taken[z]) :# a== time of medicine to be taken
                                                             print 'a is equal'
                                                             diff2 = 0
                                                         else:
                                                             t=n
                                                             print 'frm z, t=',t
                                                

                                print "a=",a
                                b = (int)(re.sub(pattrn,'',datetime.datetime.now().strftime('%H:%M')),base=10)
                                print "\n b=",b
                            with open(os.path.join(data_location,'med_list.csv'), 'rb') as f:
                                        reader = csv.reader(f)
                                        index1=0
                                        # read file row by row
                                        for row in reader:
                                                if index1 == t:
                                                    patient_id =str(row[0])
                                                    for k in range(2,len(row)):
                                                            med_list.append(row[k])
                                                            print 'list of med=',row[k]
                                                index1=index1+1
                                                        
                            print "\n patient_id=",patient_id            
                            print "my_timet=",my_time[t]
                            print "\n med dos=",med_list
                            if t!=0:
                                a = (int)(re.sub(pattrn,'',my_time[t]),base=10)
                            else:
                                a=3333
                            while start2:
                                current_time = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                                lcd.clear()
                                lcd.set_cursor(0,0)
                                lcd.message(datetime.datetime.now().strftime('%d/%m/%Y %H:%M'))
                                pattrn = re.compile('\W')
                                if t!=0:
                                    lcd.set_cursor(0,1)
                                    lcd.message('Next dose: ' + my_time[t])
                                else:
                                   
                                    lcd.set_cursor(0,1)
                                    lcd.message('No dose for today')
                                        

                                lcd.set_cursor(0,3)
                                lcd.message('Press ESC to go back')
                                print "Press ESC to go back"
                                b = int(re.sub(pattrn,'',datetime.datetime.now().strftime(datestring)),base=10)
                                if a==b  :
                                    os.system("sudo mpg123 -q Store_Door.mp3 &")
                                    time.sleep(2)
                                    temp = list(med_list) 
                                    lcd.clear()
                                    lcd.message("It's time for dose")
                                    speak("It's time for dose")
                                    
                                    patient_detail=[]
                                   
                                    with open(os.path.join(data_location,'patient_list.csv'), 'rb') as f:
                                        reader = csv.reader(f)
                                        index1=0
                                        # read file row by row
                                        for row in reader:
                                                if patient_id == row[0]:
                                                      patient_detail=row
                                                      break
                                    print ' patient detail= ',patient_detail
                                    send_sms(patient_detail[1],patient_detail[2],0)
                                    time.sleep(1)
                                    send_sms(patient_detail[3],patient_detail[4],1)
                                    time.sleep(1)
                                    print 'send sms, patient=',t
                                    
                                    p=0
                                    for n in temp:
                                        lcd.clear()
                                        lcd.message("It's time for dose")
                                        lcd.set_cursor(0,1)
                                        lcd.message(str(p+1) + ')' + temp[p])
                                        p=p+1
                                        print'n=',n
                                        speak(n)
                                    print 'temp=',temp
                                    lists = len(temp)
                                    print 'lengh of tempt=',lists
                                    
                                    temp_r = 0
                                    if lists<=3:
                                        v=lists
                                    else:
                                        v=3
                                    remove_num = 0
                                    xr = 1
                                    lcd.clear()
                                    lcd.message("Take your medicines")
                                    print 'take your medicines'
                                    while True:
                                        q=1
                                        for x in range(0,v):
                                            lcd.set_cursor(0,q)
                                            lcd.message(str(x+1) + ')' + temp[x])
                                            q=q+1
                                        lcd.show_cursor(1)
                                        lcd.blink(1)
                                        time.sleep(1)
                                        lcd.clear()
                                        lcd.message('Take Your Medicines ')
                                        time.sleep(1)
                                        break
                                    break   
                                       
                                lcd.show_cursor(0)
                                lcd.blink(0)
                                t1 = ((datetime.datetime.now()))   
                                while True:

                                    event=dev.read_one()
                                    if event:
                                        if event.type == evdev.ecodes.EV_KEY:
                                            data = evdev.categorize(event)
                                            if data.keystate == 1:
                                                key_lookup = scancodes.get(data.scancode) or None
                                                if key_lookup == 'ESC':
                                                    start2 = 0
                                                    start1=0
                                                    break
                                    elif GPIO.input(sleep)==False:
                                            take_medicine()
                                            start2=0
                                            break
                                            
                                        
                                    else:
                                        t2 = datetime.datetime.now()
                                        delta = t2 - t1
                                        time_elapse = delta.total_seconds()
                                        if time_elapse > 1:
                                            break
                                        
                                        
                        else:
                            start1=0
                            print 'Kindly set Dosages\nfirst!\n\nPress ENTER'
                            if not len(medicine_dosage) > 0 and len(medicine_names) > 0:
                                lcd.clear()
                                lcd.message('Kindly set Dosages\nfirst!\n\nPress ENTER')
                                speak('Kindly set Dosages first! Press enter to go back')
                                key = keyboard(0,0,data_type='all')
                            elif not len(medicine_names) > 0 and len(medicine_dosage) > 0:
                                lcd.clear()
                                lcd.message('Kindly set Medicine\nfirst!\n\nPress ENTER')
                                speak('Kindly set Medicine first! Press enter to go back')
                                key = keyboard(0,0,data_type='all')
                            else:
                                lcd.clear()
                                lcd.message('You have to set\nMedicine and Dosages\nfirst!\nPress ENTER')
                                speak('You have to Set Medicine and Dosages first!, Press enter to go back')
                                key = keyboard(0,0,data_type='all')
                            time.sleep(1)
                        lcd.clear()
                        lcd.message('     Main Menu      ')

                        
                                    
                if menu == 2:
                    lcd.set_cursor(0,1)
                    lcd.message('START               ')
                    lcd.set_cursor(0,2)
                    lcd.message('=>SET Reminder      ')
                    key = keyboard(0,0,data_type='arrow')
                    if key == 'UP':
                        menu = 1
                    elif  key == 'DOWN':
                        menu = 2
                    elif key == 'ENTER' or key == 'R_ENTER':
                        menu = 1
                        while True:
                            lcd.clear()
                            lcd.message('    SET Reminder    ')
                            if menu == 1:
                                lcd.set_cursor(0,1)
                                lcd.message('=>Enroll Patient  ')
                                lcd.set_cursor(0,2)
                                lcd.message('Back             ')
                                key = keyboard(0,0,data_type='arrow')
                                if key == 'DOWN' or key == 'UP' :
                                    menu=2
                                 
                                if key == 'ENTER' or key == 'R_ENTER':
                                    enrol_patient()
                                    menu = 1
                                    
                            if menu == 2:
                                lcd.set_cursor(0,1)
                                lcd.message('Enroll Patient  ')
                                lcd.set_cursor(0,2)
                                lcd.message('=>Back             ')
                                key = keyboard(0,0,data_type='arrow')
                                if key == 'DOWN' or key == 'UP' :
                                    menu=1
                                if key == 'ENTER' or key == 'R_ENTER':
                                    lcd.clear()
                                    lcd.message('     Main Menu      ')
                                    menu = 1
                                    break    
                
    except Exception as errr :
        print "Exception :",errr
        print 'got error'
        print 'press reset'
        lcd.clear()
        lcd.message('   !!!!Error!!!!   ')

        while GPIO.input(reset):
            lcd.set_cursor(0,2)
            lcd.message('    Press reset     ')
            time.sleep(0.5)
            lcd.set_cursor(0,2)
            lcd.message('                    ')
            time.sleep(0.5)

        t1 = datetime.datetime.now()
        while GPIO.input(reset) == False:
            t2 = datetime.datetime.now()
            delta = t2 - t1
            time_elapse = delta.total_seconds()
            if time_elapse > 5:
                main = False
                break

lcd.clear()
lcd.message('Programme terminate!')
while True:
    None
time.sleep(2)
lcd.clear()
GPIO.cleanup()
