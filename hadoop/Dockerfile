FROM debian:bullseye-slim

ARG DEBIAN_FRONTEND=noninteractive
ARG HADOOP_VERSION=3.3.6

# Reintentos de apt
RUN printf 'Acquire::Retries "10";\nAcquire::http::Timeout "60";\nAcquire::http::Pipeline-Depth "0";\n' > /etc/apt/apt.conf.d/80-retries

# Bullseye ya es archivo: usar archive.debian.org
RUN sed -i -e 's|deb.debian.org|archive.debian.org|g' \
    -e 's|security.debian.org|archive.debian.org|g' \
    -e '/bullseye-updates/d' /etc/apt/sources.list \
    && echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99archive

# Java, SSH y Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-11-jdk-headless openssh-server openssh-client \
    python3 curl ca-certificates procps \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s "$(dirname $(dirname $(readlink -f $(which javac))))" /usr/lib/jvm/java

# Variables de entorno
ENV JAVA_HOME=/usr/lib/jvm/java
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Hadoop standalone (se descarga en el build; el .tar.gz no va en el repo)
RUN for url in \
    https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
    https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz ; do \
    curl -fL --retry 10 --retry-delay 5 --retry-all-errors -C - -o /tmp/hadoop.tar.gz "$url" && break ; \
    done \
    && tar -xzf /tmp/hadoop.tar.gz -C /opt \
    && mv /opt/hadoop-${HADOOP_VERSION} ${HADOOP_HOME} \
    && rm /tmp/hadoop.tar.gz \
    && echo "export JAVA_HOME=${JAVA_HOME}" >> ${HADOOP_HOME}/etc/hadoop/hadoop-env.sh

# SSH: solo llaves, sin contraseñas. Las llaves se generan al arrancar (start.sh)
RUN mkdir -p /run/sshd /root/.ssh /keys \
    && chmod 700 /root/.ssh \
    && printf "Host *\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null\n" > /root/.ssh/config \
    && sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config \
    && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config

COPY start.sh /usr/local/bin/start.sh
RUN sed -i 's/\r$//' /usr/local/bin/start.sh && chmod +x /usr/local/bin/start.sh

WORKDIR /mapreduce
EXPOSE 22
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["/usr/local/bin/start.sh"]