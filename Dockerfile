FROM ubuntu:20.04
LABEL maintainer="Piotr Załuski"

ENV TZ=Europe/Warsaw
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update
RUN apt-get install -y python3-pip python3 nginx-full

RUN mkdir /app
ADD requirements.txt /app/

WORKDIR /app
RUN pip3 install -r requirements.txt
 
ADD /app /app

ADD nginx/default /etc/nginx/sites-enabled/
ADD service/mail_exposer /etc/init.d/
RUN chmod +x /etc/init.d/mail_exposer


COPY service/wrapper.sh /app/wrapper.sh
RUN chmod +x /app/wrapper.sh

CMD ["/app/wrapper.sh"]