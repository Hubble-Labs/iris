import os, time, datetime
import numpy as np
from bridge import Bridge

from PIL import Image
import hashlib
import json
import base64

from eolearn.core import EOWorkflow, FeatureType, LoadTask, OutputTask, SaveTask, linearly_connect_tasks
from eolearn.io import ExportToTiffTask, SentinelHubEvalscriptTask, SentinelHubInputTask
from sentinelhub import CRS, BBox, DataCollection, SHConfig

config = ""
cwd = os.getcwd()
export_folder = os.path.join(cwd, "data")

class ImageHashAdapter():
    def __init__(self, input):
        self.id = input.get('id', '1')
        self.request_data = input.get('data')

        self.config = SHConfig()
        self.aoi_bbox = BBox(bbox=[5.60, 52.68, 5.75, 52.63], crs=CRS.WGS84)
        self.time_interval = ("2018-04-01", "2018-05-01")
        self.maxcc = 0.8
        self.resolution = 10
        self.time_difference = datetime.timedelta(hours=2)
        
        if self.validate_request_data():
            self.bridge = Bridge()
            workflow = self.createWorkflow()
            self.request(workflow)
        else:
            self.result_error('No data provided')

    def validate_request_data(self):
        if self.request_data is None:
            return False
        if self.request_data == {}:
            return False
        return True

    def createWorkflow(self) -> EOWorkflow:
        # Get Sentinel-2 data
        l1c_task1 = SentinelHubInputTask(
                data_collection=DataCollection.SENTINEL2_L1C,
                bands=["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B10", "B11", "B12"],
                bands_feature=(FeatureType.DATA, "L1C_data"),
                additional_data=[(FeatureType.MASK, "dataMask")],
                resolution= self.resolution,
                maxcc=self.maxcc,
                time_difference = self.time_difference,
                config = self.config,
                max_threads=3,
            )
        # SAVE EOPATCH IN MEMORY
        output_task = OutputTask("eopatch")
        workflow_nodes = linearly_connect_tasks(l1c_task1, output_task)
        workflow = EOWorkflow(workflow_nodes)
        return workflow
            
    def request(self, workflow):
        h = ""
        try:
            workflow_nodes = workflow.get_nodes()
            # Allows you to pass special parameters into the nodes before execution
            result = workflow.execute(
                {
                    workflow_nodes[0]: {"bbox": self.aoi_bbox, "time_interval": self.time_interval},
                    #workflow_nodes[2]: {"filename": "img1.tiff"}
                    #workflow_nodes[-2]: {"eopatch_folder": "eopatch"},
                }
            )

            if result.workflow_failed():
                print("Error: Workflow failed")
                raise Exception("Workflow failed.")
            else:
                eopatch = result.outputs["eopatch"]
                data = eopatch.__getitem__((FeatureType.DATA, "L1C_data"))
                img = getImage(data, 2)
                band = getBand(img, 2)
                h = returnImageHash(band)

            response = {
                "hash": h
            }

            j = json.dumps(response)
            self.result = j
            self.result_success(j)

        except Exception as e:
            self.result_error(e)
        finally:
            self.bridge.close()

    def result_success(self, data):
        self.result = {
            'jobRunID': self.id,
            'data': data,
            'result': self.result,
            'statusCode': 200,
        }

    def result_error(self, error):
        self.result = {
            'jobRunID': self.id,
            'status': 'errored',
            'error': f'There was an error: {error}',
            'statusCode': 500,
        }
    

"""
Configures SentinelHub OAuth access and returns config object
"""
def SHSignIn():
    config = SHConfig()
    config.instance_id = '81f4ec4b-3952-4c9d-91bd-2e0536d86e9a'
    config.sh_client_id = '9b276c05-d06d-449e-8369-1b521fd97174'
    config.sh_client_secret = 'wX7cF<&K,euia!?nuDx!>F7,j,b{8k;5w/&edd1x'
    config.save()
    return config

"""
Function that takes in the result of an eopath which is an ndarray of shape:
    (time * height * width * band) and saves only the RGB bands as images.
"""

