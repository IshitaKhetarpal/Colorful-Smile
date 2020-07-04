from io import BytesIO
from PIL import Image, ImageDraw,ImageFont
import requests
import json
import pprint
import operator

def LoadImage(imgPath):
    pil_img = Image.open(imgPath)
    stream = BytesIO()
    pil_img.save(stream, format='JPEG')
    bin_img = stream.getvalue()
    return bin_img

API_KEY = '91975ffbb09e47a7b859367068ffc454'
headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': API_KEY}    
headersStream = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': API_KEY}
baseEndpoint = "https://centralindia.api.cognitive.microsoft.com/face/v1.0"

personGroupName = "fam"
personNames = {'Ishita','Akshay'}

# Delete a person group
#ENDPOINT = baseEndpoint+"/persongroups/cloudgurus"
#requests.delete(url=ENDPOINT, headers=headers)

# 1 - Create a person group
ENDPOINT = baseEndpoint+"/persongroups/{0}".format(personGroupName)
createPersongroupResponse = requests.put(url=ENDPOINT, headers=headers,json=dict(name = personGroupName))
if createPersongroupResponse.status_code == 200:
    print("Face group created")
else:
    print("Error")
    pprint.pprint(createPersongroupResponse.json())

createPersonEndpoint = baseEndpoint + "/persongroups/{0}/persons".format(personGroupName)

for personName in personNames:
    createPersonResponse = requests.post(url=createPersonEndpoint, headers=headers,json=dict(name = personName))
    if createPersonResponse.status_code == 200:

        # 2 - Create a person in the persongroup
        personCreateResponse = createPersonResponse.json()
        personId = personCreateResponse['personId']
        print("Person created with Name: {0} ID: {1}".format(personName,personId))

        # 3 - Add a face(s) to the person
        addFaceToPersonEndpoint = baseEndpoint + "/persongroups/{0}/persons/{1}/persistedFaces".format(personGroupName,personId)

        binImg = LoadImage('Image/{0}.jpg'.format(personName))

        addFaceResponse = requests.post(data=binImg, url=addFaceToPersonEndpoint, headers=headersStream)
        if addFaceResponse.status_code == 200:
            addFaceResponseJson = addFaceResponse.json()
            persistedFaceId = addFaceResponseJson['persistedFaceId']
            print("- Face added to person {0} with ID: {1}".format(personName,persistedFaceId))
            
    else:
        print("Person creation failed")

        
# 4 - Train the group
ENDPOINT = baseEndpoint + "/persongroups/{0}/train".format(personGroupName)
trainPersonGroupResponse = requests.post(url=ENDPOINT, headers=headers)
if trainPersonGroupResponse.status_code == 202:
    print("Persongroup {0} trained".format(personGroupName))
else:
    print(trainPersonGroupResponse.json())