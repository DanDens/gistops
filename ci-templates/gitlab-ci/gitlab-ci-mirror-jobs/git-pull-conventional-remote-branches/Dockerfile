FROM docker.apps.bssn-software.de/base-images/alpine/git:v2.26.2

# We need bash to be 
RUN apk update
RUN apk upgrade
RUN apk add bash

# Force push to remote branch
ADD apply.sh .
RUN chmod ugo+x apply.sh

CMD [ "/bin/bash", "-c", "/git/apply.sh" ]