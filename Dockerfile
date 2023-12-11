FROM ubuntu:jammy-20231128
RUN apt update && apt install -y python3-dev python3-pip libpq-dev git curl
RUN curl -sL https://deb.nodesource.com/setup_18.x -o nodesource_setup.sh
RUN bash nodesource_setup.sh
RUN apt install -y nodejs
RUN npm install -g newman
COPY . "/LCV-CM"
WORKDIR "/LCV-CM"
RUN pip3 install -r requirements.txt
EXPOSE 3251
RUN chmod +x entrypoint.sh
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]