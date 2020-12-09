import threading
import logging
import uuid
import json
from bluetooth import *
from includes.readfile import parse_data_from_bluetooth, dump_data
logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(name)s :: %(levelname)s :: %(process)s :: %(message)s')
logger = logging.getLogger(__name__)

class BtServer():

    def __init__(self):
        self.server_socket = None
        self.socks = list()

    def init_socket(self):
        self.server_socket = BluetoothSocket( RFCOMM )
        self.server_socket.bind(('', PORT_ANY))
        self.server_socket.listen(1)
        port = self.server_socket.getsockname()[1]
        uuid1 = str(uuid.uuid4())                     								
        advertise_service(self.server_socket, "TestServer",
			service_id = uuid1,
			service_classes = [ uuid1, SERIAL_PORT_CLASS ],
                        profiles = [ SERIAL_PORT_PROFILE ] )
        logger.info('BtServer is listening on port {}.'.format(port))

    
    def send(self, data):
        for sock in self.socks:
            sock.send(data.encode('utf-8'))

    
    def run(self, blue_child):
        self.init_socket()
        while True:
            logger.info('waiting for connecting...')
            sock, info = self.server_socket.accept()
            logger.info('{}  connected!'.format(str(info[0])))
            self.socks.append(sock)
            self.serve_socket(sock, info[0], blue_child)
            
    
    def serve_socket(self, sock, info, blue_child):  
        import re
        while True:
            try:
                rcv = sock.recv(1024).decode('utf-8')
                if rcv.strip() == 'STOP':
                    blue_child.send('STOP')   
                    logger.info("Stop Animations now.")
                    
                elif rcv.strip() =='START':
                    blue_child.send('START')
                    logger.info("Start Animations now.")
                    
                elif rcv.strip() =='END':
                    blue_child.send('END')
                    logger.info("Shutdown Programm.")

                elif rcv.strip() =='STATUS':
                    blue_child.send('STATUS')
                    while blue_child.poll() == False:
                        pass
                    status = blue_child.recv()
                    BtServer.send(self,str(status))
                    
                elif len(rcv.split()) == 4:
                    format_data = parse_data_from_bluetooth(rcv)
                    dump_data(format_data)
                    logger.info("Dumped data in parameters.json")
                          
                elif len(rcv.split()) == 1:         #Checks the incoming text with regex operations, to ensure its formated right for operations.
                    
                    pats = [re.compile(expression) for expression in ['\W\WSeg\d\W\W\W\d+\W\W','\W\WSeg\d\W\W\W\W\d+\W\d+\W\d+\W\W\W',]]
                    for pat in pats:
                        if re.search(pat, rcv) is not None:
                            for match in pat.finditer(rcv): 
                                blue_child.send(rcv[match.span()[0]:match.span()[1]])
                                    
                else:
                    logger.critical("Couldnt recognize incoming data {}".format(rcv))
            
            except Exception as e:
                logger.critical(str(e))
                logger.critical("There is an Error receiving bluetooth data. Pipe will be closed.")
                self.server_socket.close()          #if connection get lost close server_socket and reinit bluetooth server
                BtServer().run(blue_child)   
                        

def get_data_from_bluetooth(blue_child):  #Start BluetoothServer
    BtServer().run(blue_child)
    

    
    



