from machine import UART, Pin
import time

uart0 = machine.UART(0,baudrate=9600)
gsm_buffer = ''
destination_phone = r"+254719586585"

########################################################################
def convert_to_string(buf):
    tt =  buf.decode('utf-8').strip()
    return tt
########################################################################

def send_command(cmdstr, msgtext=None, lines=1, uart=uart0):
    global gsm_buffer
    
    #___________________________________________________________________
    print("CMD: " + cmdstr)
    cmdstr = cmdstr+'\r'
    #___________________________________________________________________
    #Empty the serial buffer
    while uart.any():
        uart.read()
    #___________________________________________________________________
    #Send command to sim800l
    uart.write(cmdstr)
    time.sleep(0.5)
    #___________________________________________________________________
    #Only used while sending sms
    if msgtext:
        print("MSG: " + msgtext)
        uart.write(msgtext + chr(26))
    #___________________________________________________________________        
    #
    #___________________________________________________________________
    #read data comming from sim800l line by line
    buf=await_response() 
    #___________________________________________________________________
    if not buf:
        return None
    result = convert_to_string(buf)
    #___________________________________________________________________
    #if there are multiple lines of data comming from sim800l
    if lines>1:
        gsm_buffer = ''
        for i in range(lines-1):
            buf=uart.readline()
            time.sleep(0.1)
            if not buf:
                return result
            #print(buf)
            buf = convert_to_string(buf)
            if not buf == '' and not buf == 'OK':
                gsm_buffer += buf+'\n'
    #___________________________________________________________________
    return result
########################################################################

########################################################################
def await_response(uart=uart0, timeout=10000):
    prvMills = time.ticks_ms()
    resp = b""
    while (time.ticks_ms()-prvMills)<timeout:
        if uart.any():
            resp = b"".join([resp, uart.readline()])
            
    if resp != '':
        print("response: " + resp.decode())
        print("_______________________________")
        return resp
    else:
        print("_______________________________")
    return None
########################################################################    
    
########################################################################
def send_sms(msgtext):
    global gsm_buffer
    result = send_command('AT+CMGS="{}"'.format(destination_phone),msgtext, 99)
   # if result and result=='>' and gsm_buffer:
    #    params = gsm_buffer.split(':')
   #     if params[0]=='+CUSD' or params[0] == '+CMGS':
  #          print('OK')
 #           return 'OK'
#    print('ERROR')
    print("gsm_buffer: " + gsm_buffer)
    return gsm_buffer
########################################################################    

#print(send_command('AT\r\n'))

uart0.write('AT\r\n')
time.sleep(1)
"""
Basic initialization commands to set up the SIM800 module.
"""
print("Checking for sim module presence ...")
send_command('AT')  # Check module presence

print("Turn off command echoing ...")
send_command('ATE0')  # Turn off command echoing

print("Setting full functionality mode ...")
send_command('AT+CFUN=1')  # Set full functionality mode

print("Setting extended error message reporting ...")
send_command('AT+CMEE=1')  # enable extended error message reporting


print("Show what type of sms-encoding is used ...")
encodingType = send_command('AT+CSCS?')  # show what type of sms-encoding is used

if '+CSCS: "GSM"' not in encodingType:
    print("Set sms-encoding to GSM ...")
    send_command('AT+CSCS="GSM"')  # set sms-encoding to GSM



# Check if device text mode is PDU or Text
print("check device text mode ...")
textMode = send_command('AT+CMGF?')# Set message format

if '+CMGF: 1' not in textMode:
    # Set device text mode to Text
    print("Set device text mode to Text ...")
    print(send_command('AT+CMGF=1'))# Set mode to Text


# print("\nConfigure receive message and delivery reports:")
# print(send_command('AT+CNMI=2,2,0,2,0\r\n'))
# time.sleep(0.5)

# print("\nDelete all inboxes:") # delete all inbox messages
# print(send_command('AT+CMGD=1,4\r\n'))
# time.sleep(0.5)

#print(send_command('AT+CSCS=?\r\n'))
#print(send_command('AT+CUSD=?\r\n'))

# send_command('AT+CSCS="GSM"\r\n')
#send_command('AT+CUSD=1')

# print(send_command('AT+CUSD=1,\"*144#\", 15\r\n',None,10))

print("Sending sms ...")
print(send_sms("hey, test text. imework?"))





 
#2 sec timeout is arbitrarily chosen
def sendCMD_waitResp(cmd, uart=uart0, timeout=8000):
    print("CMD: " + cmd)
    uart.write(cmd)
    waitResp(uart, timeout)
    print()
    
def waitResp(uart=uart0, timeout=8000):
    prvMills = time.ticks_ms()
    resp = b""
    while (time.ticks_ms()-prvMills)<timeout:
        if uart.any():
            resp = b"".join([resp, uart.readline()])
            
    if resp != '':
        print("response: " + resp.decode())   
 
   
#sendCMD_waitResp("AT+CGATT?\r\n")
#time.sleep(2)
#sendCMD_waitResp("AT\r\n")
#time.sleep(2)

#sendCMD_waitResp("ATI\r\n")
#time.sleep(2)

#sendCMD_waitResp("ATD*144#\r\n") #+CUSD: <m>[,<str>,<dcs>] 
#time.sleep(4)

#sendCMD_waitResp("AT+CGMS+254719586585;\r\n")  #Replace xxxxxxxx with monile number
#time.sleep(5)

#sendCMD_waitResp("ATD+254719586585;\r\n")  #Replace xxxxxxxx with monile number
#time.sleep(20)
#sendCMD_waitResp("ATH\r\n")   # Hang call
