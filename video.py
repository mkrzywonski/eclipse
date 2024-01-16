#!/usr/bin/env python3
import argparse
import datetime
import time
import os
import subprocess
from urllib.parse import urlparse

# Define global variables and constants
camera_ip = "seestar.local"
ffmpeg = "ffmpeg -y"
loglevel = "quiet"
c1 =  datetime.datetime.fromisoformat("2024-04-08T12:16:50")
c2 = datetime.datetime.fromisoformat("2024-04-08T13:34:18")
c3 =  datetime.datetime.fromisoformat("2024-04-08T13:38:08")
c4 = datetime.datetime.fromisoformat("2024-04-08T14:57:04")
margin = datetime.timedelta(minutes=5)      # Start recording 5 minutes before C1
t_margin = datetime.timedelta(seconds=5)    # End partial timelapse 5 seconds befor C2
duration = c4 - c1
duration_pre = c2 - c1 - t_margin
duration_totality = c3 - c2 + (t_margin * 2)
duration_post = c4 - c3 - t_margin
go_time = c1.replace(year=datetime.datetime.today().year,
    month=datetime.datetime.today().month,
    day=datetime.datetime.today().day) - margin
pid = os.getpid()
snapshots = [
        datetime.datetime.fromisoformat("2024-04-08T12:16:50"), # First Contact
        datetime.datetime.fromisoformat("2024-04-08T12:18:50"), # PP Image 1
        datetime.datetime.fromisoformat("2024-04-08T12:26:59"), # PP Image 2
        datetime.datetime.fromisoformat("2024-04-08T12:35:09"), # PP Image 3
        datetime.datetime.fromisoformat("2024-04-08T12:43:19"), # PP Image 4
        datetime.datetime.fromisoformat("2024-04-08T12:51:29"), # PP Image 5
        datetime.datetime.fromisoformat("2024-04-08T12:59:38"), # PP Image 6
        datetime.datetime.fromisoformat("2024-04-08T13:07:48"), # PP Image 7
        datetime.datetime.fromisoformat("2024-04-08T13:15:58"), # PP Image 8
        datetime.datetime.fromisoformat("2024-04-08T13:24:08"), # PP Image 9
        datetime.datetime.fromisoformat("2024-04-08T13:32:18"), # PP Image 10
        datetime.datetime.fromisoformat("2024-04-08T13:34:18"), # Second Contact
        datetime.datetime.fromisoformat("2024-04-08T13:36:13"), # Max Eclipse
        datetime.datetime.fromisoformat("2024-04-08T13:38:08"), # Third Contact
        datetime.datetime.fromisoformat("2024-04-08T13:40:08"), # PP Image 11
        datetime.datetime.fromisoformat("2024-04-08T13:48:27"), # PP Image 12
        datetime.datetime.fromisoformat("2024-04-08T13:56:47"), # PP Image 13
        datetime.datetime.fromisoformat("2024-04-08T14:05:06"), # PP Image 14
        datetime.datetime.fromisoformat("2024-04-08T14:13:26"), # PP Image 15
        datetime.datetime.fromisoformat("2024-04-08T14:21:45"), # PP Image 16
        datetime.datetime.fromisoformat("2024-04-08T14:30:05"), # PP Image 17
        datetime.datetime.fromisoformat("2024-04-08T14:38:24"), # PP Image 18
        datetime.datetime.fromisoformat("2024-04-08T14:46:44"), # PP Image 19
        datetime.datetime.fromisoformat("2024-04-08T14:55:04"), # PP Image 20
        datetime.datetime.fromisoformat("2024-04-08T14:57:04"), # Fourth Contact
        ]

# Parse command line arguments
parser = argparse.ArgumentParser(description="Solar Eclipse Video Processing Script")
parser.add_argument("--crop", action="store_true", help="Crop video from portrait to square")
parser.add_argument("--ip", default=camera_ip, help="Camera IP address")
parser.add_argument("--skip_capture", action="store_true", help="Skip video capture")
parser.add_argument("--skip_wait", action="store_true", help="Don't wait, start recording immediately")
parser.add_argument("--snapshot", action="store_true", help="Generate partial phase snapshots")
parser.add_argument("--src", default="sun.mp4.bak", help="Source file. Used with --skip_capture")
parser.add_argument("--tcp", action="store_true", help="Use TCP for RTSP stream")
parser.add_argument("--timestamp", action="store_true", help="Add timestamps to video")
parser.add_argument("--url", help="Camera URL")
parser.add_argument("filename", nargs='?', default=f"eclipse-{pid}.mp4", help="Output filename")
args = parser.parse_args()

