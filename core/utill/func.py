import time
import numpy as np
import pyaudio
import sys

from clapDetector import ClapDetector, printDeviceInfo


def ClapDetection(
    inputDeviceIndex: int = 0,
    thresholdBias: int = 6000,
    lowcut: int = 1000,
    highcut: int = 5000,
    rate: int = 44100,
    chunk: int = 2048,
    verbose: bool = False
):
    """
    Run clap detection loop using external audio stream.

    Args:
        inputDeviceIndex (int): Microphone device index
        thresholdBias (int): Detection sensitivity
        lowcut (int): High-pass filter cutoff
        highcut (int): Low-pass filter cutoff
        rate (int): Sample rate
        chunk (int): Buffer size
    """
    if verbose :
        printDeviceInfo()
        print("\nStarting Clap Detection...\n")

    p = pyaudio.PyAudio()

    # auto pick working mic
    input_device_info = p.get_default_input_device_info()
    inputDeviceIndex = input_device_info['index']

    channels = int(input_device_info.get('maxInputChannels', 1))
    channels = max(1, min(channels, 1))  # force safe mono

    stream = p.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=rate,
        input=True,
        frames_per_buffer=chunk,
        input_device_index=inputDeviceIndex
    )

    clapDetector = ClapDetector(inputDevice=-1, logLevel=10)
    try:
        while True:
            audioData = np.frombuffer(stream.read(chunk), dtype=np.int16)

            result = clapDetector.run(
                thresholdBias=thresholdBias,
                lowcut=lowcut,
                highcut=highcut,
                audioData=audioData
            )

            if len(result) >= 2:
                if verbose :
                    print(f"Double clap detected! bias={thresholdBias}, lowcut={lowcut}, highcut={highcut}")
                break
            time.sleep(1 / 60)

    except KeyboardInterrupt:
        print("Exited gracefully")

    except Exception as e:
        print(f"error: {e}")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
