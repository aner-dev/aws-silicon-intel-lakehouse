FROM quay.io/astronomer/astro-runtime:12.7.1

USER root

RUN apt-get update && \
  apt-get install -y --no-install-recommends openjdk-17-jdk ant && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME dynamic (works in x86 & ARM)
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

USER astro
