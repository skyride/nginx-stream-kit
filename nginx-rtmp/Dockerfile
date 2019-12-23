FROM alpine:3.11

WORKDIR /build

# Requirements
RUN apk add wget git

# Download Nginx
ADD http://nginx.org/download/nginx-1.17.6.tar.gz /build/
RUN tar -xvf nginx-1.17.6.tar.gz

# Download RTMP module
RUN git clone https://github.com/arut/nginx-rtmp-module.git

# Build requirements
RUN apk add build-base openssl-dev zlib-dev

# Build
WORKDIR /build/nginx-1.17.6
ARG CFLAGS="-Wno-error"
RUN ./configure --add-module=/build/nginx-rtmp-module --without-http_rewrite_module
RUN make
RUN make install

# Download ffmpeg and dependencies
WORKDIR /build
RUN apk add nasm yasm x264-dev x265-dev numactl-dev libvpx-dev
RUN apk add autoconf automake libtool
RUN git -C fdk-aac pull 2> /dev/null || git clone --depth 1 https://github.com/mstorsjo/fdk-aac && \
    cd fdk-aac && \
    autoreconf -fiv && \
    ./configure --prefix="/ffmpeg_build" --disable-shared && \
    make && \
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
    PATH="/bin:$PATH" make && \
    make install && \
    hash -r