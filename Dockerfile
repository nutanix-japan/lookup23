FROM python:alpine3.11

# set a directory for the app
WORKDIR /home

# copy all the files to the container
COPY . /home/

# install pip dependencies
RUN pip install -r requirements.txt

# run the command to start bottle web server
CMD ["python3", "./lookup.py"]

# docker run -dit -p  5000:5000 -v /home/ubuntu/github/lookup/APAC.xlsx:/mnt/APAC.xlsx -e sheet_path=/mnt/APAC.xlsx --restart unless-stopped ariesbabu/luckychan
