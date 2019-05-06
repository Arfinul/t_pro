# Flc

# To use it:
- White and Tea images reolution must be same.
```
Correct - white and leaf image resolution - 560 x 1109 pixels
Incorrect - White image is vertically captured and leaf image is horizontally captured.
            white image resolution - 560 x 1109 pixels
            tea image resolution - 1109 x 560 pixels
```
- Don't zoom white capturing the images
- Maintain distance between the bunches

![step0001](https://user-images.githubusercontent.com/29590484/57215245-ed507380-7009-11e9-83ae-ba1b302e559c.jpg)
![step0002](https://user-images.githubusercontent.com/29590484/57215250-f3465480-7009-11e9-86c2-055fd14682eb.jpg)
![step0003](https://user-images.githubusercontent.com/29590484/57215262-f80b0880-7009-11e9-9366-2d1ffedc3004.jpg)

Suggested numbers of workers and queues size:

- Webcam stream: default values
- Video stream: 20 workers, 150 queue size (Maybe little hand tunning could be done)
