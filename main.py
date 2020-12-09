#! /usr/bin/env python3

import multiprocessing
import time
import json
from includes.led_animations import LED_Segment
from includes.readfile import read_data_from_file, parse_data_from_bluetooth, read_config_file
#from led_animations import LED_Segment
import logging
import traceback
import os
import signal
import sys


if __debug__ == False:
    from rpi_ws281x import PixelStrip


#start = time.perf_counter()    
global POISON_PILL
POISON_PILL = 'STOP'
global running
running = False
global count_update_strip
count_update_strip = 0

    
logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(name)s :: %(levelname)s :: %(process)s :: %(message)s')
    

def start_led_animations(arglist, q,  Lock, pid_list =[], run_flag_list = [], *args):
    """Initiates the LED_Animation classes and start the animations as childprocesses"""
    global running
    params_led_animations = list(zip(arglist[0],arglist[1],arglist[2],arglist[3], arglist[4]))         

    for index,param in enumerate(params_led_animations):  
    
        call_function = getattr(LED_Segment(param[0],param[1], param[2], param[3]), param[4])
        run_flag = multiprocessing.Value('i', 1, lock= True)
        run_flag_list.append(run_flag)
        pid_list.append(multiprocessing.Process(target=call_function, args= (q, Lock, run_flag)))                   
        pid_list[index].daemon = False
        pid_list[index].start()

    running = True
    logging.info(pid_list)
    return pid_list, run_flag_list
    

def get_data_from_childs(conn, Lock, q, data_package=[]):   
    """Get the data from the led animations class in queue (q). Send one data package to parent conn handled in function "transmit data" when received POISONPILL from queue"""

    while True:
        try:
            if q.empty() == False:                                      
                inc_value = q.get()
                data_package.append(inc_value)
                if inc_value == POISON_PILL:                                 
                    conn.send(data_package[:-1])                        
                    conn.send(POISON_PILL)                             
                    data_package = []
            
            elif conn.poll() == True:
                if conn.recv()== POISON_PILL:
                    break

        except (BrokenPipeError, IOError, EOFError):
            logging.error("uncaught exception: %s", traceback.format_exc())
            break
            
    return 0
            
    

def create_arglist(parsed_list, index, start_led =[], stop_led=[], delay=[], color=[], function =[]):
    """Creates the parameters from the arguments loaded from the dumped parameters.json file and save it in lists"""
    import multiprocessing
    
    if index == 0:              
        params = []
        stack_args = [start_led, stop_led, delay, color, function]

        for args in stack_args:
            params.append(args.copy())
            args.clear()
                     
        return params[0], params[1], params[2], params[3], params[4]


    delay.insert(0, multiprocessing.Value('i', int(parsed_list[3].get("Seg"+str(index))),lock=True))
    function.insert(0, str(parsed_list[1].get("Seg"+str(index))))
    color.insert(0, multiprocessing.Array('i', [int(value) for value in parsed_list[2].get("Seg"+str(index))[1:-1].split(',')], lock=True))
    start_led.insert(0,int(parsed_list[0].get("Seg"+str(index-1)) if parsed_list[0].get("Seg"+str(index-1)) is not None else 0))
    stop_led.insert(0,int(parsed_list[0].get("Seg"+str(index))))
    
    return create_arglist(parsed_list, index-1, start_led, stop_led, delay, color, function)


def show_led_strip(data_act, strip= None):
    """Shows the set LED Pixels on Strip"""
    if __debug__== True: 
        logging.info(data_act)
    
    else: 
        for led in range(0, len(data_act), 1):
            strip.setPixelColor(led, data_act[led][0][1])
        strip.show()
    

def fill_memory_with_zeros(arglist):
    """Init the length of the Array for the each led Pixel and sets a container for the RGB Values"""
    data_act = []
    set_led = tuple(x for x in range(arglist[1][-1]+1))
    for val_led in set_led:
        data_act.append([(val_led, 0)]) 
    return data_act
        
    
def init_led_strip(arglist):  
    """Initiates with the dumpload the config.json to programm the ws_281x Pixel strip. """
    global running
    global reinit
    data_act = fill_memory_with_zeros(arglist)

    if __debug__: 
        return data_act

    else:
        try:
            config_data= read_config_file('config.json')
            logging.info(config_data)
            if len(config_data)!= 6:
                raise Exception 
            strip=PixelStrip(len(data_act), config_data.get('LED_PIN'), config_data.get('LED_FREQ_HZ'), config_data.get('LED_DMA'), False, config_data.get('LED_BRIGHTNESS'), config_data.get('LED_CHANNEL'))
            strip.begin()

        except:
            logging.error("uncaught exception: %s", traceback.format_exc())
            logging.critical("Problems in initialize the rpi_ws281x library. Shutdown programm now...")
            running = False
            reinit = False

        finally:
            return strip, data_act