class ConsoleColor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def wait_for_eclipse_start():
    wait = True
    now = datetime.datetime.today()
    remaining = go_time - now
    print(f"\n{ConsoleColor.HEADER}Waiting to start capture in {str(remaining)[0:7]}{ConsoleColor.ENDC}", end='', flush=True)
    while wait:
        now = datetime.datetime.today()
        remaining = go_time - now
        if now < go_time:
            if (remaining.seconds % 60 == 0):
                print(f"\n{ConsoleColor.HEADER}Waiting to start capture in {str(remaining)[0:7]}{ConsoleColor.ENDC}", end='', flush=True)
            else:
                print(f"{ConsoleColor.HEADER}.{ConsoleColor.ENDC}", end='', flush=True)

            time.sleep(remaining.microseconds / 1000000)
        else:
            wait = False

def check_camera():
    # Check if camera is reachable
    if args.url:
        ip = urlparse(args.url).hostname
    else:
        ip = args.ip

    print(f"{ConsoleColor.HEADER}Trying to ping camera: {ip}{ConsoleColor.ENDC}")
    try:
        subprocess.check_output(["ping", "-c", "1", ip])
    except subprocess.CalledProcessError:
        # Camera is not reachable, set skip_capture to True
        print(f"{ConsoleColor.HEADER}Camera at IP address {args.ip} is not reachable. Skipping video capture.{ConsoleColor.ENDC}")
        exit()

def capture_video():
    print(f'\n{ConsoleColor.HEADER}Capturing Video from camera{ConsoleColor.ENDC}')
    video_file = f"full-{pid}.mp4"
    seestar_url = f'rtsp://{args.ip}:4554/stream'
    length = margin + duration + margin

    # Use TCP for RTSP stream
    if args.tcp:
        tcp = '-rtsp_transport tcp'
    else:
        tcp = ''

    # Get camera URL from command line, or use Seestar URL as default
    if args.url:
        url = args.url
    else:
        url = seestar_url

    if args.skip_capture:
        cmd = f'cp {args.src} {video_file}'
    else:
        cmd = f'{ffmpeg} {tcp} -loglevel {loglevel} -stats -i {url} -t {length} -c:v copy -c:a copy {video_file}'

    print(f"{ConsoleColor.HEADER}Running command: {cmd}{ConsoleColor.ENDC}")
    result = os.system(cmd)
    if result > 0:
        print(f"{ConsoleColor.HEADER}Unable to capture. Is the Camera online?{ConsoleColor.ENDC}")
        exit()
    return(video_file)

def modify_video(input_file):
    if not (args.crop or args.timestamp):
        return(input_file)

    print(f'\n{ConsoleColor.HEADER}Cropping/Timestamping Video{ConsoleColor.ENDC}')
    output_file = f"cropped-{pid}.mp4"
    crop = None
    timestamp = None
    if args.crop:
        crop = 'crop=1080:1080'
    if args.timestamp:
        timestamp = f'drawtext=expansion=strftime:basetime=$(date +%s -d\'{go_time}\')000000:text=\'%Y/%m/%d %H\\:%M\\:%S\':r=12:x=(w-tw)/2:y=h-(2*lh):fontcolor=white:fontsize=42'
    filter = ', '.join(s for s in [crop, timestamp] if s is not None)
    cmd = f'{ffmpeg} -loglevel {loglevel} -stats -i {input_file} -vf "{filter}" {output_file}'
    print(f"{ConsoleColor.HEADER}Running command: {cmd}{ConsoleColor.ENDC}")
    result = os.system(cmd)
    if result > 0:
        print(f"{ConsoleColor.FAIL}Crop/Timestamp failed{ConsoleColor.ENDC}")
        exit()
    return(output_file)

def generate_clip(input_file, output_file, start, duration):
    print(f'\n{ConsoleColor.HEADER}Generating video clip {output_file}{ConsoleColor.ENDC}')
    cmd = f'{ffmpeg} -loglevel {loglevel} -stats -ss {start} -i {input_file} -t {duration} -c:v copy -c:a copy {output_file}'
    print(f"{ConsoleColor.HEADER}Running command: {cmd}{ConsoleColor.ENDC}")
    result = os.system(cmd)
    if result > 0:
        print(f"{ConsoleColor.FAIL}Clip generation failed{ConsoleColor.ENDC}")
        exit()

def generate_timelapse(input_file, output_file, rate):
    print(f"\n{ConsoleColor.HEADER}Generating timelapse of partial phase{ConsoleColor.ENDC}")
    #cmd = f'{ffmpeg} -loglevel {loglevel} -stats -i {input_file} -vf framestep={framestep},setpts=N/30/TB -r 30 {output_file}'
    cmd = f'{ffmpeg} -loglevel {loglevel} -stats -i {input_file} -vf "setpts={rate}*PTS" -an {output_file}'
    print(f"{ConsoleColor.HEADER}Running command: {cmd}{ConsoleColor.ENDC}")
    result = os.system(cmd)
    if result > 0:
        print(f"{ConsoleColor.FAIL}Timelapse generation failed{ConsoleColor.ENDC}")
        exit()