def saveRGBBands(data):
    band_name = ""
    for i in range(data.shape[0]):
        imgs = data[i, ...]
        for j in range(imgs.shape[-1]):
            if(j >= 2 & j <= 4):
                if(j == 2):
                    band_name= "blue"
                elif(j == 3):
                    band_name="green"
                else:
                    band_name="red"
                band = imgs[..., j]
                scaled_band = (band * 255 / np.max(band)).astype('uint8')
                im = Image.fromarray(scaled_band)
                folder_path = os.path.join(os.getcwd(), "data", "test1rgb", f"img{i}")
                file_path = os.path.join(folder_path, f"img{i}{band_name}.png")
                os.makedirs(folder_path, exist_ok=True)
                im.save(file_path)

"""
Function that takes in the result of an eopath which is an ndarray of shape:
    (time * height * width * band) and saves only the RGB bands as images.
"""
def saveBand(folder_path: str, band: Image) -> None:
    file_name = returnImageHash(band)
    file_path = os.path.join(folder_path, f"{file_name}.png")
    os.makedirs(folder_path, exist_ok=True)
    band.save(file_path)

"""
Function that takes in the result of an eopath which is an ndarray of shape:
    (time * height * width * band) and saves ALL bands as images
"""
def saveBands(data):
    band_name = ""
    for i in range(data.shape[0]):
        imgs = data[i, ...]
        for j in range(imgs.shape[-1]):
            band = imgs[..., j]
            scaled_band = (band * 255 / np.max(band)).astype('uint8')
            im = Image.fromarray(scaled_band)
            folder_path = os.path.join(os.getcwd(), "data", "test1rgb", f"img{i}")
            file_path = os.path.join(folder_path, f"img{i}band{j}.png")
            os.makedirs(folder_path, exist_ok=True)
            im.save(file_path)

def getImages(data, start, end):
    imgs = []
    print(type(imgs))
    for i in range(data.shape[0]):
        if(i >= start & i <= end):
            imgs.append(data[i, ...])
    return imgs

def getImages(data):
    imgs = []
    for i in range(data.shape[0]):
        imgs.append([i, ...])
    return imgs
    
def getImage(data, index) -> np.ndarray:
    for i in range(data.shape[0]):
        if (i == index):
            img = data[i, ...]
            return img

def getBands(img):
    band_imgs = []
    for i in range(img.shape[-1]):
        band = img[..., i]
        scaled_band =(band * 255 / np.max(band)).astype('uint8')
        band_img = Image.fromarray(scaled_band)
        band_imgs.append(band_img)
    return band_imgs

def getBand(img, index) -> Image:
    for i in range(img.shape[-1]):
        if (i == index):
            band = img[..., i]
            scaled_band = (band * 255 / np.max(band)).astype('uint8')
            band_img = Image.fromarray(scaled_band)
            return band_img

def returnBase64Hash(base64_msg: str) -> str:
    base64_str = base64_msg.encode('utf-8')
    t = str(time.time()).encode('utf-8')

    hasher = hashlib.sha1()
    hasher.update(base64_str)
    hasher.update(t)
    return hasher.hexdigest()

def returnImageHash(img: Image) -> str:
    img_str = imageToBase64String(img).encode('utf-8')
    t = str(time.time()).encode('utf-8')

    hasher = hashlib.sha1()
    hasher.update(img_str)
    hasher.update(t)
    return hasher.hexdigest()


"""
Takes in image path and returns base64 string
"""
def imagePathToBase64String(image_path: str):
    with open(image_path, 'rb') as binary_file:
        binary_file_data = binary_file.read()
        base64_bytes = base64.b64encode(binary_file_data)
        base64_message = base64_bytes.decode('utf-8')
    return base64_message

"""
Takes in image and returns base64 string
"""
def imageToBase64String(img: Image):
    img_bytes = img.tobytes()
    base64_bytes = base64.b64encode(img_bytes)
    base64_message = base64_bytes.decode('utf-8')
    return base64_message


"""
Takes in base64 string and returns image in bytes
"""
def base64StringToImage(base64_message):
    #str to ascii bytes
    base64_bytes = base64_message.encode('ascii')
    #ascii bytes to image bytes
    img_bytes = base64.b64decode(base64_bytes) 
    return img_bytes