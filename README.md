# datastax-workshop

##Docker

    cat /etc/dse/cassandra/cassandra.yaml | grep broadcast_rpc_address:|awk -F' ' '{print $2}' > config.txt


```
docker build -t cql-notebook-image .
docker run --net=host -d -p 0.0.0.0:7001:7001 --name cql-notebook cql-notebook-image


One liner to remove answers from Notebooks:
```
cat Lab\ 1\ Workbook.ipynb |  jq '{"cells":[  .cells[] | select(.cell_type=="raw" // .cell_type=="code" | not) ]} + del (."cells")' > Lab\ 1\ Workbook\ Student.ipynb
```

Or just run `./generate_student_workbooks.sh`
