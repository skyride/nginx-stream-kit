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