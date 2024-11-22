FROM python:3.9.19

ARG BUILD_DATE
ARG VCS_REF
ARG BRANCH=develop

RUN apt-get update
RUN apt-get install wget

# install dockerize
WORKDIR /opt
RUN wget -q https://github.com/kbase/dockerize/raw/master/dockerize-linux-amd64-v0.6.1.tar.gz \
    && tar xvzf dockerize-linux-amd64-v0.6.1.tar.gz \
    && rm dockerize-linux-amd64-v0.6.1.tar.gz
RUN mkdir -p /kb/deployment/bin/
RUN ln -s /opt/dockerize /kb/deployment/bin/dockerize

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

# set workdir
COPY ./ /kb/module
WORKDIR /kb/module

LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-url="https://github.com/kbase/feeds.git" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0.0-rc1" \
      us.kbase.vcs-branch=$BRANCH \
      maintainer="Steve Chan sychan@lbl.gov"

ENV KB_DEPLOYMENT_CONFIG=/kb/module/deploy.cfg

ENTRYPOINT [ "/kb/deployment/bin/dockerize" ]
CMD [ "--template", \
      "/kb/module/deployment/conf/.templates/deploy.cfg.templ:/kb/module/deploy.cfg", \
      "make", "start" ]