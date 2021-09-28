import fastai
from fastai.vision import *
from fastai.metrics import error_rate

bs = 64

PATH  = "/content/drive/My Drive/Colab Notebooks/Tea DL/data"


tfms = get_transforms()

data = ImageDataBunch.from_folder(PATH, valid_pct=.25,ds_tfms=tfms, size=224, bs=bs).normalize(imagenet_stats)

data.show_batch(rows=3, figsize=(7,6))

learn = cnn_learner(data, models.resnet18, metrics=accuracy)

learn.fit_one_cycle(10)

learn.unfreeze()

learn.fit_one_cycle(1)

learn.unfreeze()
learn.fit_one_cycle(10, max_lr=slice(1e-6,1e-5))

learn.export()