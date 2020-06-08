FROM python:3
MAINTAINER Fazlur Rahman "fazlur@alterra.id"
RUN mkdir -p /trello
COPY . /trello
RUN pip install -r /trello/requirements.txt
WORKDIR /trello
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]

