FROM alpine

LABEL org.opencontainers.image.source="https://github.com/ATNOG/mp1-test-app-mec"

RUN apk update
RUN apk add python3
RUN apk add py3-flask
RUN apk add py3-requests

COPY app.py /usr/local/bin/app.py
COPY app_site /var/www/
RUN chmod +x /usr/local/bin/app.py

CMD /usr/local/bin/app.py
