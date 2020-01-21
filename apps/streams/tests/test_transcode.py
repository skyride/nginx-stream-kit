from django.test import TestCase

from ..models import TranscodeProfile


class MediaWorkerTranscodeTests(TestCase):
    """
    Tests transcode methods on the media worker.
    """
    video_path = "apps/streams/tests/videos/10sec.mp4"

    def setUp(self):
        from ..media import MediaWorker
        self.media_worker = MediaWorker()

    def test_x264_in_x264_out(self):
        # Prepare data
        profile = self._create_transcode_profile(video_codec="libx264")

        # Call method
        video_out_bytes, stderr = self.media_worker.transcode_segment(
            self.video_path,
            profile)

    def _create_transcode_profile(self, **kwargs) -> TranscodeProfile:
        kwargs = {
            **{
                "video_width": 1280,
                "video_codec": "libx264",
                "video_bitrate": 1600000,
                "video_preset": "ultrafast",
                "audio_codec": "libfdk_aac",
                "audio_bitrate": 48000},
            **kwargs}
        return TranscodeProfile(**kwargs)