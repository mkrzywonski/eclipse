## Eclipse video capture script for Seestar S50

I created this python script to automate the capture of video on eclipse day (April 8, 2024). Clips will be created for the partial phases and compressed to approximately 1 minute timelapses. Another clip will be generated for totality. A final MP4 video file will be created that includes a 1 minute timelapse of the first partial phase, followed by all of totality in real time, followed by a timelapse of the second partial phase.

## Installation:

This script requires Python 3, ImageMagick, and FFmpeg. Make sure you have those installed. I am running this script under Linux. I make no guarantees that it will run on your system.

Edit the script and set the times for first contact through fourth contact (C1, C2, C3, and C4) in the variables/constants section near the top.  A great resource for discovering the timing for the eclipse at your location is: [http://xjubier.free.fr/en/site_pages/solar_eclipses](http://xjubier.free.fr/en/site_pages/solar_eclipses/TSE_2024_GoogleMapFull.html)

If you want to generate an eclipse sequence with still images from different points during the eclipse, edit the times in the "snapshots" list. I got times for my location using the Solar Eclipse Timer app. <https://www.solareclipsetimer.com/>

## Usage:

You will need to configure your Seestar to connect to your WiFi network so your PC can communicate with it. 

Set up your Seestar S50 and put it in solar observing mode. Don't forget to install the included solar filter on the front. Once you get the sun centered in the field of view on the app, you can close the app and put down your phone.

Note: On eclipse day, you may run the battery on your Seestar completely flat. Make sure you have a USB power source if you don't want the scope to cut off during the eclipse. Also check the "auto-shutoff" settings in the app.

Run the script

```
python3 video.py
```

The script will attempt to ping your Seestar at the address, "seestar.local". If the Seestar does not respond, the script will teminate. You can provide the IP address of the Seestar on your WiFi network using:

```
python3 video.py --ip=192.168.1.xxx
```

If the Seestar is online and responding to pings, the script will wait until 5 minutes before first contact.

```
Solar Eclipse Video Generation Script
Trying to ping camera: 127.0.0.1

Waiting to start capture in 3:00:29.....................
```

If you want to practice capturing video without waiting for eclipse time, use the --skip_wait flag.

```
python3 video.py --skip_wait
```

The script will proceed as if the eclipse is starting now. It will capture video for the entire eclipse duration (between 2 - 3 hours) and save the video as "full-xxxxxx.mp4". It will then generate clips for the first partial phase, totality, and the second partial phase: p1-xxxxxx.mp4, totality-xxxxxx.mp4, and p2-xxxxxx.mp4. Then it will generate timelapse videos from the two partial phase clips: tl1-xxxxxx.mp4 and tl2-xxxxxx.mp4. Finally, it will concatenate the timelapses and the totality clip into the final video: eclipse-xxxxxx.mp4.

All the files created will include the PID of the process running the script. This allows you to open multiple terminal windows and run multiple instances on the same PC.

If you are modifying the code to suit your own purpose, you may not want to wait 3 hours to capture video every time you test a change. You can supply a previously recorded video as follows:

```
python3 video.py --skip_wait --skip_capture --src=mysamplevideo.mp4
```

If you want to crop the Seestar's portrait sized video to a square, use the --crop flag. If you want to add timestamps at the bottom of the video, use the --timestamp flag.

```
python3 video.py --crop --timestamp
```

If you want to generate a eclipse sequence image with snapshots from the partial phases, use the --snapshot flag. This requires ImageMagik.

```
python3 video.py --crop --snapshot
```

The eclipse sequence montage will be named: "eclipse-xxxxxx.jpg"

## Non-Seestar Cameras

You can use this script to capture video during the eclipse from any camera that provides a RTSP stream. I plan to capture video from a security camera overlooking my observing location as well as from the Seestar on eclipse day. I will overlay the solar image in one corner on top of the video showing all of us observing the eclipse.

Terminal Window #1:

```
python3 video.py --crop --snapshot sun.mp4
```

Terminal Window #2:

```
python3 video.py --url=rtsp://user:password@my_camera_ip:554 people.mp4
```

After both videos have been captured, use ffmpeg to place the sun, picture-in-picture style, in the upper right corner of the people.mp4 video:

```
ffmpeg -i sun.mp4 -i people.mp4 -filter_complex "[0]scale=iw/3:ih/3 [pip]; [1][pip] overlay=main_w-overlay_w-10:10" -profile:v main -level 3.1 -b:v 440k -ar 44100 -ab 128k -s 1920x1080 -vcodec h264 -acodec libfaac combined.mp4
```

## To Do:

- Figure out how to include audio from non-seestar cameras during totality. Not sure how best to handle the timelapse segments with respect to audio.
- The solar image jiggles a bit due to the alt-az tracking of the Seestar. This is very visible during the timelapse segments. I'm sure there is astrophotography software that could align the frames to get rid of this motion. I haven't spent any time trying to fix this yet. Not sure if I will.
