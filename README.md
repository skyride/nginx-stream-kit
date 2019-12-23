# Nginx Stream Kit

This is a simple off-the-shelf kit for streaming video using [nginx-rtmp-module](https://github.com/arut/nginx-rtmp-module),
ffmpeg and a simple Django application. Individually these pieces are all extremely configurable, almost to a fault
in many use cases. This application provides them packaged as a turn key application designed to make full use
of a single server. Since it uses HLS and HTTP to deliver all video content it should theoretically be possible
to dramatically scale up the user count of this system simply by placing CloudFront or another proxy-based CDN
in front of the system.