FROM quay.io/astronomer/astro-runtime:12.7.1

USER root

# Instalación limpia de Java 17
RUN apt-get update && \
  apt-get install -y --no-install-recommends openjdk-17-jdk ant && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME dinámico (funciona en x86 y ARM)
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
# Si estás en una Mac con Silicon o Raspberry, usa: /usr/lib/jvm/java-17-openjdk-arm64

USER astro
