import easyocr as ocr  #OCR
import streamlit as st  #Web App
from PIL import Image, ImageOps #Image Processing
import time
from unittest import result
import editdistance
from pythainlp.util import isthai
import numpy as np

st.title("Idcard detection (OCR) Webapp.")

#subtitle
st.markdown("Identification Card detector.")

st.markdown("")

#image uploader
image = st.file_uploader(label = "upload Idcard img here.. OwO",type=['png','jpg','jpeg'])


@st.cache
def load_model(): 
    reader = ocr.Reader(['en'],model_storage_directory='.')
    return reader 

reader = load_model() #load model

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

def Get_OCR(input_image):
  input_image = Image.open(input_image) #read image
  with st.spinner("🤖 AI is at Work! "):

      t1 = time.perf_counter()
      result = reader.readtext(np.array(input_image))

      result_text = [] #empty list for results


      for text in result:
          result_text.append(text[1])

      st.write(result_text)
      t2 = time.perf_counter()
      st.write('time taken to run: {:.2f} sec'.format(t2-t1))
  #st.success("Here you go!")


def Get_Idcard_detail(file_path):
  raw_data = []
  id_num = {"id_num" : "None"}
  name = file_path
  img = Image.open(name)
  img = ImageOps.exif_transpose(img) # fix image rotating

  width, height = img.size # get img_input size
  if (width == 1280) and (height == 1280):
    result = reader.readtext(np.array(img))
  else:
    #im = im.convert('L') #Convert to gray
    old_size = img.size  # old_size[0] is in (width, height) format
    ratio = float(1280)/max(old_size)
    new_size = tuple([int(x*ratio) for x in old_size])
    img = img.resize(new_size, Image.ANTIALIAS)
    new_im = Image.new("RGB", (1280, 1280))
    new_im.paste(img, ((1280-new_size[0])//2,
                        (1280-new_size[1])//2))
    
    result = reader.readtext(np.array(new_im))


  

  result_text = [] #empty list for results
  for text in result:
    result_text.append(text[1])


  raw_data = result_text  



  def get_english(raw_list): # Cut only english var
    eng_name = []
    thai_name = []

    for name in raw_list:
      if isthai(name) == True:
        thai_name.append(name)
      else:
        eng_name.append(name)

    return eng_name

  raw_data = get_english(raw_data)


  def Clear_syntax(raw_list):

    Clean_syntax = ["","#","{","}","=","/","@","#","$","—","|","%","-","(",")","¥", "[", "]", "‘",':',';']

    for k in range(len(Clean_syntax)):
      while (Clean_syntax[k] in raw_list): # remove single symbol
        raw_list.remove(Clean_syntax[k])

    for l in range(len(raw_list)): 
      raw_list[l] = raw_list[l].replace("!","l") #split ! --> l (Error OCR Check)
      raw_list[l] = raw_list[l].replace(",",".") #split ! --> l (Error OCR Check)
      raw_list[l] = raw_list[l].replace(" ","") #split " " out from str
      raw_list[l] = raw_list[l].lower() #Set all string to lowercase

    for m in range(len(raw_list)): #Clear symbol in str "Hi/'" --> "Hi"
      for n in range(len(Clean_syntax)):
          raw_list[m] = raw_list[m].replace(Clean_syntax[n],"") 
    return raw_list

  raw_data = Clear_syntax(raw_data)


  def get_idnum(raw_list):
    id_num = {"id_num" : "None"}
    # 1. normal check 
    for i in range(len(raw_list)): # check if len(list) = 1, 4, 5, 2, 1 (13 digit idcard) and all is int
      try:
        if ((len(raw_list[i]) == 1) and (len(raw_list[i+1]) == 4) and (len(raw_list[i+2]) == 5) and (len(raw_list[i+3]) == 2) and (len(raw_list[i+4]) == 1)) and ((raw_list[i] + raw_list[i+1] + raw_list[i+2] + raw_list[i+3] + raw_list[i+4]).isnumeric()):
          id_num["id_num"] = (raw_list[i] + raw_list[i+1] + raw_list[i+2] + raw_list[i+3] + raw_list[i+4])
          break 
      except:
        pass

    # 2. Hardcore Check
    if id_num["id_num"] == "None":
      id_count = 0
      index_first = 0
      index_end = 0
      for i in range(len(raw_list)):
        if id_count == 13:
          index_end = i-1 #ลบ 1 index เพราะ ครบ 13 รอบก่อนหน้านี้
          #print(f"index_first == {index_first} index_end == {index_end}")
          #print(f"id = {raw_list[index_first:index_end+1]}")
          id_num["id_num"] = ''.join(raw_list[index_first:index_end+1]) 
          break
        else:
          if raw_list[i].isnumeric() == True and index_first == 0:
            id_count += len(raw_list[i])
            index_first = i
          elif raw_list[i].isnumeric() == True and index_first != 0:
            id_count += len(raw_list[i])
          elif raw_list[i].isnumeric() == False:
            id_count = 0
            index_first = 0

    return id_num

  id_num = (get_idnum(raw_data))

      #Complete list name check
  def list_name_check(raw_list):
    sum_list = raw_list
    name_key = ['name', 'lastname']

    #1. name_key check
    if ("name" in sum_list) and ("lastname" in sum_list): # if name and lastname in list pass it!
      pass
    else:
      for i in range(len(name_key)):
        for j in range(len(sum_list)):
          if (editdistance.eval(name_key[i], sum_list[j]) <= 2 ): 
            sum_list[j] = name_key[i]

    gender_key = ["mr.", "mrs.", 'master', 'miss']
    #2 gender_key check
    count = 0 # check for break
    for i in range(len(gender_key)):
      for j in range(len(sum_list)):
        if (count == 0):
          try:
            if (sum_list[i] == "name") or (sum_list[i] == "lastname"): # skip "name" and "lastname"
              pass
            else:
              # mr, mrs sensitive case double check with len(gender_key) == len(keyword)
              if (gender_key[i] == "mr." or gender_key[i] == "mrs.") and (editdistance.eval(gender_key[i], sum_list[j]) <= 3 and (len(gender_key[i]) == len(sum_list[j]))): 
                sum_list[j] = gender_key[i]
                count+=1
                #print(1)
              elif (gender_key[i] == "master" or gender_key[i] == "miss") and (editdistance.eval(gender_key[i], sum_list[j]) <= 3 ) and (len(gender_key[i]) == len(sum_list[j])):
                sum_list[j] = gender_key[i]
                count+=1
                #print(1)
          except:
            if (gender_key[i] == "mr." or gender_key[i] == "mrs.") and (editdistance.eval(gender_key[i], sum_list[j]) <= 2 and (len(gender_key[i]) == len(sum_list[j]))): 
                sum_list[j] = gender_key[i]
                count+=1
                #print(1)
            elif (gender_key[i] == "master" or gender_key[i] == "miss") and (editdistance.eval(gender_key[i], sum_list[j]) <= 3 ) and (len(gender_key[i]) == len(sum_list[j])):
                sum_list[j] = gender_key[i]
                count+=1
                #print(1)
        else:
          break

    return sum_list

  raw_data = list_name_check(raw_data)

  #get_eng_name
  def get_engname(raw_list):
    get_data = raw_list
    engname_list = []

    name_pos = [] 
    lastname_pos = []
    mr_pos = []
    mrs_pos = []

      # check keyword by name, lastname, master, mr, miss, mrs
    for j in range(len(get_data)): #get "name" , "lastname" index
      if "name" == get_data[j]:
        name_pos.append(j)
      elif "lastname" == get_data[j]:
        lastname_pos.append(j)
      elif ("mr." == get_data[j]) or ("master" == get_data[j]):
        mr_pos.append(j)
      elif ("miss" == get_data[j]) or ("mrs." == get_data[j]):
        mrs_pos.append(j)


    if len(name_pos) != 0: #get_engname ex --> ['name', 'master', 'tanaanan', 'lastname', 'chalermpan']
      engname_list = get_data[name_pos[0]:name_pos[0]+6] # select first index กรณีมี "name" มากกว่า 1 ตัว
    elif len(lastname_pos) != 0:
      engname_list = get_data[lastname_pos[0]-3:lastname_pos[0]+3] 
    elif len(mr_pos) != 0:
      engname_list = get_data[mr_pos[0]-1:mr_pos[0]+5]
    elif len(mrs_pos) != 0:
      engname_list = get_data[mrs_pos[0]-1:mrs_pos[0]+5]
    else:
      print("Can't find eng name!!") 

    return engname_list

  raw_data = get_engname(raw_data)




  def split_genkey(raw_list): # remove stringname + gender_key ex. "missjate" -> "jate"
    data = raw_list
    key = ['mrs.','mr.','master','miss']
    name = "" #gen_key name
    name_pos = 0
    gen_index = 0
    gen_type = "" #male / female
    # check keyword
    for key_val in key:
        for each_text in data:
            if (each_text[:len(key_val)] == key_val) or (editdistance.eval(each_text[:len(key_val)],key_val) <= 1 and (len(each_text[:len(key_val)]) == len(key_val))):
                #each_text = each_text[len(key):]
                if (each_text == "name") or (each_text == "lastname"):
                  pass
                else:
                  name = (each_text[:len(key_val)])
                  name_pos = data.index(each_text) # get_index
                  gen_index = len(key_val)
                  break
    if (name_pos != 0): 
      data[name_pos] = data[name_pos][gen_index:] # split gender_key on list
      for empty_str in range(data.count('')): # clear "empty string"
        data.remove('')
    return data

  raw_data = split_genkey(raw_data)


  def clean_name_data(raw_list): # delete all single string and int string
    for k in range(len(raw_list)):
      try:
        while ((len(raw_list[k]) <= 2) or (raw_list[k].isnumeric() == True)): # remove single symbol
          raw_list.remove(raw_list[k])
      except IndexError:
        pass
    return raw_list

  raw_data = clean_name_data(raw_data)


  def name_sum(raw_list):
    info = {"name" : "None",
            "lastname" : "None"}
    key = ['mr.','mrs.', 'master', 'miss', 'mrs','mr']
    name_pos = 0
    lastname_pos = 0
    for key_val in key: # remove gender_key in string
      if key_val in raw_list:
        raw_list.remove(key_val)
    try:
      for i in range(len(raw_list)):
        if raw_list[i] == "name":
          info["name"] = raw_list[i+1]
          name_pos = i+1
        elif raw_list[i] == "lastname":
          info["lastname"] = raw_list[i+1]
          lastname_pos = i+1
    except:
      pass

    # กรณี หาอย่างใดอย่าหนึ่งเจอให้ลองข้ามไปดู 1 index name, "name_val", lastname , "lastname_val"
    if (info["name"] != "None") and (info["lastname"] == "None"):
      try:
        info["lastname"] = raw_list[name_pos+2]
      except:
        pass
    elif (info["lastname"] != "None") and (info["name"] == "None"):
      try:
        info["name"] = raw_list[lastname_pos-2]
      except:
        pass

    # remove . on "mr." and "mrs."
    info["name"] = info["name"].replace(".","")
    info["lastname"] = info["lastname"].replace(".","")


    return info

  st.success("Process Completed!.....")
  st.write(id_num)
  st.write(name_sum(raw_data))




if image is not None:

  new_img = img_resize(image, 1280)
  st.image(new_img)

  #Get_OCR(image)
  with st.spinner("🤖 AI is at Work! "):

    t1 = time.perf_counter()
    Get_Idcard_detail(image)
    t2 = time.perf_counter()
    st.write('time taken to run: {:.2f} sec'.format(t2-t1))



else:
  st.write("## Waiting for image..")
  st.image('spy-x-family-anya-heh-anime.jpg')

st.caption("Made by Tanaanan .M")
