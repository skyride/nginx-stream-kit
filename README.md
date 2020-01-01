# Nginx Stream Kit

This is a simple off-the-shelf kit for streaming video using [nginx-rtmp-module](https://github.com/arut/nginx-rtmp-module),
ffmpeg and a simple Django application. Individually these pieces are all extremely configurable, almost to a fault
in many use cases. This application provides them packaged as a turn key application designed to make full use
of a single server. Since it uses HLS and HTTP to deliver all video content it should theoretically be possible
to dramatically scale up the user count of this system simply by placing CloudFront or another proxy-based CDN
in front of the system.

## Setup

Run the following scripts. Note the build command can take ~10 minutes as ffmpeg requires a lot of compiling. This is 
entirely normal.

```
git clone git@github.com:skyride/nginx-stream-kit.git
cd nginx-stream-kit
docker-compose build
docker-compose run --rm web ./manage.py migrate
docker-compose run --rm web ./manage.py collectstatic
echo SECRET_KEY=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w ${1:-32} | head -n 1` >> .env
```

You can create an account to login to the `/admin` panel using the following command:
` docker-compose run --rm web ./manage.py createsuperuser`

## Usage

`docker-compose up`

Access the system at `http://localhost:2323/`. You can stream to the system using any RTMP streaming tool at
`rtmp://localhost/ingest/{STREAM_KEY}`. The stream key at current is anything you want. The stream can then be
accessed at `http://localhost:2323/watch/{STREAM_KEY}` or from the list at `http://localhost:2323/`.

### Production

In production use this command to bring it up with gunicorn instead of the Django local development server as a
background process.

`docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d`