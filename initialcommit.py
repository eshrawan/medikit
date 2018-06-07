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