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

## datestring=' %d/%m/%Y %H:%M'
date = (int)(datetime.datetime.now().strftime('%d')) - 1
month = (int)(datetime.datetime.now().strftime('%m')) - 1
year = (int)(datetime.datetime.now().strftime('%Y')) 
hour = (int)(datetime.datetime.now().strftime('%H')) 
minute = (int)(datetime.datetime.now().strftime('%M')) 
day = (int)(datetime.datetime.now().strftime('%d')) - 1
datestring='%H:%M'

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