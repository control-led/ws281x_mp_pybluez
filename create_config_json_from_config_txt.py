import json,re
  
  
# the file to be converted to  
# json format 
filename = 'config.txt'
  
# dictionary where the lines from 
# text will be stored 
json_out = {} 

# creating dictionary 
with open(filename) as fh:
    
    for line in fh:
        parameter_to_search= re.compile(r'\d+\W+[#]')
        value_to_search = re.compile(r'\w+\W[=]')
        matches_parameter_to_search= parameter_to_search.finditer(line)
        matches_value_to_search = value_to_search.finditer(line)
        
        for matches in zip(matches_parameter_to_search,matches_value_to_search):
            key_for_dict = matches[1].group().split(" ")[0]
            value_for_dict = int(matches[0].group().split(" ")[0])
            json_out.update({key_for_dict:value_for_dict})
                
    fh.close()
    
            #print("The raw expression {} is found on {}".format(line, matches))
            

# creating json file 
# the JSON file is named as config_dumped.json
with open("config.json", "w") as file:
    json.dump(json_out, file, sort_keys = False)
    file.close()
#out_file.close() 
