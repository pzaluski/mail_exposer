Setting up container:
create file from config.ini.org -> config.ini with your credentials
docker build -t mail_exposer .
docker run --rm -p 8080:80/tcp -it mail_exposer

Instruction:
Config locatated in /app/config/config.ini
Logs are kept in /var/log/mail_exposer.log (default location)

What should be still done is to protect webdav with at least simple basic auth (not implemented to simplify demo solution).
Logs and config should be exposed as mountpoints in order to manipulte them outside container. 
Container could be packed with some Service ex. Docker Swarm.