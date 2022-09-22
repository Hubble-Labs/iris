import os, time, datetime, hashlib, json, base64
import numpy as np
from bridge import Bridge
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error
from PIL import Image
from eolearn.core import EOWorkflow, FeatureType, OutputTask, linearly_connect_tasks
from eolearn.io import SentinelHubInputTask
from sentinelhub import CRS, BBox, DataCollection, SHConfig
import boto3
from botocore.exceptions import ClientError
import cv2

from .image_utils import get_image_sets, get_band_cv2array, get_image_hash, save_img

cwd = os.getcwd()
export_folder = os.path.join(cwd, "data")
num_of_imgs = 0
avg_sc_folder_path = os.path.join(export_folder, "average_scenario")
avg_sc_name = "avg_sc"
avg_sc_path = os.path.join(avg_sc_folder_path, avg_sc_name)

class IrisAdapter():
    def __init__(self, input):
        # Bridge request variables
        self.id = input.get('id', '1')
        self.request_data = input.get('data')

        # SentinelHub request variables
        self.config = sh_signin()
        self.aoi_bbox = BBox(bbox=[5.60, 52.68, 5.75, 52.63], crs=CRS.WGS84)
        self.time_interval = ("2018-04-01", "2018-05-01")
        self.maxcc = 0.8
        self.resolution = 10
        self.time_difference = datetime.timedelta(hours=2)
        
        if self.validate_request_data():
            self.bridge = Bridge()
            workflow = self.create_workflow()
            self.request(workflow)
        else:
            self.result_error('No data provided')

    def validate_request_data(self):
        if self.request_data is None:
            return False
        if self.request_data == {}:
            return False
        return True

    def create_workflow(self) -> EOWorkflow:
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
        url = ""
        try:
            workflow_nodes = workflow.get_nodes()
            # Allows you to pass special parameters into the nodes before execution
            result = workflow.execute({
                    workflow_nodes[0]: {"bbox": self.aoi_bbox, "time_interval": self.time_interval}
            })

            if result.workflow_failed():
                print("Error: Workflow failed")
                raise Exception("Workflow failed.")
            else:
                eopatch = result.outputs["eopatch"]
                data = eopatch.__getitem__((FeatureType.DATA, "L1C_data"))

                h, url = get_payload(data)

                response = {
                    "hash": h,
                    "url": url
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

def sh_signin():
    """
    Configures SentinelHub OAuth access and returns config object
    """
    config = SHConfig()
    config.instance_id = '81f4ec4b-3952-4c9d-91bd-2e0536d86e9a'
    config.sh_client_id = '9b276c05-d06d-449e-8369-1b521fd97174'
    config.sh_client_secret = 'wX7cF<&K,euia!?nuDx!>F7,j,b{8k;5w/&edd1x'
    config.save()
    return config

def smallest_not_zero(arr: list):
    """
    Function that takes in an array of numbers and sends back the smallest value
    greater than zero.

    Input:
    - arr: Array of numbers

    Output:
    - second_min: Smallest number in array greater than 0.
    - idx: Index of smallest number in array greater than 0 in input array 'arr'.
    """
    second_min = max(arr)
    idx = 0
    for i in range(len(arr)):
        val = arr[i]
        if((val != 0) and (val < second_min)):
            second_min = val
            idx = i
    return second_min, idx

def calc_mse(imgs):
    """
    Calculates the MSE scores of all images in the list imgs with respect to each other.

    Input:
    - imgs: List of ndarrays representing images in the cv2 representation of size n.

    Output:
    - ssim_results: An n by n matrix where ssim_results[i][j] is the MSE score of imgs[i] and imgs[j].
    """
    mse_results = []
    for i in range(num_of_imgs):
        img_results = []
        img = imgs[i]

        for j in range(num_of_imgs):
            if (i != j):
                ms_err = mean_squared_error(img, imgs[j])
                img_results.append(ms_err)
            else: 
                img_results.append(0)
        mse_results.append(img_results)
    #print("made it out of calc_mse")
    return mse_results

def calc_ssim(imgs):
    """
    Calculates the SSIM scores of all images in the list imgs with respect to each other.

    Input:
    - imgs: List of ndarrays representing images in the cv2 representation of size n.

    Output:
    - ssim_results: n by n matrix where ssim_results[i][j] is the SSIM score of imgs[i] and imgs[j]
    """

    ssim_results = []
    bw_imgs = []
    # Converts images to cv2 gray representation.
    for i in range(num_of_imgs):
        img_cv2array = imgs[i]
        try: 
            img_temp = cv2.cvtColor(img_cv2array, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            print("Error in converting image to gray:", "\n", "Error: ", e)
        bw_imgs.append(img_temp)
    # Compares bw_imgs[i] to bw_imgs[j] and calculate SSIM.
    for i in range(num_of_imgs):
        img_results = []
        img = bw_imgs[i]
        for j in range(num_of_imgs):
            if (i != j):
                ssim_res = ssim(img, bw_imgs[j])
                img_results.append(ssim_res)
            else: 
                img_results.append(0)
        ssim_results.append(img_results)
    return ssim_results

def calc_avg_scenario(mse_results: list, ssim_results: list) -> int:
    """
    Takes in list of MSE scores and SSIM scores per image where the index in the list
    corresponds to an image with the same index in the image list passed to compute mse_results and 
    ssim_results.

    Input:
        - mse_results: List containing MSE values for each image pair combination.
        - ssim_results: List containing SSIM values for each image pair combination.

    Output:
        - idx: Index of image that is the average scenario based on MSE and SSIM results.
    """
    avg_scenario_results = [0] * num_of_imgs
    for i in range(num_of_imgs):
        mse_result = mse_results[i]
        ssim_result = ssim_results[i]

        mse_min, best_sme_idx = smallest_not_zero(mse_result)
        #print("ssim_result")
        ssim_max = max(ssim_result)
        
        best_ssim_idx = ssim_result.index(ssim_max)

        if(best_ssim_idx == best_sme_idx):
            avg_scenario_results[best_sme_idx] += 2
        else:
            avg_scenario_results[best_ssim_idx] += 1
            avg_scenario_results[best_sme_idx] += 1


    print("avg_sc_results")    
    idx = avg_scenario_results.index(max(avg_scenario_results))
    return idx

def get_payload(data):
    """
    Function that recieves SentinelHub eopatch FEATURE.DATA ndarray containing the images
    we want, gets the blue channel of all images recieved, calculates their ssim and mse
    scores, finds the Average Scenario, uploads it to our AWS S3 bucket, and returns its 
    hash and url where it is stored publically.

    Input:
    - data: numpy ndarray containing eopatch FEATURE.DATA containing the requested images

    Output:
    - h: Hash of the average scenario.
    - url: URL of average scenario.
    """

    # List containing all Band 2 images of images to be compared.
    global num_of_imgs
    # List of images as cv2 ndarray representation.
    imgs = []
    h = ""
    avg_scenario_idx = 0
    avg_scenario = ""
    url = ""

    img_sets = get_image_sets(data)
    for i in range(len(img_sets)):
        img_set = img_sets[i]
        # Gets the blue channel
        imgs.append(get_band_cv2array(img_set, 2))

    num_of_imgs = len(imgs)

    mse_results = calc_mse(imgs)
    ssim_results = calc_ssim(imgs)

    avg_scenario_idx = calc_avg_scenario(mse_results, ssim_results)
    avg_scenario = imgs[avg_scenario_idx]
    # avg_scenario in Image representation
    avg_scenario = Image.fromarray(avg_scenario)

    h = get_image_hash(avg_scenario)
    url = upload_image(avg_scenario, h)

    print(h, url)
    return h, url

def upload_image(im: Image, key: str) -> str:
    """
    Uploads provided Image 'im' to our S3 Bucket and returns publically available
    url of image.

    Input:
    - im: Image object to upload.
    - key: Name of the upload within the bucket.

    Output:
    - url: Publically available URL.
    """
    url = ""
    bucket_name = "iris-web3athon-demo"
    location = ""

    
    
    save_img(avg_sc_folder_path, im, avg_sc_name)
    
    s3 = boto3.client('s3')
    location = 'us-east-1'

    try:
        response = s3.upload_file(avg_sc_path + ".png", bucket_name, key)
    except ClientError as e:
        print("AWS Client Error:", e)
    except Exception as e:
        print("Unspecified error uploading file", e)

    try:
        url = str(f"https://s3-{location}.amazonaws.com/{bucket_name}/{key}")
    except Exception as e:
        print("Error getting URL", e)

    return url
    