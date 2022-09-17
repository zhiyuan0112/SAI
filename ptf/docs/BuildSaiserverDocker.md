# Build Saiserver Docker
*In this article, you will get known how to get a saiserver docker and get a builder to build saiserver binary*

1. Start a local build
   ```
   # Clean environment as needed
   make reset
   # Init env
   make init
   # NOSTRETCH=y : Current image is buster
   # KEEP_SLAVE_ON=yes: Keeps slave container up and active after building process concludes.
   #setup environment as broadcom flatform
   make configure PLATFORM=broadcom
   #start build
   NOSTRETCH=y NOJESSIE=y KEEP_SLAVE_ON=yes ENABLE_SYNCD_RPC=y make target/debs/buster/saiserver_0.9.4_amd64.deb
   ```
   **You can get this build target by running commands like(adjust as needed): NOSTRETCH=y NOJESSIE=y ENABLE_SYNCD_RPC=y make list**


2. Wait for the build process 
3. In the end, you will get something like this, and prompt as below (inside docker)
   ```
   # Check if thrift installed
   richardyu@a0363ed6ca36:/sonic$ thrift
   Usage: thrift [options] file

   Use thrift -help for a list of options
   ```
4. Keep this terminal and start another terminal, log in to the same host
 - Check the docker, the builder appears with the name sonic-slave-***, it is always the recently created one
   ```
   docker ps
   CONTAINER ID   IMAGE                                                 COMMAND                  CREATED          STATUS          
   PORTS                                     NAMES
   e1df2df072c4   sonic-slave-buster-richardyu:86ef76a28e6              "bash -c 'make -f sl…"   36 minutes ago   Up 36 minutes   
   22/tcp                                         condescending_lovelace
   ```
 - Commit that docker as a saiserver-docker builder for other bugging or related resource building usages.
   ```
   docker commit <docker_name> <docker_image>:<tag>
   docker commit condescending_lovelace saisever-builder-20201231-39:0.0.1
   ```
5. Then, exit from the docker above (console as 'richardyu@e1df2df072c4'), you can get your buildout artifacts in folder `./target`, there also contains the logs and other accessories
6. For building the saiserver binary, you can mount your local SAI repository to that docker and just start that docker for your building purpose.
   ```
   # SAI repo is located inside the local /code folder
   docker run --name saisever-builder-20201231-39 -v  /code:/data -di saisever-builder-20201231-39:0.0.1 bash
   ```
