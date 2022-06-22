# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
FROM python:3.10-bullseye as builder
ARG VERSION="master"
RUN pip install -U pip \
 && pip install git+https://github.com/huisint/cropsiss@${VERSION}

FROM python:3.10-slim-bullseye as runner
ARG TARGETPLATFORM
# Install chromium
WORKDIR /tmp/chromium
COPY install_chromium.sh /tmp/chromium
RUN bash -e install_chromium.sh ${TARGETPLATFORM}
RUN rm -rf /tmp/chromium
# Copy packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
WORKDIR /cropsiss
ENV PYTHONUNBUFFERED 1
CMD [ "cropsiss" ]