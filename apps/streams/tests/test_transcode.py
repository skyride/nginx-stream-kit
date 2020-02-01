from uuid import uuid4

from django.test import TestCase

from ..models import TranscodeProfile


class MediaWorkerTranscodeTests(TestCase):
    """
    Tests transcode methods on the media worker.
    """
    video_path = "apps/streams/tests/videos/x264.mp4"

    def setUp(self):
        from ..media import MediaWorker
        self.media_worker = MediaWorker()

    def test_exception_raised_on_non_existant_file(self):
        # Prepare data
        profile = self._create_transcode_profile()

        # Call method
        from ..exceptions import TranscodeError
        self.assertRaises(TranscodeError,
            self.media_worker.transcode_segment,
            f"/tmp/{uuid4()}.ts",
            profile)

    def test_x264_in_x264_out(self):
        # Prepare data
        profile = self._create_transcode_profile()

        # Call method
        video_out_bytes, stderr, command = self.media_worker.transcode_segment(
            self.video_path,
            profile)

    def test_x264_in_265_out(self):
        # Prepare data
        profile = self._create_transcode_profile(video_codec="libx265")

        # Call method
        video_out_bytes, stderr, command = self.media_worker.transcode_segment(
            self.video_path,
            profile)

    def test_x265_in_264_out(self):
        # Prepare data
        profile = self._create_transcode_profile()

        # Call method
        video_out_bytes, stderr, command = self.media_worker.transcode_segment(
            "apps/streams/tests/videos/x265.mp4",
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


class MediaWorkerStillGeneration(TestCase):
    video_path = "apps/streams/tests/videos/segment.ts"

    def setUp(self):
        from ..media import MediaWorker
        self.media_worker = MediaWorker()

    def test_exception_raised_on_non_existant_file(self):
        # Call method
        from ..exceptions import TranscodeError
        self.assertRaises(TranscodeError,
            self.media_worker.generate_still_from_video,
            f"/tmp/{uuid4()}.ts")

    def test_valid_generation(self):
        # Call method
        image_out_bytes, timecode, stderr = \
            self.media_worker.generate_still_from_video(
                self.video_path)
        
        # Assertions
        self.assertGreater(len(image_out_bytes), 0)
        self.assertEqual(46.904044, timecode)

class MediaWorkerParseTest(TestCase):
    def setUp(self):
        root_path = "apps/streams/tests/stderr"
        with open(f"{root_path}/successful_transcode.txt", "r") as f:
            self.successful_transcode = f.read()

        from ..media import MediaWorker
        self.media_worker = MediaWorker()

    def test_valid_duration_parse(self):
        # Call method
        duration = self.media_worker.parse_duration_from_stderr(
            self.successful_transcode)

        # Assertions
        self.assertEqual(duration, 7328.24)

    def test_no_duration_parse(self):
        # Call method
        duration = self.media_worker.parse_duration_from_stderr("")

        # Assertions
        self.assertIsNone(duration)

    def test_valid_start_parse(self):
        # Call method
        timecode = self.media_worker.parse_start_timecode_from_stderr(
            self.successful_transcode)

        # Assertions
        self.assertEqual(timecode, 1065.501333)
    
    def test_no_start_parse(self):
        # Call method
        timecode = self.media_worker.parse_start_timecode_from_stderr("")

        # Assertions
        self.assertIsNone(timecode)