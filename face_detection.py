from io import BytesIO
from PIL import Image, ImageDraw,ImageFont
import requests
import json
import pprint
import operator

apiKey = '91975ffbb09e47a7b859367068ffc454'
baseUrl = "https://centralindia.api.cognitive.microsoft.com/face/v1.0"
ENDPOINT = "https://centralindia.api.cognitive.microsoft.com/face/v1.0/detect"

args = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'true',
    'returnFaceAttributes': 'age,gender,emotion'
}

headers = {'Content-Type': 'application/octet-stream', 'Ocp-Apim-Subscription-Key': apiKey}    

# Load image and convert to bytes
pil_img = Image.open('Image/hi.jpg')
stream = BytesIO()
pil_img.save(stream, format='JPEG') # convert PIL Image to Bytes
bin_img = stream.getvalue()

# Detect faces
detectEndpoint = baseUrl+"/detect"
detectResponse = requests.post(data=bin_img, url=detectEndpoint, headers=headers, params=args)
faces = detectResponse.json()

# Identify faces
jsonHeaders = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': apiKey}  
identifyEndpoint = baseUrl+"/identify"
requestData = dict(
    faceIds = [o['faceId'] for o in faces],
    personGroupId = "fam",
    maxNumOfCandidatesReturned = 1,
    confidenceThreshold = 0.5
)
identifyResponse = requests.post(url=identifyEndpoint, headers=jsonHeaders,json=requestData)
identifyResponseJson = identifyResponse.json()

def getRectangle(faceDictionary):
    rect = faceDictionary['faceRectangle']
    left = rect['left']
    top = rect['top']
    bottom = left + rect['height']
    right = top + rect['width']
    return ((left, top), (bottom, right))

def getEmotion(faceDictionary):
    emotions = faceDictionary['faceAttributes']['emotion']
    sorted_x = sorted(emotions.items(), key=operator.itemgetter(1),reverse=True)
    emotion = sorted_x[0]
    return emotion

draw = ImageDraw.Draw(pil_img)
font = ImageFont.truetype("arial.ttf", 40)
for face in faces:
    draw.rectangle(getRectangle(face), outline='red',width=3)
    
    textPosition = (face['faceRectangle']['left'],face['faceRectangle']['top'] + face['faceRectangle']['height'])
    feeling = getEmotion(face)
    age = face['faceAttributes']['age']
    gender = face['faceAttributes']['gender']

    # Match face to person
    personName = "unkown"
    person = next(d for d in identifyResponseJson if d['faceId'] == face['faceId']) 
    if person['candidates']:
        personId = person['candidates'][0]['personId']
        personDetailsEndpoint = baseUrl+"/persongroups/{0}/persons/{1}".format("fam",personId)
        personDetailsRequest =  requests.get(url=personDetailsEndpoint, headers=jsonHeaders)       
        personDetailsRequestJson = personDetailsRequest.json()
        personName = personDetailsRequestJson['name']

    draw.text(textPosition,"Age: {0}\nFeeling: {1}\nGender: {2}\nName: {3}".format(age,feeling,gender,personName),font=font,fill=(255,0,0,255))    

pil_img.show()    