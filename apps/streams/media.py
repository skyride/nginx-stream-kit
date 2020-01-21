import subprocess
import os

from typing import Tuple
from uuid import uuid4

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

        proc = subprocess.Popen(transcode_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stderr = proc.stderr.read().decode("utf-8")

        # Create segment
        with open(out_filepath, "rb") as f:
            file_out_bytes = f.read()
        os.remove(out_filepath)

        return file_out_bytes, stderr