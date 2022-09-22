import numpy as np
import os, hashlib, time, base64
from PIL import Image

def save_rgb_bands(data):
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


def save_img(folder_path: str, img: Image) -> None:
    file_name = get_image_hash(img)
    file_path = os.path.join(folder_path, f"{file_name}.png")
    os.makedirs(folder_path, exist_ok=True)
    img.save(file_path)

def save_img(folder_path: str, img: Image, file_name: str) -> None:
    file_path = os.path.join(folder_path, f"{file_name}.png")
    os.makedirs(folder_path, exist_ok=True)
    img.save(file_path) 

"""
Function that takes in the result of an eopath which is an ndarray of shape:
    (time * height * width * band) and saves ALL bands as images
"""
def save_bands(data):
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

def get_image_sets(data, start, end):
    img_sets = []
    for i in range(data.shape[0]):
        if(i >= start & i <= end):
            img_sets.append(data[i, ...])
    return img_sets


# Returns list of images in SentinelHub representation: x * y
def get_image_sets(data):
    img_sets = []
    for i in range(data.shape[0]):
        img_sets.append(data[i, ...])
    return img_sets
    
def get_image_set(data: np.ndarray, index: int) -> np.ndarray:
    """
    Get the image set of SentinelHub FEATURE.DATA data at position 'index'.
    """
    for i in range(data.shape[0]):
        if (i == index):
            img = data[i, ...]
            return img

def get_bands(img: np.ndarray) -> list:
    band_imgs = []
    for i in range(img.shape[-1]):
        band = img[..., i]
        scaled_band = (band * 255 / np.max(band)).astype('uint8')
        band_img = Image.fromarray(scaled_band)
        band_imgs.append(band_img)
    return band_imgs

def get_band(img, index) -> Image:
    for i in range(img.shape[-1]):
        if (i == index):
            band = img[..., i]
            scaled_band = (band * 255 / np.max(band)).astype('uint8')
            band_img = Image.fromarray(scaled_band)
            return band_img

# Recieves image in SentinelHub representation and returns

def get_band_cv2array(img_set, index) -> np.ndarray:
    for i in range(img_set.shape[-1]):
        if (i == index):
            band_img = ""
            band = img_set[..., i]
            scaled_band = (band * 255 / np.max(band)).astype('uint8')
           
            band_img = Image.fromarray(scaled_band)
        
            rgb_band_img = band_img.convert('RGB')
            rgb_band_img_arr = np.asarray(rgb_band_img)
            
            return rgb_band_img_arr 

def get_base64_hash(base64_msg: str) -> str:
    base64_str = base64_msg.encode('utf-8')
    t = str(time.time()).encode('utf-8')

    hasher = hashlib.sha1()
    hasher.update(base64_str)
    hasher.update(t)
    return hasher.hexdigest()

def get_image_hash(img: Image) -> str:
    img_str = image_to_base64string(img).encode('utf-8')
    t = str(time.time()).encode('utf-8')

    hasher = hashlib.sha1()
    hasher.update(img_str)
    hasher.update(t)
    return hasher.hexdigest()

def imagepath_to_base64string(image_path: str) -> str:
    """
    Takes in image path and returns base64 string
    """
    with open(image_path, 'rb') as binary_file:
        binary_file_data = binary_file.read()
        base64_bytes = base64.b64encode(binary_file_data)
        base64_message = base64_bytes.decode('utf-8')
    return base64_message

def image_to_base64string(img: Image) -> str:
    """
    Takes in image and returns base64 string
    """
    img_bytes = img.tobytes()
    base64_bytes = base64.b64encode(img_bytes)
    base64_message = base64_bytes.decode('utf-8')
    return base64_message

def base64StringToImage(base64_message: str):
    """
    Takes in base64 string and returns image in bytes
    """
    #str to ascii bytes
    base64_bytes = base64_message.encode('ascii')
    #ascii bytes to image bytes
    img_bytes = base64.b64decode(base64_bytes) 
    return img_bytes