import fastai
import sys

from fastai.vision import *
import warnings
warnings.filterwarnings("ignore")


PATH  = '/home/agnext/Documents/tea_infer/'  #Location of .pkl file file

learn = load_learner(PATH,test=ImageList.from_folder('test'))

if __name__ =="__main__":
    
    file_name =sys.argv[1]
    img =open_image(file_name)
    pred_class,pred_idx,outputs =learn.predict(img)
    print("Prediction Class=",pred_class)
    print("Prediction Label=", pred_idx)
    print("Prediction Probability=",outputs)
    