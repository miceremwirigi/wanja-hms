from machine import UART, Pin
import time

uart0 = UART(0, baudrate=9600)
gsm_buffer = ''
destination_phone = r"+254719586585"

########################################################################
def convert_to_string(buf):
    tt = buf.decode('utf-8').strip()
    return tt
########################################################################

def send_command(cmdstr, msgtext=None, lines=1, uart=uart0):
    global gsm_buffer
    
    #___________________________________________________________________
    print("CMD: " + cmdstr)
    cmdstr = cmdstr + '\r'
    #___________________________________________________________________
    # Empty the serial buffer
    while uart.any():
        uart.read()
    #___________________________________________________________________
    # Send command to sim800l
    uart.write(cmdstr)
    time.sleep(0.5)
    #___________________________________________________________________
    # Only used while sending sms
    if msgtext:
        print("MSG: " + msgtext)
        uart.write(msgtext + chr(26))
    #___________________________________________________________________        
    #
    #___________________________________________________________________
    # Read data coming from sim800l line by line
    buf = await_response(uart=uart) 
    #___________________________________________________________________
    if not buf:
        return None
    result = convert_to_string(buf)
    #___________________________________________________________________
    # If there are multiple lines of data coming from sim800l
    if lines > 1:
        gsm_buffer = ''
        for i in range(lines - 1):
            buf = uart.readline()
            time.sleep(0.1)
            if not buf:
                return result
            buf = convert_to_string(buf)
            if buf and buf != 'OK':
                gsm_buffer += buf + '\n'
    #___________________________________________________________________
    return result
########################################################################

########################################################################
def await_response(uart=uart0, timeout=10000):
    prvMills = time.ticks_ms()
    resp = b""
    while (time.ticks_ms() - prvMills) < timeout:
        if uart.any():
            resp = b"".join([resp, uart.readline()])
    if resp:
        print("response: " + resp.decode())
        print("_______________________________")
        return resp
    else:
        print("No response")
        print("_______________________________")
    return None
########################################################################    
    
########################################################################
def send_sms(msgtext):
    global gsm_buffer
    result = send_command('AT+CMGS="{}"'.format(destination_phone), msgtext, 99)
    print("gsm_buffer: " + gsm_buffer)
    return gsm_buffer
########################################################################    

# Basic initialization commands to set up the SIM800 module.

print("Checking for sim module presence ...")
print(send_command('AT'))  # Check module presence

print("Turn off command echoing ...")
print(send_command('ATE0'))  # Turn off command echoing

print("Setting full functionality mode ...")
print(send_command('AT+CFUN=1'))  # Set full functionality mode

print("Setting extended error message reporting ...")
print(send_command('AT+CMEE=1'))  # Enable extended error message reporting

print("Show what type of sms-encoding is used ...")
encodingType = send_command('AT+CSCS?')  # Show what type of sms-encoding is used

if '+CSCS: "GSM"' not in encodingType:
    print("Set sms-encoding to GSM ...")
    print(send_command('AT+CSCS="GSM"'))  # Set sms-encoding to GSM

# Check if device text mode is PDU or Text
print("Check device text mode ...")
textMode = send_command('AT+CMGF?')  # Check message format

if '+CMGF: 1' not in textMode:
    # Set device text mode to Text
    print("Set device text mode to Text ...")
    print(send_command('AT+CMGF=1'))  # Set mode to Text

print("Sending sms ...")
print(send_sms("hey, test text. imework?"))

# Additional commands for debugging purposes
def sendCMD_waitResp(cmd, uart=uart0, timeout=8000):
    print("CMD: " + cmd)
    uart.write(cmd)
    waitResp(uart, timeout)
    print()
    
def waitResp(uart=uart0, timeout=8000):
    prvMills = time.ticks_ms()
    resp = b""
    while (time.ticks_ms() - prvMills) < timeout:
        if uart.any():
            resp = b"".join([resp, uart.readline()])
    if resp:
        print("response: " + resp.decode())