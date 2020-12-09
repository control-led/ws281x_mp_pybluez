class LED_Segment(object):
    """ LED animations class with led animations as functions """
    global wheel
    global Color
    global POISON_PILL
    POISON_PILL ='STOP'    
    
    #start_led: int, stop_led = int, chosen_color = tuple(x,x,x), delay= int
    def __init__(self, start_led, stop_led, delay, chosen_color=None, running = True):  
        self.start_led = start_led
        self.stop_led = stop_led   
        self.delay = delay 
        self.color = chosen_color if chosen_color is not None else None
        self.running = running
    

    def Color(red, green, blue, white=0):
        """Convert the provided red, green, blue color to a 24-bit color value.
        Each color component should be a value 0-255 where 0 is the lowest intensity
        and 255 is the highest intensity.
        """
        return (white << 24) | (red << 16) | (green << 8) | blue    
    

    def wheel(pos):
        """Generate colors in color palette 0-255 positions and convert the rgb value in hex format."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)    

    
    def colorWipe(self, q, l, run_flag): 
        import time, multiprocessing,logging,asyncio
        logger = logging.getLogger(__name__) 
        logger.info("Start colorWipe on Process {}".format(multiprocessing.current_process()))
        
        while True:
            for led in range(self.start_led, self.stop_led, 1): 
                try:
                    l.acquire()
                    q.put((led, Color(self.color.get_obj()[0],self.color.get_obj()[1],self.color.get_obj()[2])))
                    
                except (BrokenPipeError, IOError, EOFError):
                    pass

                finally: 
                    q.put(POISON_PILL)
                    l.release()
                    time.sleep(self.delay.value/1000.0)
                    if run_flag.value == 0:
                        logger.info("Stopped color Wipe on Process {}".format(multiprocessing.current_process()))
                        while run_flag.value == 0:
                            pass

            for led in range(self.start_led, self.stop_led, 1):
                try:
                    l.acquire()
                    q.put((led, Color(0,0,0)))
                except (BrokenPipeError, IOError, EOFError):
                    pass
                
                finally:
                    q.put(POISON_PILL)
                    l.release()            

 
    def theaterChase(self, q, l, run_flag):
        import time, multiprocessing,logging 
        logger = logging.getLogger(__name__) 
        logger.info("Start animation theaterChase on Process {}".format(multiprocessing.current_process()))

        while True:
            for j in range(256):
                for z in range(3):
                    try:
                        l.acquire()
                        for led in range(self.start_led, self.stop_led, 3):
                            q.put((led+z, Color(self.color.get_obj()[0],self.color.get_obj()[1],self.color.get_obj()[2])))
                    except (BrokenPipeError, IOError, EOFError):
                        pass
                    
                    finally:
                        q.put(POISON_PILL)
                        l.release()
                        time.sleep(self.delay.value/ 1000.0)
                        if run_flag.value == 0:
                            logger.info("Stopped animation theaterChase on Process {}".format(multiprocessing.current_process()))
                            while run_flag.value == 0:
                                pass  
                    try: 
                        l.acquire()
                        for led in range(self.start_led, self.stop_led, 3):
                            q.put((led+z, Color(0,0,0)))
                            
                    except (BrokenPipeError, IOError, EOFError):
                        pass                    
                            
                    finally:
                        q.put(POISON_PILL)
                        l.release()
                
    
    def theaterChaseRainbow(self, q, l, run_flag):
        import time, multiprocessing,logging 
        logger = logging.getLogger(__name__) 
        logger.info("Start theaterChaseRainbow on Process {}".format(multiprocessing.current_process()))        
        while True:
            for j in range(256):
                for z in range(3):
                    try:
                        l.acquire()
                        for led in range(self.start_led, self.stop_led, 3):
                            q.put((led +z, wheel((led + j) % 255)))
                   
                    except (BrokenPipeError, IOError, EOFError):
                        pass   
                    
                    finally:
                        q.put(POISON_PILL)
                        l.release()
                        time.sleep(self.delay.value / 1000.0)
                    try:
                        l.acquire()
                        for led in range(self.start_led, self.stop_led, 3):
                            q.put((led + z, 0))
                            
                    except (BrokenPipeError, IOError, EOFError):
                        pass 
                    
                    finally: 
                        q.put(POISON_PILL)
                        l.release()
                        if run_flag.value == 0:
                            logger.info("Stopped theaterChaseRainbow on Process {}".format(multiprocessing.current_process()))
                            while run_flag.value == 0:
                                pass
                    
                                  
    def rainbow(self, q, l, run_flag):   
        import time, multiprocessing,logging 
        logger = logging.getLogger(__name__) 
        logger.info("Started rainbow on Process {}".format(multiprocessing.current_process()))

       
        while True:
            for j in range(256):
                try:
                    l.acquire()
                    for i in range(self.start_led, self.stop_led, 1):
                        q.put((i, wheel(((i + j) & 255))))
                        
                except (BrokenPipeError, IOError, EOFError):
                    break
             
                finally:
                    q.put(POISON_PILL)
                    l.release()
                    time.sleep(self.delay.value/ 1000.0)
                    
                    if run_flag.value == 0:
                            logger.info("Stopped Rainbow on Process {}".format(multiprocessing.current_process()))
                            while run_flag.value == 0:
                                pass


    def rainbowCycle(self, q, l, run_flag):
        import time, multiprocessing,logging 
        logger = logging.getLogger(__name__) 
        logger.info("Start rainbowCycle on Process {}".format(multiprocessing.current_process()))
        while True:
            for j in range(256):
                try:
                    l.acquire()
                    for i in range(self.start_led, self.stop_led, 1):
                        q.put((i, wheel((int(i * 256 / (self.stop_led- self.start_led)) + j) & 255)))          
                except (BrokenPipeError, IOError, EOFError):
                    pass
                
                finally:
                    q.put(POISON_PILL)
                    l.release()
                    time.sleep(self.delay.value / 1000.0)
                    if run_flag.value == 0:
                        logger.info("Stopped rainbow Cycle on Process {}".format(multiprocessing.current_process()))
                        while run_flag.value == 0:
                            pass
       
                                    
    def pulsing_light(self, q, l, run_flag):
        import time, multiprocessing,logging 
        import math
        logger = logging.getLogger(__name__) 
        logger.info("Started Pulsing Light on Process {}".format(multiprocessing.current_process()))        
        while True:
            position = 0
            for i in range((self.stop_led-self.start_led)*2):
                position = position +1
                try:
                    l.acquire()
                    for j in range(self.start_led, self.stop_led,1):
                        q.put((j, Color(round(((math.sin(j+position) * 127 + 128)/255)*self.color.get_obj()[0]),round(((math.sin(j+position) * 127 + 128) /255)*self.color.get_obj()[1]), round(((math.sin(j+position) * 127 + 128) /255)*self.color.get_obj()[2]))))
                        
                except (BrokenPipeError, IOError, EOFError):
                    pass
                
                finally:
                    q.put(POISON_PILL)
                    l.release()
                    time.sleep(self.delay.value /1000.0)
                    if run_flag.value == 0:
                        logger.info("Stopped Pulsing Light on process {}".format(multiprocessing.current_process()))
                        while run_flag.value == 0:
                            pass
                    
                

    def strobe(self, q, l, run_flag, strobe_count=7, pulse_count=12):
        from random import randrange
        import time, multiprocessing,logging 
        logger = logging.getLogger(__name__) 
        logger.info("Started Strobe on Process {}".format(multiprocessing.current_process()))    
        while True:
            for strobe in range(strobe_count):    
                for pulse in range(pulse_count):
                    try:
                        l.acquire()                
                        for i in range(self.start_led, self.stop_led, 1):
                            q.put((i, Color(self.color.get_obj()[0], self.color.get_obj()[1], self.color.get_obj()[2])))
                            
                    except (BrokenPipeError, IOError, EOFError):
                        pass
                    
                    finally:
                        q.put(POISON_PILL)
                        l.release()
                        time.sleep(randrange(0,45,1) /1000.0)
                    try: 
                        l.acquire()
                        for i in range(self.start_led, self.stop_led, 1):
                            q.put((i, Color(0,0,0)))
                            
                    except (BrokenPipeError, IOError, EOFError):
                        pass
                    
                    finally:
                        q.put(POISON_PILL)
                        l.release()
                        if run_flag.value == 0:
                            logger.info("Stopped Strobe on Process {}".format(multiprocessing.current_process()))
                            while run_flag.value == 0:
                                pass
                    time.sleep(self.delay.value/1000.0)


    def bouncing_balls(self, q, l, run_flag, ball_count=2, wait_ms=200):
        import time, multiprocessing,logging  
        import math
        logger = logging.getLogger(__name__) 
        logger.info("Starting Bouncing Balls on Process {}".format(multiprocessing.current_process()))      
        start_time = time.time()
        ClockTimeSinceLastBounce = [0 for i in range(ball_count)]
        StartHeight=1
        
        for i in range(ball_count):
            ClockTimeSinceLastBounce[i] = time.time()
            
        Height = [0 for i in range(ball_count)]
        Position = [0 for i in range(ball_count)]
        ImpactVelocity = [0 for i in range(ball_count)]
        ImpactVelocityStart= math.sqrt(-2 * -9.81 * 1)
        Dampening = [0 for i in range(ball_count)]
        TimeSinceLastBounce = [0 for i in range(ball_count)]
        
        for i in range(0,ball_count,1):
            last_ClockTimeSinceLastBounce = ClockTimeSinceLastBounce[i]
            ClockTimeSinceLastBounce[i] = time.time() - last_ClockTimeSinceLastBounce
        
            Height[i] = StartHeight
            Position[i] = 0
            ImpactVelocity[i] = math.sqrt(-2 * -9.81 * 1)
            TimeSinceLastBounce[i] = 0
            Dampening[i] = 0.90 - (float(i)/(ball_count**2))
        
        while True:
            for i in range(ball_count):
                TimeSinceLastBounce[i] = time.time() - ClockTimeSinceLastBounce[i]
                Height[i] = 0.5 * (-9.81) * (TimeSinceLastBounce[i]**2) + ImpactVelocity[i] * TimeSinceLastBounce[i]
                if (Height[i] < 0):
                    Height[i] = 0
                    ImpactVelocity[i] = Dampening[i] * ImpactVelocity[i]
                    ClockTimeSinceLastBounce[i] = time.time()
                    if (ImpactVelocity[i] < 0.01):
                        ImpactVelocity[i] = ImpactVelocityStart              
                Position[i] = round(Height[i] * ((self.stop_led - self.start_led)-1)/StartHeight)   
                
            try:
                l.acquire()
                for i in range(ball_count):
                    q.put((self.start_led + Position[i], Color(self.color.get_obj()[0], self.color.get_obj()[1], self.color.get_obj()[2])))
                    
            except (BrokenPipeError, IOError, EOFError):
                pass
            
            finally:
                q.put(POISON_PILL)
                l.release()  
                time.sleep(0.1)
                if run_flag.value == 0:
                    logger.info("Stopped Bouncing Balls on Process {}".format(multiprocessing.current_process()))
                    while run_flag.value == 0:
                        pass
            
            try: 
                l.acquire()
                for i in range(self.start_led, self.stop_led, 1):
                    q.put((i, Color(0,0,0)))
                    
            except (BrokenPipeError, IOError, EOFError):
                pass 
            
            finally:
                q.put(POISON_PILL)
                l.release()
        

    def snow_sparkle(self, q, l, run_flag):
        import time, multiprocessing,logging 
        from random import randint
        logger = logging.getLogger(__name__) 
        logger.info("Starting Snow Sparkle on Process {}".format(multiprocessing.current_process()))        
        while True:
            pixel= randint(0, self.stop_led - self.start_led)
            speed_delay=randint(100,1000)
            try:
                l.acquire()
                for i in range(self.start_led, self.stop_led, 1):
                    q.put((i, Color(16,16,16)))
            except (BrokenPipeError, IOError, EOFError):
                pass
            
            finally:
                q.put(POISON_PILL)
                l.release()
                time.sleep(speed_delay/1000.0)
                if run_flag.value == 0:
                    logger.info("Stopped Snow Sparkle on Process {}".format(multiprocessing.current_process()))
                    while run_flag.value == 0:
                         pass

            try:
                l.acquire()
                q.put((self.start_led+pixel, Color(255,255,255)))
                
            except (BrokenPipeError, IOError, EOFError):
                pass
            
            finally:
                q.put(POISON_PILL)
                l.release()
                time.sleep(self.delay.value /1000.0 )
            
