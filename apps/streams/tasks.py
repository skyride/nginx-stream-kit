import ffmpeg
import os
import subprocess

from uuid import UUID, uuid4

from django.core.files.base import ContentFile

from streamkit.celery import app
from .models import (
    TranscodeProfile, Distribution, Segment,
    generate_segment_filename)


@app.task
def transcode_segment(segment_id: UUID, distribution_id: UUID) -> UUID:
    """
    Transcode the segment provided and add it to the distribution specified.
    """
    distribution: Distribution = Distribution.objects.get(pk=distribution_id)
    source_segment: Segment = Segment.objects.get(pk=segment_id)
    profile: TranscodeProfile = distribution.transcode_profile

    # Stop now if this distribution doesn't actually have a profile
    if profile is None:
        return None

    # Perform transcode
    out_filepath = f"/tmp/{uuid4()}.ts"
    cmd = (
        ffmpeg
        .input(source_segment.file.url)
        .filter("scale", profile.video_width, -1)
        .output(out_filepath,
            vcodec=profile.video_codec,
            video_bitrate=profile.video_bitrate,
            preset=profile.video_preset,
            acodec=profile.audio_codec,
            audio_bitrate=profile.audio_bitrate)
    )
    transcode_command = [
        "ffmpeg", "-copyts",
        "-i", source_segment.file.url,
        "-vf", f"scale={profile.video_width}:-1",
        "-vcodec", profile.video_codec, "-vb", str(profile.video_bitrate),
        "-acodec", profile.audio_codec, "-ab", str(profile.audio_bitrate),
        "-preset", profile.video_preset,
        out_filepath
    ]

    proc = subprocess.Popen(transcode_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout = proc.stdout.read().decode("utf-8")
    stderr = proc.stderr.read().decode("utf-8")

    # Create segment
    with open(out_filepath, "rb") as f:
        segment: Segment = Segment(
            distribution=distribution,
            sequence_number=source_segment.sequence_number,
            transcode_command=" ".join(transcode_command),
            transcode_stdout=stdout,
            transcode_stderr=stderr)
        segment.file.save(f"{uuid4()}.ts", f)

    print(f"Transcoded segment {source_segment.sequence_number} of "
          f"{distribution.id} at {profile.name}, locally deleting now")
    os.remove(out_filepath)