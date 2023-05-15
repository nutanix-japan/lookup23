FROM python:alpine3.11

# set a directory for the app
WORKDIR /home

# copy all the files to the container
COPY . /home/

# install pip dependencies
RUN pip install -r requirements.txt
# RUN mv lookup.py /usr/local/lib/python3.11/bin/
# run the command to start bottle web server
CMD ["python3", "./lookup.py"]
# docker run -dit -p  8090:8090 -v /home/ubuntu/github/lookup/APAC_SE_Cluster_assignments.xlsx:/mnt/APAC_SE_Cluster_assignments.xlsx -e sheet_path=/mnt/APAC_SE_Cluster_assignments.xlsx --restart unless-stopped ariesbabu/luckychan
