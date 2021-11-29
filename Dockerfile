FROM python:3.9-alpine

RUN apk update
RUN mkdir /project
WORKDIR /project
COPY . /project

RUN pip install -r /project/requirements.txt

ENTRYPOINT [ "python", "mac_resolver.py" ]

CMD [ "-h" ]
