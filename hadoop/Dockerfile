FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ARG HADOOP_VERSION=3.3.6

RUN echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80-retries

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

# Hadoop (se descarga en el build; el .tar.gz no va en el repo)
RUN for url in \
    https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
    https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz ; do \
    curl -fL --retry 10 --retry-delay 5 --retry-all-errors -C - -o /tmp/hadoop.tar.gz "$url" && break ; \
    done \
    && tar -xzf /tmp/hadoop.tar.gz -C /opt \
    && mv /opt/hadoop-${HADOOP_VERSION} ${HADOOP_HOME} \
    && rm /tmp/hadoop.tar.gz \
    && echo "export JAVA_HOME=${JAVA_HOME}" >> ${HADOOP_HOME}/etc/hadoop/hadoop-env.sh

# SSH sin contraseña
RUN mkdir -p /var/run/sshd /root/.ssh \
    && ssh-keygen -t rsa -b 4096 -N "" -f /root/.ssh/id_rsa \
    && cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys \
    && chmod 700 /root/.ssh && chmod 600 /root/.ssh/authorized_keys \
    && printf "Host *\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null\n" > /root/.ssh/config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

WORKDIR /mapreduce
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["service ssh start && tail -f /dev/null"]