def transfer_data(arglist, parent_conn, run_flag_list, *args):
    """Transfer data between the childprocesses who runs the LED Animation an the bluetooth connection which receives data from android phone """
    global running
    global count_update_strip
    reinit = False

    if __debug__ == True:
        data_act = init_led_strip(arglist)
    else:
        strip, data_act = init_led_strip(arglist)
    
    while running == True:  
        if parent_conn.poll() == True:
            try:
                data_block = []
                while True:   
                    new_value = parent_conn.recv()
                    if new_value == POISON_PILL:
                        break                    
                    data_block.insert(-1,new_value)
                for data in range(len(data_block[0])):
                    data_act.pop(data_block[0][data][0])
                    data_act.insert(data_block[0][data][0],[(data_block[0][data][0], data_block[0][data][1])])
                data_block= []
        
            except:  

                logger.error("uncaught exception: %s", traceback.format_exc())
                logging.error(data_block[0][data][0])
                break

        elif __debug__ == False:  
            if blue_conn_parent.poll() == True:
                try:
                    blue_recv= blue_conn_parent.recv()
                    if blue_recv == 'STOP':                     #Stop the animations
                        for run_flag in run_flag_list:                       
                            run_flag.value = 0
                        logging.info("Pause animations!")
    
                    elif blue_recv == 'START':                  #Start the animations
                        logging.info("Start animations")
                        for run_flag in run_flag_list:
                            run_flag.value  = 1

                    elif blue_recv == 'END':                    #End the animations
                        running = False
                        reinit = True
                        
                        for run_flag in run_flag_list:
                            run_flag_list.remove(run_flag)
                        
                        logging.info("Terminate Processes now and reinit program!")
                        break

                    elif blue_recv =='SHUTDOWN':                #Shutdown the raspberrypi
                        running = False
                        reinit = False
                        for run_flag in run_flag_list:
                            run_flag_list.remove(run_flag)
                        
                        logging.info("Terminate Processes now and shutdown program!")
                        break

                    elif blue_recv =='STATUS':
        
                        blue_conn_parent.send(run_flag_list[0].value)
                        
                        

                    else:
                        data_value= []
                        data_value = parse_data_from_bluetooth("'{}'".format(blue_recv))

                        if len(data_value)>0:      

                            if len(list(data_value[0].values())[0])<4:
                                parsed_data= [int(item) for item in list(data_value[0].values())[0].split(',')]
                                parsed_key = int(list(data_value[0].keys())[0][-1])

                            elif len(list(data_value[0].values())[0])>4:
                                parsed_data = [int(item) for item in (list(data_value[0].values())[0][1:-1].split(','))]
                                parsed_key = int(list(data_value[0].keys())[0][-1])


                            if len(parsed_data) == 1:
                                arglist[2][parsed_key-1].value = parsed_data[0]


                            elif len(parsed_data) == 3:
                                arglist[3][parsed_key-1].get_obj()[:]= [int(item) for item in parsed_data]
          
                except:
                    logging.error("Error occurs in: %s", traceback.format_exc())
                    logging.error("There were errors in receiving bluetooth data")
                    
            
        if __debug__ == True:    
            show_led_strip(data_act)
            count_update_strip = count_update_strip + 1
            

        else:
            show_led_strip(data_act, strip)
            count_update_strip = count_update_strip + 1   

    if __debug__ == True:
        return count_update_strip, reinit, run_flag_list
    else:
        
        return count_update_strip, reinit, run_flag_list, strip          

   
def terminate_processes(parent_conn, pid_list, p, arglist, strip = None):  
    """Terminates the led animations by sending a signal.SIGKILL"""
    parent_conn.send(POISON_PILL)
    if __debug__ == False:
        show_led_strip(fill_memory_with_zeros(arglist), strip)
    os.kill(p.pid, signal.SIGKILL)
    
    logging.info("get_data_from_child_process is terminated")
    logging.info("terminate the child processes now")
    
    for child_process in pid_list:
        try:
            os.kill(child_process.pid, signal.SIGKILL) 
            time.sleep(0.1)
            if child_process.is_alive() == False:
                test ="SUCCESS"

            elif child_process.is_alive() == True:
                test = "ERROR" 
                return result
        except:
            logging.info("Error")
            return "ERROR"
                       
        finally:
            if p.is_alive() == True:
                test = "ERROR"

    pid_list.clear()

    result = test
    return result, pid_list
    


def import_parameters_from_file():
    """Imports the parameters for the led animations from file parameters.json"""
    
    parsed_list = read_data_from_file('parameters.json')

    if parsed_list == 'ERROR':
        pass
    
    else:
        pass
    return parsed_list


