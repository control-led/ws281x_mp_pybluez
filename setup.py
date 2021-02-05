##!/usr/bin/env python

from setuptools import setup,find_packages
import os, time, json
value = input("This will install the Control LED Strip App. Do you wish to continue (Y/N)?")                

if value == "Y":
    pass
else:
    exit()


os.system("echo Initiate the LED Strip config in now...")
json_out= {}

questions = ["Number of LED Pixels?:  ", "GPIO PIN connected to the pixel (10 uses SPI):  ", "LED Signal frequency in hertz (usually 800000):  ", "DMA channel to use for generating signal (try10)","Set 0 for darkest and 255 for brightest:  ", "Set to '1' for GPIOs 13,19,41,45 or 53:  "]
             
keys = ["LED_COUNT", "LED_PIN", "LED_FREQ_HZ", "LED_DMA", "LED_BRIGHTNESS",  "LED_CHANNEL"]



def check_value_int(text):
    try:
        value = input(text)
        if value.isnumeric() == False:
            raise ValueError
        elif value.isnumeric() == True:
            return int(value),True
    except ValueError:
        print("Please fill in a decimal number!")
        return value,False
    return int(value),False


def check_value_bool(text):
    try:
        value = input(text)
        if isinstance(bool(value),bool) == False:
            raise ValueError
        elif isinstance(bool(value), bool) == True:
            return bool(value),True
    except ValueError:
        print("Please fill in a boolean expression!")
        return value,False
    return bool(value),False
    
    
for index, key in enumerate(keys):
    correct = False
    while correct!=True:

        value,correct= check_value_int(questions[index])
        
    
    json_out.update({key: value})

with open("config.json", "w") as  file:
    json.dump(json_out, file, sort_keys= False)


if json_out.get("LED_PIN") == 10 or 38:
    os.system("echo You connected the Strip to Pin " +str(json_out.get("LED_PIN")) +", so you need to enable SPI Bus")
    time.sleep(1)
    os.system("Checking if SPI is enabled...")
    import subprocess
    return_value =subprocess.check_output("sudo raspi-config nonint get_spi", stderr=subprocess.STDOUT, shell = True)
    return_value = int(return_value.decode("utf-8").replace("\n", " "))
    if return_value == 1:
        value = input("Your SPI Port is not enabled. Enable now (Y/N)")
        if value == "Y":
            os.system("sudo raspi-config nonint do_spi 0")
            time.sleep(0.5)
            os.system("echo Your SPI Port is now enabled!")
        if value == "N":
            os.system("echo Exit setup now till SPI Port is actived by yourself!")
            exit()
    if return_value == 0:
        os.system("echo Your SPI Port is already enabled! Continue installing files...")
        os.system("echo Install the bluetooth header files now...")

time.sleep(3)
os.system("sudo apt-get install libbluetooth-dev")

os.system("echo Now installing the rpi_ws281x and the pybluez2 library!")
time.sleep(3)


def _post_install():
    print("echo Now, the librarys pybluez2 and rpiws281x are installed. Set some important Bluetooth settings now...")
    import re, fileinput, sys
    filename = '/etc/systemd/system/dbus-org.bluez.service'
    try:
        for line in fileinput.input(filename, inplace = True):
            keyword_to_search =re.compile(r'ExecStart=/usr/lib/bluetooth/bluetoothd(\s[-][-]\w+)?')
            k_matches = keyword_to_search.finditer(line)
            for k_match in k_matches:
                line = line.replace(k_match.group(), "ExecStart=/usr/lib/bluetooth/bluetoothd --compat")

            sys.stdout.write(line)  

        fileinput.close()
    except FileNotFoundError:
        print("A File couldn't be found. Contact the developer of this Programm!")
    finally:
        print("Installation completed!")
        time.sleep(1)

    value = input("Do you want to autostart the ws281x_mp_pybluez programm when the raspberrypi boots?(Y/N)")
    
    if value == "Y":
        try:
            filename = '/etc/rc.local'                                                     #hier in linux pfad aendern
            with fileinput.input(filename, inplace = True) as f:
                for line in f:
                    keyword_to_search =re.compile(r'exit 0')   #search for word exit in file
                    k_matches = keyword_to_search.finditer(line)
                    for k_match in k_matches:
                        line = line.replace(k_match.group(), "sudo python3 -O /home/pi/ws281x_mp_pybluez/main.py &") #hier file einfügen
                    sys.stdout.write(line)  
                fileinput.close()

            file_object = open(filename, 'a')
            file_object.write("\nexit 0")
            file_object.close()

        except FileNotFoundError:
            print("There were error while setting the python file as autostart in /etc/rc.local")
        finally:
            pass
    else:
        pass
        
    
    value = input("Do you want to reboot now? Reboot makes the changes effective.(Y/N)")

    if value == "Y":
        os.system("sudo reboot now")
    elif value == "N":
        exit()
        
          
setup(
    name='rpi_ws281x_mp_pybluez',
    version = '0.0.1',
    description = 'Control LED Strips via multiprocessing and bluetooth connection',
    long_description=open("README.txt").read(),
    author ='Alexander Hoch',
    author_email='a.hoch90@gmail.com',
    license = 'MIT-license',
    url='https://pypi.python.org/pypi/multiprocessing_ledstrip',
    keywords=['ledstrip', 'app', 'raspberrypi'],
    install_requires = [
    "rpi-ws281x == 4.1.0",
    "pybluez2 == 0.41"],
    python_requires = '>3.5')
    


_post_install()








        








    
