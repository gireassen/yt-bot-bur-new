FROM python:3.9.7-slim

WORKDIR /yt-bot-bur

COPY requirements.txt /yt-bot-bur/

RUN pip install -r requirements.txt

ENV TZ=Europe/Moscow

RUN cp /usr/share/zoneinfo/$TZ /etc/localtime

COPY bot.py /yt-bot-bur/
COPY functions.py /yt-bot-bur/
COPY email_module.py /yt-bot-bur/
COPY start.py /yt-bot-bur/

ENTRYPOINT ["python3"]

CMD ["-u","bot.py"]
