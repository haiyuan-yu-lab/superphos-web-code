# SuperPhos
## Website (and Docker file) for SuperPhos

Download the following files in a local directory and run the following commands to set up docker container locally. The following code was tested locally on Macbook Pro 2020 (Monterey 12.5.1) and on BioHPC (compute cluster)

Build the docker image and see the image ID with the following code -

```
docker build -t superphos-web .
docker images
```

OUTPUT - 

| REPOSITORY | TAG | IMAGE ID | CREATED | SIZE |
| --- | --- | --- | --- | --- |
| superphos-web | latest | 89ec007b4999 | 12 seconds ago | 1.77GB |



Run the container and set up a proxy to a specific port (here, 8967) using the code below. Also get information on whether the docker container successfully ran or not using the second line of code as well as get the container ID.

```
docker run --name superphos-web -p 8967:8967 -t -d 89ec007b4999
docker ps -a
```
OUTPUT - 

| CONTAINER ID | IMAGE | COMMAND | CREATED | STATUS | PORTS | NAMES |
| --- | --- | --- | --- | --- | --- | --- |
| 1787daa50cea | 89ec007b4999 | "flask run --host=0.…" | 18 seconds ago | Up 8 seconds | 0.0.0.0:8967->8967/tcp, :::8967->8967/tcp | superphos-web |


For diagnosing what might be issues in the container -

```
docker logs 1787daa50cea
```

For rerunning the container in case of breakage -

```
docker restart superphos-web
```