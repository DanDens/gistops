FROM docker.apps.bssn-software.de/base-images/bitnami/git:2.37.3

# We need bash to be 
RUN export DEBIAN_FRONTEND=noninteractive && apt --yes --force-yes update
RUN export DEBIAN_FRONTEND=noninteractive && apt --yes --force-yes upgrade
RUN export DEBIAN_FRONTEND=noninteractive && apt-get install --yes --force-yes bash zip curl

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install
RUN aws --version 

# Force push to remote branch
ADD apply.sh .
RUN chmod ugo+x apply.sh

CMD [ "/bin/bash", "-c", "apply.sh" ]