
import requests
import json
import csv
import os

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
    IMAGE_FOLDER = os.path.join(os.path.dirname(os.path.realpath('__file__')),IMAGE_FOLDER)
    EXTRA_INFO = data.get("EXTRA_INFO")
    CLIENTID = data.get("CLIENTID")
    CLIENTSECRET = data.get("CLIENTSECRET")

    if(APPID == ''):
        print("No App ID provided, assuming CLIENTID and CLIENTSECRET were provided or project has public status in Epicollect")
    return FILENAME, NAMECOLS, IMGCOLS, SLUG, APPID, IMAGE_FOLDER, EXTRA_INFO, CLIENTID, CLIENTSECRET
    


def get_image(imagestring, imagename,APPID,SLUG,IMAGE_FOLDER, CLIENTID, CLIENTSECRET):

    #Private 
    if not CLIENTID == "":

        #Get APPID with POST request
        if APPID == "":

            params = {
            'grant_type': 'client_credentials',
            'client_id': CLIENTID,
            'client_secret' : CLIENTSECRET,
            }

            response = requests.post('https://five.epicollect.net/api/oauth/token',params)
            if(response.status_code == 404):
                print("Unable to connect to private repo, check CLIENTID and CLIENTSECRET in data.json")
                os.exit(0)
            content = json.loads(response.content)

            APPID = content.get('access_token')

        params = {
        'type': 'photo',
        'format': 'entry_original',
        'name' : imagename,
        }

        headers = {
            'Authorization': f'Bearer {APPID}',
        }

        response = requests.get(MEDIAURL+SLUG,params=params,headers=headers)

    #Public
    else:
        params = {
        'type': 'photo',
        'format': 'entry_original',
        'name' : imagename
        }
        response = requests.get(MEDIAURL+SLUG,params)
        if(response.status_code == 404):
            print("Failed to retrieve file: " + imagename)
            return
    

    print("Processing: "+ imagestring)

    
    content = response.content
    
    with open(os.path.join(IMAGE_FOLDER,imagestring), 'wb') as f:
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
    FILENAME, NAMECOLS, IMGCOLS, SLUG, APPID, IMAGE_FOLDER, EXTRA_INFO, CLIENTID, CLIENTSECRET = load_variables('data.json')
    NAMECOLS = [x for x in NAMECOLS.split(",") if x]
    IMGCOLS= [x for x in IMGCOLS.split(",") if x]
    # print(FILENAME, NAMECOLS, IMGCOLS, SLUG, APPID, IMAGE_FOLDER, EXTRA_INFO )

    with open (FILENAME) as f:
        print("Opening " + FILENAME)
        data = [x for x in csv.reader(f, delimiter=',', quotechar='"')]
        headers = data[0]

    nameIndicies,imgIndicies = getColIndicies(headers,NAMECOLS, IMGCOLS)

    for fields in data[1:]:    
        stringDataList = [fields[i].strip().rstrip("\n") for i in nameIndicies] + [EXTRA_INFO]
        nameString = "_".join(stringDataList)

        for img in imgIndicies:
            if (fields[img].split(".")[-1] == "jpg"):
                get_image(nameString + "_" + headers[img].strip().rstrip("\n")+".jpg",fields[img],APPID,SLUG,IMAGE_FOLDER, CLIENTID, CLIENTSECRET)
            else:
                print("No " + headers[img].rstrip("\n") + " img for " + nameString + " given: " + fields[img])

main()