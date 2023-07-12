import cv2
import matplotlib.pyplot
import numpy
import scipy.signal

def get_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    while (frame := cap.read()[1]) is not None:
        yield frame


def is_high(x, low, high):
    # Check if x is closer to high than low
    return abs(x - low) > abs(x - high)


frame_brightness = [numpy.average(frame).astype(numpy.uint8) for frame in get_frames("video.mp4")]

brightness_count = dict(zip(*numpy.unique(frame_brightness, return_counts=True)))  # Count levels of brightness, as dict
brightness_count = [brightness_count.get(x, 0) for x in range(256)]  # 1D list of all brightness levels
dark, light = sorted(scipy.signal.find_peaks(brightness_count)[0])  # Lowest peak is the dark value, high is light. There should only be two peaks (if there is no bad noise)

light_frames = (lambda x: is_high(x, dark, light))(frame_brightness)  # List all light frames

light_frames = numpy.trim_zeros(numpy.trim_zeros(light_frames != True) != True)  # Trim light then trim darkness
light_frames += False  # Add trailing False to properly print last light

matplotlib.pyplot.plot(light_frames[:10*24])  # TODO: Remove this. Assume it's 24 fps and render first 10s.
matplotlib.pyplot.savefig("test.png")
matplotlib.pyplot.close()

# Find durations
# TODO: Make this less horrible

previous = light_frames[0]
duration = 0
duration_count = {True: {}, False: {}}
for is_light in light_frames:
    if is_light == previous:
        duration += 1
    else:
        duration_count[previous][duration] = duration_count[previous].get(duration, 0) + 1
        previous = is_light
        duration = 0

light_duration_count = [duration_count[True].get(x, 0) for x in range(0, max(duration_count[True].keys()))]
short_light, long_light = sorted(scipy.signal.find_peaks(light_duration_count)[0])

dark_duration_count = [duration_count[False].get(x, 0) for x in range(0, max(duration_count[False].keys()))]
short_dark, long_dark = sorted(scipy.signal.find_peaks(dark_duration_count)[0])

# Print morse
# TODO: Make this less horrible
# TODO: First and last morse code might be wrong. Should trim both sides to first long darkness?

previous = light_frames[0]
duration = 0
for is_light in light_frames:
    if is_light == previous:
        duration += 1
    else:
        if previous:
            # Light
            if is_high(duration, short_light, long_light):
                print(f"-", end="")
            else:
                print(f".", end="")
        else:
            # Dark
            if is_high(duration, short_dark, long_dark):
                print(f" ", end="")
            else:
                print(f"", end="")

        previous = is_light
        duration = 0

print()
