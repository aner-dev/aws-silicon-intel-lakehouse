FROM quay.io/astronomer/astro-runtime:12.7.1

USER root

RUN apt-get update && \
  apt-get install -y --no-install-recommends openjdk-17-jre-headless && \ 
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# openjdk-17-jdk: ~300 MB - 500 MB | openjdk-17-jre-headless: ~150 MB - 200 MB
# headless: without GUI ("The Brain without the Face")
# Set JAVA_HOME dynamic (works in x86 & ARM)
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER astro
