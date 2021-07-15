FROM ubuntu:18.04

ENV SOURCE_DIR="/src/"
ENV BUILD_DIR="/build/"
ENV OUTPUT_DIR="/var/output/"
ENV METRICS_FN_NAME="HaloMetricsToSumologic"
ENV EVENTS_CODE_DIR="halo_events_to_sumologic"
ENV EVENTS_FN_NAME="HaloEventsToSumologic"
ENV METRICS_CODE_DIR="halo_metrics_to_sumologic"

ENV LC_ALL="C.UTF-8"
ENV LANG="C.UTF-8"

RUN export LC_ALL=C.UTF-8
RUN export LANG=C.UTF-8

RUN mkdir -p ${OUTPUT_DIR}
RUN mkdir -p ${BUILD_DIR}
RUN mkdir -p ${SOURCE_DIR}

RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    zip

RUN pip3 install aws-sam-cli

# Run sam build to download all deps
WORKDIR ${SOURCE_DIR}
COPY src/ ${SOURCE_DIR}

# Build events shipper
WORKDIR ${SOURCE_DIR}
RUN sam build --debug --region=us-west-2 -b ${BUILD_DIR}

# Build metrics shipper
WORKDIR ${SOURCE_DIR}
RUN sam build --debug --region=us-west-2 -b ${BUILD_DIR}

RUN ls /build/*

# Zip up metrics lambda function
WORKDIR ${BUILD_DIR}${METRICS_FN_NAME}
RUN zip -r ${OUTPUT_DIR}${METRICS_FN_NAME}.zip ./*

# Zip up events lambda function
WORKDIR ${BUILD_DIR}${EVENTS_FN_NAME}
RUN zip -r ${OUTPUT_DIR}${EVENTS_FN_NAME}.zip ./*

RUN ls ${OUTPUT_DIR}
