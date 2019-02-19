FROM kbase/kb_python:python3

ARG BUILD_DATE
ARG VCS_REF
ARG BRANCH=develop

COPY ./ /kb/module
WORKDIR /kb/module

RUN pip install --upgrade pip setuptools wheel
RUN while read requirement; do conda install --yes $requirement || pip install $requirement; done < /kb/module/requirements.txt

LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-url="https://github.com/kbase/feeds.git" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0.0-rc1" \
      us.kbase.vcs-branch=$BRANCH \
      maintainer="Steve Chan sychan@lbl.gov"

ENV KB_DEPLOYMENT_CONFIG=/kb/module/deploy.cfg

ENTRYPOINT [ "/kb/deployment/bin/dockerize" ]
CMD [ "--template", \
      "/kb/module/deployment/conf/.templates/deploy.cfg.templ:/kb/module/deploy.cfg" \
      "make start" ]