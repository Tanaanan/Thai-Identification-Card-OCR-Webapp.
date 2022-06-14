import streamlit as st  #Web App
from PIL import Image, ImageOps #Image Processing
import time
from unittest import result
from pythainlp.util import isthai
import numpy as np
from icevision.all import *
from icevision.models import *
from distutils.version import LooseVersion, Version


st.title("ATK-OCR detection (AOC) Webapp.")

#subtitle
st.markdown("## Antigen test kit + Identification Card detector.")

st.markdown("")

#image uploader
image = st.file_uploader(label = "upload ATK + Idcard img here.. OwO",type=['png','jpg','jpeg'])



#set default size as 1280 x 1280
def img_resize(input_path,img_size): # padding
  desired_size = img_size
  im = Image.open(input_path)
  im = ImageOps.exif_transpose(im) # fix image rotating
  width, height = im.size # get img_input size
  if (width == 1280) and (height == 1280):
    new_im = im
  else:
    #im = im.convert('L') #Convert to gray
    old_size = im.size  # old_size[0] is in (width, height) format
    ratio = float(desired_size)/max(old_size)
    new_size = tuple([int(x*ratio) for x in old_size])
    im = im.resize(new_size, Image.ANTIALIAS)
    new_im = Image.new("RGB", (desired_size, desired_size))
    new_im.paste(im, ((desired_size-new_size[0])//2,
                        (desired_size-new_size[1])//2))

  return new_im


checkpoint_path = "./AOC_weight_97.4.pth"

checkpoint_and_model = model_from_checkpoint(checkpoint_path, 
    model_name='ross.efficientdet', 
    backbone_name='tf_d2',
    img_size=384, 
    is_coco=False)

model_type = checkpoint_and_model["model_type"]
backbone = checkpoint_and_model["backbone"]
class_map = checkpoint_and_model["class_map"]
img_size = checkpoint_and_model["img_size"]
#model_type, backbone, class_map, img_size

model = checkpoint_and_model["model"]

device=next(model.parameters()).device

img_size = checkpoint_and_model["img_size"]
valid_tfms = tfms.A.Adapter([*tfms.A.resize_and_pad(img_size), tfms.A.Normalize()])

def get_detection(img_path):
 
  #Get_Idcard_detail(file_path=img_path)
  img = PIL.Image.open(img_path)
  img = ImageOps.exif_transpose(img) # fix image rotating
  width, height = img.size # get img_input size
  if (width == 1280) and (height == 1280):
    new_im = img
  else:
    #im = im.convert('L') #Convert to gray
    old_size = img.size  # old_size[0] is in (width, height) format
    ratio = float(1280)/max(old_size)
    new_size = tuple([int(x*ratio) for x in old_size])
    img = img.resize(new_size, Image.ANTIALIAS)
    new_im = Image.new("RGB", (1280, 1280))
    new_im.paste(img, ((1280-new_size[0])//2,
                        (1280-new_size[1])//2))


    pred_dict  = model_type.end2end_detect(new_im, valid_tfms, model, class_map=class_map, detection_threshold=0.6)
    #st.write(new_im.size)

  

  try:
    labels, acc = pred_dict['detection']['labels'][0], pred_dict['detection']['scores'][0]
    acc = acc * 100
    if labels == "Neg":
      labels = "Negative"
    elif labels == "Pos":
      labels = "Positive"
    st.success(f"Result : {labels} with accuracy {round(acc, 2)} %.")
  except IndexError:
    st.error("Not found ATK image! ; try to take a pic again..")
    labels = "None"
    acc = 0

def get_img_detection(img_path):
   
  #Get_Idcard_detail(file_path=img_path)
  img = PIL.Image.open(img_path)
  img = ImageOps.exif_transpose(img) # fix image rotating
  width, height = img.size # get img_input size
  if (width == 1280) and (height == 1280):
    new_im = img
  else:
    #im = im.convert('L') #Convert to gray
    old_size = img.size  # old_size[0] is in (width, height) format
    ratio = float(1280)/max(old_size)
    new_size = tuple([int(x*ratio) for x in old_size])
    img = img.resize(new_size, Image.ANTIALIAS)
    new_im = Image.new("RGB", (1280, 1280))
    new_im.paste(img, ((1280-new_size[0])//2,
                        (1280-new_size[1])//2))
  
  pred_dict  = model_type.end2end_detect(new_im, valid_tfms, model, class_map=class_map, detection_threshold=0.6)


  return pred_dict['img']

if image is not None:

  new_img = img_resize(image, 1280)
  #st.image(new_img)
  st.image(get_img_detection(image))

  #Get_OCR(image)
  with st.spinner("🤖 Working... "):
      
    t1 = time.perf_counter()
    get_detection(image)
    t2 = time.perf_counter()
    st.write('time taken to run: {:.2f} sec'.format(t2-t1))


  
else:
  st.write("## Waiting for image..")
  st.image('spy-x-family-anya-heh-anime.jpg')

st.caption("Made by Tanaanan .M")