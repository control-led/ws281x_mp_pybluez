import json, logging, traceback

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(name)s :: %(levelname)s :: %(process)s :: %(message)s')
logger = logging.getLogger(__name__)

def dump_data(data):
    
    with open("parameters.json","w") as file:
        json.dump(data, file, indent=2)
        file.close()
        


def read_data_from_file(filename):

    with open(filename) as file:
        try:
            data = json.load(file)
            
        except:
            logger.critical("There were errors in reading parameters.json")
            return 'ERROR'

        finally:
            logger.info("Successfully loaded parameters.json")
            file.close()
            return data


def read_config_file(filename):

    with open(filename) as file:
        try:
            set_config = json.load(file)
            
        except:
            logger.critical("There were errors in reading config file")
            return 'ERROR'

        finally:
            logger.info("Successfully loaded config.json")
            file.close()
            return set_config
            
            
            

def parse_data_from_bluetooth(string):
    try:
        new_value = string.split()
        new_data = []
        for val in new_value:
            new_data.append(json.loads(val[1:-1]))
            
    except:
        logging.error("Error occurs in: %s", traceback.format_exc())
        logging.info("Parameters could not be changed ... continue with old parameters.json file")
        
    finally:
        return new_data



