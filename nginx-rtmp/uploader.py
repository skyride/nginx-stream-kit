import glob
import time
import sys
import os
import requests

"""
This script is run under nginx-rtmp when a stream is live. It's job is to watch
for new .ts files appearing and upload them back to the main django application
where they can be processed and stored in our S3 backend.
"""

API_URL = "http://web:8000/api"
STREAM_KEY = sys.argv[1]
HLS_ROOT = "/hls"
HLS_DIRECTORY = f"{HLS_ROOT}/{STREAM_KEY}"


def get_stream():
    """
    Fetch stream and "source" distribution info
    """
    response = requests.get(f"{API_URL}/streams/",
        params={"status": "live", "key": STREAM_KEY})
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch stream with key {STREAM_KEY}, "
                        f"{response.status_code}")

    return response.json()['results'][0]


def get_distribution(stream_id):
    """
    Fetch "source" distribution using the stream id.
    """
    response = requests.get(f"{API_URL}/distributions/",
        params={"stream": stream_id, "name": "source"})

    if response.status_code != 200:
        raise Exception(f"Failed to fetch distribution with stream ID "
                        f"{stream_id}, {response.status_code}")

    return response.json()['results'][0]


def upload_segment(file_id):
    """
    Upload a file to our distribution.
    """
    file_path = f"{HLS_DIRECTORY}/{file_id}.ts"

    with open(file_path, "rb") as f:
        response = requests.post(f"{API_URL}/segments/",
            data={
                "distribution": distribution['id'],
                "sequence_number": file_id},
            files={"file": f})

        if response.status_code != 201:
            print(f"An error ocurred uploading segment ID {file_id}, "
                  f"{response.status_code}")
            return False
    
    os.remove(file_path)
    print(f"Uploaded segment ID {file_id} to {stream['id']}, "
          f"file deleted locally")
    return True

# Get objects
stream = get_stream()
distribution = get_distribution(stream['id'])

# State
uploaded_file_ids = set()
latest_file_id = 0

# Loop for new files
while True:
    # A file should be uploaded once the file after it is created so we can
    # ensure it's complete.
    files = glob.glob(f"{HLS_DIRECTORY}/*.ts")
    file_ids = [
        int(file.replace(".ts", "").replace(f"{HLS_DIRECTORY}/", ""))
        for file in files]
    latest_file_id = max(file_ids)

    for file_id in file_ids:
        if file_id < latest_file_id and file_id not in uploaded_file_ids:
            # Upload our file as a segment
            if upload_segment(file_id):
                uploaded_file_ids.add(file_id)

    # Sleep some time so we don't kill the machine
    time.sleep(0.2)