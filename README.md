# Setting up container:
create file from `config.ini.org` -> `config.ini` with your credentials

    sudo docker build -t mail_exposer .
    sudo docker run --rm -p 8080:80/tcp -it mail_exposer

or

    sudo docker-compose up --build --detach

# Instruction:
Config locatated in `/data/mail_exposer/config/config.ini`

Logs are kept in `/data/mail_exposer/logs/activity.log` (default location)

