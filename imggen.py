import asyncio
import requests
import os
from dotenv import load_dotenv

load_dotenv()
runpod_api = "Bearer {}".format(os.getenv('RUNPOD_KEY'))

async def generateImage(prompt, size=(512, 512), anime=False):
    # Set the API endpoint URL
    endpoint = ""
    if anime:
        endpoint = "https://api.runpod.ai/v1/sd-anything-v4/run"
    else:
        endpoint = "https://api.runpod.ai/v1/sd-openjourney/run"

    # Set the headers for the request
    headers = {
    "Content-Type": "application/json",
    "Authorization": runpod_api
    }

    # Define your inputs
    input_data = {
        "input": {
            "prompt": prompt,
            "width": size[0],
            "height": size[1],
            "num_inference_steps": 150,
        }
    }

    # Make the request
    response = requests.post(endpoint, json=input_data, headers=headers).json()
    print(response)
    
    status = ""
    output = {}
    while status not in ["COMPLETED", "FAILED"]:
        print("Waiting for image generation to complete...")
        print(response["id"])
        res = None
        if anime:
            res = requests.get('https://api.runpod.ai/v1/sd-anything-v4/status/{}'.format(response["id"]), headers=headers)
        else: 
            res = requests.get('https://api.runpod.ai/v1/sd-openjourney/status/{}'.format(response["id"]), headers=headers)
        if res.status_code != 200:
            print(res.status_code, res.content)
        else:
            output = res.json()
            print(output)
            status = output["status"]
        await asyncio.sleep(5)

    print(output)
    files = []
    for img in output['output']:
        img_data = requests.get(img['image']).content
        with open('img_{}.png'.format(img['seed']), 'wb') as handler:
            handler.write(img_data)
            files.append('img_{}.png'.format(img['seed']))
    
    return files