def generate_eclipse_video(timelapse1_file, totality_file, timelapse2_file, output_file):
    print(f"\n{ConsoleColor.HEADER}Generating eclipse video{ConsoleColor.ENDC}")
    cmd = f'{ffmpeg} -loglevel {loglevel} -stats -i {timelapse1_file} -i {totality_file} -i {timelapse2_file} -filter_complex "[0:v] [1:v] [2:v] concat=n=3:v=1:a=0 [vv]" -map "[vv]" {output_file}'
    print(f"{ConsoleColor.HEADER}Running command: {cmd}{ConsoleColor.ENDC}")
    result = os.system(cmd)
    if result > 0:
        print(f"{ConsoleColor.FAIL}Timelapse generation failed{ConsoleColor.ENDC}")
        exit()

def generate_snapshots(input_file, directory):
    print(f"\n{ConsoleColor.HEADER}Generating partial phase snapshots{ConsoleColor.ENDC}")
    count = 1
    for s in snapshots:
        snapshot_time = s.replace(year=datetime.datetime.today().year,
            month=datetime.datetime.today().month,
            day=datetime.datetime.today().day)
        offset = snapshot_time - go_time
        cmd = f'{ffmpeg} -loglevel {loglevel} -ss {offset} -i {input_file} -frames:v 1 -q:v 2 {directory}/snapshot-{count:02d}.jpg'
        print(f"{ConsoleColor.HEADER}Running command: {cmd}{ConsoleColor.ENDC}")
        result = os.system(cmd)
        if result > 0:
            print(f"{ConsoleColor.FAIL}Timelapse generation failed{ConsoleColor.ENDC}")
            exit()
        count += 1
    cmd = f'montage {directory}/*.jpg -tile 5x5 -geometry +0+0 eclipse.jpg'
    print(f"{ConsoleColor.HEADER}Running command: {cmd}{ConsoleColor.ENDC}")
    result = os.system(cmd)
    if result > 0:
        print(f"{ConsoleColor.FAIL}Timelapse generation failed{ConsoleColor.ENDC}")
        exit()

def main():

    print(f"\n{ConsoleColor.HEADER}Solar Eclipse Video Generation Script{ConsoleColor.ENDC}")

    # Ping camera to make sure it is online
    if not args.skip_capture:
        check_camera()

    # Wait until eclipse is about to begin before capturing video
    if not args.skip_wait:
        wait_for_eclipse_start()

    # Capture video for entire eclipse
    # This will be the master file. Timelapse clips
    # will be generated from this file.
    capture_file = capture_video()

    # Get a timestamp so we can calculate elapsed 
    # video processing time
    timer_start = datetime.datetime.now()
    
    # Add timestamps and crop from portrait to square
    # format if desired.
    # This could be done live during the capture above, but
    # it is CPU intensive and could cause dropped frames.
    # Better to make the initial capture lightweight 
    # and let the CPU take as long as necessary after
    # the capture is complete.
    file = modify_video(capture_file)

    # Generate clip for first partial phase
    start_offset = margin
    generate_clip(file, f"p1-{pid}.mp4", start_offset, duration_pre)

    # Generate clip for second partial phase
    start_offset = margin + duration_pre + duration_totality
    generate_clip(file, f"p2-{pid}.mp4", start_offset, duration_post)

    # Generate clip for totality
    start_offset = margin + duration_pre
    generate_clip(file, f"totality-{pid}.mp4", start_offset, duration_totality)

    # Generate timelapse for first partial phase
    rate = 60/duration_pre.seconds
    generate_timelapse(f"p1-{pid}.mp4", f"tl1-{pid}.mp4", rate)

    # Generate timelapse for second partial phase
    rate = 60/duration_pre.seconds
    generate_timelapse(f"p2-{pid}.mp4", f"tl2-{pid}.mp4", rate)

    # Generate eclipse video
    generate_eclipse_video(f"tl1-{pid}.mp4", f"totality-{pid}.mp4", f"tl2-{pid}.mp4", f"{args.filename}")

    # Generate Partial Phase Snapshots
    if args.snapshot:
        generate_snapshots(file, "snapshots")

    # Show how much time we took processing the video files
    timer_end = datetime.datetime.now()
    elapsed = timer_end - timer_start
    print(f'{ConsoleColor.HEADER}Processing time: {elapsed}{ConsoleColor.ENDC}')

if __name__ == "__main__":
    main()

