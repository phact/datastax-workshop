# datastax-workshop

The workshop is a dockerized notebook that includes the data load and setup + the exercises hosted on port 7001.

##Docker

install docker https://docs.docker.com/engine/installation/linux

add your user to the docker group 

    sudo gpasswd -a ${USER} docker

and refresh:

    newgrp docker

Set up config.txt with your broadcast rpc address (client address for DSE)

    cat /etc/dse/cassandra/cassandra.yaml | grep broadcast_rpc_address:|awk -F' ' '{print $2}' > config.txt


For OSX
```
docker-machine start default
eval $(docker-machine env default)
#a bit of cleanup
docker rm -f $(docker ps -aq)
docker rmi -f $(docker images -aq)
```

For linux


```
service docker start
```


```
docker build -t cql-notebook-image .
docker run --net=host -d -p 0.0.0.0:7001:7001 --name cql-notebook cql-notebook-image
```

One liner to remove answers from Notebooks:

```
cat Lab\ 1\ Workbook.ipynb |  jq '{"cells":[  .cells[] | select(.cell_type=="raw" // .cell_type=="code" | not) ]} + del (."cells")' > Lab\ 1\ Workbook\ Student.ipynb
```

Or just run `./generate_student_workbooks.sh`
