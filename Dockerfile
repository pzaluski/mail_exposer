FROM ubuntu:20.04
LABEL maintainer="Piotr Załuski"

ENV TZ=Europe/Warsaw
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update
RUN apt-get install -y python3-pip python3 nginx-full

#RUN useradd mail_exposer
#RUN usermod -aG syslog mail_exposer

RUN mkdir /app
COPY requirements.txt /app/

WORKDIR /app
RUN pip3 install -r requirements.txt
 
COPY /app /app

#RUN openssl req -subj '/CN=localhost' -x509 -newkey rsa:4096 -nodes -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt -days 365
COPY nginx/nginx-selfsigned.crt /etc/ssl/certs/
COPY nginx/nginx-selfsigned.key /etc/ssl/private/
COPY nginx/default /etc/nginx/sites-enabled/
COPY nginx/htpasswd /etc/nginx/
COPY service/mail_exposer /etc/init.d/
RUN chmod +x /etc/init.d/mail_exposer
COPY service/wrapper.sh /app/wrapper.sh
RUN chmod +x /app/wrapper.sh

CMD ["/app/wrapper.sh"]