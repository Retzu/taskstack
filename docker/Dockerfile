FROM python:latest

RUN apt-get install git
RUN git clone https://github.com/Retzudo/taskstack.git /taskstack
RUN pip install --upgrade pip
RUN pip install -r /taskstack/requirements.txt
RUN pip install gunicorn

COPY start.sh /taskstack/taskstack/start.sh

WORKDIR /taskstack/taskstack

EXPOSE 8000
CMD ./start.sh
