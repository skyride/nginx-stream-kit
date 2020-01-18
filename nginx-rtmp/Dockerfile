FROM python:3.8-alpine3.11

WORKDIR /build

# Requirements
RUN apk add wget git

# Download Nginx
ADD http://nginx.org/download/nginx-1.17.6.tar.gz /build/
RUN tar -xvf nginx-1.17.6.tar.gz

# Download RTMP module
RUN git clone https://github.com/arut/nginx-rtmp-module.git

# Build dependencies
RUN apk add build-base openssl-dev zlib-dev

# Build and install Nginx
WORKDIR /build/nginx-1.17.6
ARG CFLAGS="-Wno-error"
RUN ./configure --add-module=/build/nginx-rtmp-module --without-http_rewrite_module
RUN make -j 4
RUN make install

# Install Python dependencies and uploader
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
COPY uploader.py /app/uploader.py

# Configure System
RUN apk add ncurses bash htop
COPY .bashrc /tmp/.bashrc
RUN cat /tmp/.bashrc >> /root/.bashrc

COPY nginx.conf /etc/nginx/
RUN ln -s /usr/local/nginx/sbin/nginx /bin/nginx

CMD ["nginx", "-c", "/etc/nginx/nginx.conf", "-g", "daemon off;"];