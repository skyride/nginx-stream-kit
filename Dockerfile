FROM python:3.8-alpine

# Download ffmpeg and dependencies
WORKDIR /build
RUN apk add nasm yasm x264-dev x265-dev numactl-dev libvpx-dev wget git \
            autoconf automake libtool build-base openssl-dev zlib-dev
RUN git -C fdk-aac pull 2> /dev/null || git clone --depth 1 https://github.com/mstorsjo/fdk-aac && \
    cd fdk-aac && \
    autoreconf -fiv && \
    ./configure --prefix="/ffmpeg_build" --disable-shared && \
    make -j 4 && \
    make install
RUN apk add lame-dev opus-dev

# Compile and install ffmpeg
WORKDIR /build
RUN wget -O ffmpeg-snapshot.tar.bz2 https://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2 && \
    tar xjvf ffmpeg-snapshot.tar.bz2 && \
    cd ffmpeg && \
    PKG_CONFIG_PATH="/ffmpeg_build/lib/pkgconfig" ./configure \
    --prefix="/ffmpeg_build" \
    --pkg-config-flags="--static" \
    --extra-cflags="-I/ffmpeg_build/include" \
    --extra-ldflags="-L/ffmpeg_build/lib" \
    --extra-libs="-lpthread -lm" \
    --bindir="/bin" \
    --enable-gpl \
    --enable-libfdk-aac \
    --enable-libmp3lame \
    --enable-libopus \
    --enable-libvpx \
    --enable-libx264 \
    --enable-libx265 \
    --enable-nonfree && \
    PATH="/bin:$PATH" make -j 4 && \
    make install && \
    hash -r

# Python environment
WORKDIR /app

# Python requirements
RUN apk add --no-cache postgresql-dev
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# .bashrc
COPY .bashrc /tmp/.bashrc
RUN cat /tmp/.bashrc >> /root/.bashrc

ENV PYTHONUNBUFFERED=1