FROM nginx:1.17.6

COPY default.conf /etc/nginx/conf.d/

COPY .bashrc /tmp/.bashrc
RUN cat /tmp/.bashrc >> /root/.bashrc