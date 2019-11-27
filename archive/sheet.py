import pandas as pd
import os
import glob

df = pd.DataFrame()
# users = glob.glob("../splits/*")
users = ['../splitss1/104']

ids = []
section = []
dates = []
times = []
image_name = []

for i in users:
	images = glob.glob(i + "/*")
	for img in images:
		li = img.split("/")
		ids.append(li[2])
		section.append(li[3].split("_")[3])
		dates.append(li[3].split('_')[0])
		times.append(li[3].split("_")[1].split(".")[0])
		image_name.append(li[3].split("_")[-1])
df['Date'] = dates
df['Time'] = times
df['Image name'] = image_name
df['User ID'] = ids
df['Section'] = section


df.to_csv("images.csv", index=False)