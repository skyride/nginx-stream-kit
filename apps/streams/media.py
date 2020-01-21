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
                          ) -> Tuple[bytes, str]:
        """
        Takes video file byte and a transcode profile, transcode the file,
        and returns the transcoded file in bytes, along with ffmpeg's stderr
        output.
        """
        out_filepath = f"/tmp/{uuid4()}.ts"
        transcode_command = [
            "ffmpeg", "-copyts",
            "-i", in_path,
            "-vf", f"scale={profile.video_width}:-1",
            "-vcodec", profile.video_codec, "-vb", str(profile.video_bitrate),
            "-acodec", profile.audio_codec, "-ab", str(profile.audio_bitrate),
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