def init_animations(parsed_list, pid_list, run_flag_list):
    """Init multiprocessing services and create the objects for the led animations"""
    
    multiprocessing.freeze_support()   
    q = multiprocessing.Queue()  
    Lock = multiprocessing.Lock()    
    arglist = create_arglist(parsed_list, len(parsed_list[0]))
    logging.info(arglist)
    pid_list, run_flag_list = start_led_animations(arglist, q, Lock, pid_list)
    parent_conn, child_conn = multiprocessing.Pipe()
    p = multiprocessing.Process(target=get_data_from_childs, args=(child_conn, Lock, q)) 
    p.start()
    
    return p, pid_list, run_flag_list, arglist, parent_conn, child_conn


def start_the_routine(*args):
    """Starts the main routine for the first time or after getting new parameters.json file from bluetooth"""

    global count_update_strip

    if 'pid_list' and 'run_flag_list' in locals():
        pass
    
    elif 'pid_list' and 'run_flag_list' not in locals():
        pid_list = []
        run_flag_list = []

    parsed_list = []
    
    if __debug__ == False:
        logging.info("DEBUG FALSE")
        try:
            
            parsed_list = import_parameters_from_file()
            
        except FileNotFoundError:
            logging.critical("There is no parameters.json file on your filesystem. Run the parameters.exe on your raspberrypi or create and send the paramters.json file with the Control LED with raspberrypi App, available in Google Play Store!")
            message =input("Do you want to close the script now? If you press N the script will wait till you send parameters.json file via Control LED with raspberrypi App(Y/N)")
            if message == "Y":
                exit()
            elif message == "N":
                os.system("Starting Bluetooth Connection and wait from respond from the Control LED with raspberrypi App")
                while not os.path.isfile("parameters.json") == True:
                    continue
        finally:
            p, pid_list, run_flag_list, arglist, parent_conn, child_conn = init_animations(parsed_list, pid_list, run_flag_list)
            count_update_strip, reinit, run_flag_list, strip = transfer_data(arglist, parent_conn, run_flag_list, blue_conn_parent)
                
                
            
    else:
        logging.info("DEBUG TRUE")
        try:
            parsed_list = import_parameters_from_file()
        except FileNotFoundError:
            logging.critical("There is no parameters.json file on your filesystem. Run the parameters.exe on your raspberrypi or create and send the paramters.json file with the Control LED with raspberrypi App, available in Google Play Store!")
            message =input("Do you want to close the script now? If you press N the script will wait till you send parameters.json file via Control LED with raspberrypi App(Y/N)")
            if message == "Y":
                exit()
            elif message == "N":
                os.system("Starting Bluetooth Connection and wait from respond from the Control LED with raspberrypi App")
                while not os.path.isfile("parameters.json") == True:
                    continue
        finally:
            p, pid_list, run_flag_list, arglist, parent_conn, child_conn = init_animations(parsed_list,pid_list, run_flag_list)
            count_update_strip, reinit, run_flag_list  = transfer_data(arglist, parent_conn, run_flag_list)
                      

    status = terminate_processes(parent_conn, pid_list, p, arglist, strip)  

    if reinit == True:
        parent_conn.close()
        child_conn.close()
        return start_the_routine(blue_conn_parent, blue_conn_child, count_update_strip, run_flag_list, pid_list)

    elif reinit == False:
        return count_update_strip



        
if __name__ =='__main__':
    """Main routine which starts the bluetooth receive process and the the start_routine_function to start the animation and transmit data between bluetooth process and ED Segment instances as child process"""
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(name)s :: %(levelname)s :: %(process)s :: %(message)s')
    logger = logging.getLogger(__name__)

    if __debug__ == False:
        #Debug Mode OFF
        logging.info("Start with bluetooth")
        #Setting up Connection
        logging.info("Create serial port communication")
        os.system("sudo sdptool add SP")
        time.sleep(0.5)
        logging.info("Set raspberrypi to scan bluetooth devices") 
        os.system("sudo hciconfig hci0 piscan")
        from includes.conn_bluetooth import get_data_from_bluetooth
        blue_conn_parent, blue_conn_child = multiprocessing.Pipe()
        bluet = multiprocessing.Process(target=get_data_from_bluetooth, args= (blue_conn_child,))
        bluet.start()  
        count_update_strip = start_the_routine(blue_conn_parent, blue_conn_child, count_update_strip)

    else:
        count_update_strip = start_the_routine(count_update_strip)

    #finish = time.perf_counter()

    #logger.info("The Programm runs {} seconds and updates the strip {} times.".format(str({round(finish-start,2)}), count_update_strip))
    #logger.info("Shutdown Programm ...")
