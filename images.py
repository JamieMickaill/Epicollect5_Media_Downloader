
import requests
import json
import csv
#update with dataset name downloaded from epicollect

MEDIAURL = 'https://five.epicollect.net/api/export/media/'

def load_variables(filename):
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
        
    FILENAME = data.get("FILENAME")
    NAMECOLS = data.get("NAMECOLS")
    IMGCOLS = data.get("IMGCOLS")
    SLUG = data.get("SLUG")
    APPID = data.get("APPID")
    IMAGE_FOLDER = data.get("IMAGE_FOLDER")
    if(APPID == ''):
        print("No App ID provided, assuming project has public status in Epicollect")
    return FILENAME, NAMECOLS, IMGCOLS, SLUG, APPID, IMAGE_FOLDER
    

def get_image(imagestring, imagename,APPID,SLUG):
    if not APPID == None:
        params = {
        'type': 'photo',
        'format': 'entry_original',
        'name' : imagename,
        'access_token' : APPID
        }
    else:
        params = {
        'type': 'photo',
        'format': 'entry_original',
        'name' : imagename
        }
    print("Processing: "+ imagestring)

    response = requests.get(MEDIAURL+SLUG,params)
    content = response.content
    with open(imagestring, 'wb') as f:
        f.write(content)

#Scan through data and extract fields of interest
def getColIndicies(fields,NAMECOLS, IMGCOLS):
    nameIndicies = list()
    imgIndicies = list()
    fields = [x.strip(" ").rstrip("\n") for x in fields]
    for x in NAMECOLS:
        nameIndicies.append(fields.index(x))
    for x in IMGCOLS:
        imgIndicies.append(fields.index(x))
    return nameIndicies,imgIndicies

def main():
    FILENAME, NAMECOLS, IMGCOLS, SLUG, APPID, IMAGE_FOLDER = load_variables('data.json')
    NAMECOLS = [x for x in NAMECOLS.split(",") if x]
    IMGCOLS= [x for x in IMGCOLS.split(",") if x]
    print(FILENAME, NAMECOLS, IMGCOLS, SLUG, APPID, IMAGE_FOLDER )

    with open (FILENAME) as f:
        print("Opening " + FILENAME)
        data = [x for x in csv.reader(f, delimiter=',', quotechar='"')]
        headers = data[0]
        print(headers)

    nameIndicies,imgIndicies = getColIndicies(headers,NAMECOLS, IMGCOLS)

    #update to include user input cols instead of hardcoded
    for fields in data[1:]:    
        stringDataList = [fields[i].strip().rstrip("\n") for i in nameIndicies]
        nameString = "_".join(stringDataList)

        for img in imgIndicies:
            if (fields[img].split(".")[-1] == "jpg"):
                get_image(nameString + "_" + headers[img].strip().rstrip("\n") + "_" + fields[img],fields[img],APPID,SLUG,IMAGE_FOLDER)
            else:
                print("No " + headers[img].rstrip("\n") + " img for " + nameString + " given: " + fields[img])

main()