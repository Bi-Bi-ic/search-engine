# pull official base image
FROM python:3.7.9-buster

RUN echo \
    && apt-get update \ 
    && apt-get --yes install apt-file \
    && apt-file update

RUN echo \
    && apt-get --yes install build-essential
ARG USER=root  
RUN usermod -aG sudo $USER

# set work directory
WORKDIR /search-engine
RUN mkdir -p ./logs

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /search-engine/requirements.txt
RUN export LDFLAGS="-L/usr/local/opt/openssl/lib"

RUN pip install virtualenv
ENV VIRTUAL_ENV=/venv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install -r requirements.txt


# copy project
COPY . /search-engine/
RUN chmod +wr ./logs
USER $USER

EXPOSE 8080
CMD ["python", "app.py"]