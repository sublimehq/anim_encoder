# Animation Encoder
## Overview
anim_encoder creates small JavaScript+HTML animations from a series on PNG images.
This is a modification of that original post, that adds some actual documentation
cleans up the code base a bit and attempts to make it slightly more reliable. So that
if anyone actually wants to use this is a project they can get up and running really
quickly.


Original details are at http://www.sublimetext.com/~jps/animated_gifs_the_hard_way.html

## Getting Started (Compiling the Example)
```
sudo apt-get install pngcrush python-opencv python-numpy python-scipy
python anim_encoder.py example
firefox example.html
```


## Capturing your own images
Images will be saved to capture, you simply need to run capture.py and then go about your task.
Note you can just delete frames you don't want as you initially set up, should save you some
time. Then to run the program just go

```
python capture.py
```

If you need to change any settings it should be pretty simple just jump over to config.py
and edit the configuration options.
