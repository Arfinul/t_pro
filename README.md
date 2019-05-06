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
![alt text](blob:https://web.whatsapp.com/778c9a87-7d53-46b7-8691-2b0ed3059086)

Suggested numbers of workers and queues size:

- Webcam stream: default values
- Video stream: 20 workers, 150 queue size (Maybe little hand tunning could be done)
