import subprocess
import os
import re

from typing import Tuple
from uuid import uuid4

from .exceptions import TranscodeError
from .models import TranscodeProfile


class MediaWorker(object):
    """
    This media worker runs tasks using ffmpeg against media resources.
    """
    def transcode_segment(self,
                          in_path: str,
                          profile: TranscodeProfile
                          ) -> Tuple[bytes, str, str]:
        """
        Takes video file path and a transcode profile, transcode the file,
        and returns the transcoded file in bytes, along with ffmpeg's stderr
        output.
        """
        out_filepath = f"/tmp/{uuid4()}.ts"
        transcode_command = [
            "ffmpeg",
            "-i", in_path,
            "-vf", f"scale={profile.video_width}:-1",
            *profile.get_video_transcode_parameters(),
            "-bsf:v", "h264_mp4toannexb",
            *profile.get_audio_transcode_parameters(),
            "-copyts", "-muxdelay", "0",
            "-preset", profile.video_preset,
            out_filepath
        ]

        process = subprocess.Popen(transcode_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        process.wait()
        stderr = process.stderr.read().decode("utf-8")

        # Read new file back in and delete
        try:
            with open(out_filepath, "rb") as f:
                file_out_bytes = f.read()
            os.remove(out_filepath)
        except FileNotFoundError:
            raise TranscodeError("FFmpeg returned a non-zero code.\n" + stderr)

        return file_out_bytes, stderr, transcode_command

    def generate_still_from_video(self,
                                    in_path: str
                                    ) -> Tuple[bytes, float, str]:
        """
        Takes a video file path and generates a png image of the first
        frame along with the stderr output.
        """
        out_filepath = f"/tmp/{uuid4()}.jpg"
        command = [
            "ffmpeg",
            "-i", in_path,
            "-vframes", "1",
            out_filepath
        ]

        process = subprocess.Popen(command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        process.wait()
        stderr = process.stderr.read().decode("utf-8")

        # Parse start timecode
        timecode = self.parse_start_timecode_from_stderr(stderr)

        # Read new file back in and delete
        try:
            with open(out_filepath, "rb") as f:
                file_out_bytes = f.read()
            os.remove(out_filepath)
        except FileNotFoundError:
            raise TranscodeError("FFmpeg returned a non-zero code.\n" + stderr)

        return file_out_bytes, timecode, stderr

    def parse_start_timecode_from_stderr(self, stderr: str) -> float:
        """
        Get start from an stderr dump.
        """
        pattern = "start: ([0-9]+\.[0-9]+)"
        pattern = re.compile(pattern)
        result = pattern.search(stderr)
        if result is None:
            return None

        # Parse result
        timecode = float(result.group(1))
        return timecode

    def parse_duration_from_stderr(self, stderr: str) -> float:
        """
        Get duration from an ffmpeg stderr dump.
        """
        pattern = "Duration: (\\d\\d):(\\d\\d):(\\d\\d\\.\\d\\d)"
        pattern = re.compile(pattern)
        result = pattern.search(stderr)
        if result is None:
            return None
        
        # Parse result
        hours = float(result.group(1))
        minutes = float(result.group(2))
        seconds = float(result.group(3))

        duration = (
            (hours * 60 * 60) +
            (minutes * 60) +
            seconds)
        return duration

    def get_stderr_output(self, path: str) -> str:
        process = subprocess.Popen(["ffmpeg", "-i", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        process.wait()
        return process.stderr.read().decode("utf-8")