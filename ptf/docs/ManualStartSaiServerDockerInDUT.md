# Manual Start SaiServer Docker In DUT

*In this article, you will get to know how to start a saiserver docker in a dut(Device under test).*
1. pull or upload the saiserver docker in your dut.
```
# if your docker registry has the saisever docker that you pushed like
# docker push <docker-registry-address>/docker-saiserver-<SHORTEN_ASIC>:<TAG_WITH_OS_VERSION>
# then, you can pull it,  like
docker pull <docker-registry-address>/docker-saiserver-<SHORTEN_ASIC>:<TAG_WITH_OS_VERSION>
# i.e.
docker pull soniccr1.azurecr.io/docker-saiserver-brcm:20201231.29
```
Otherwise, you can upload the docker file from a local building and manually upload it
- import and start the docker
```shell
docker load -i ./<DOCKERFILE>
```
> please refer to doc for how to build a saiserver docker
[Check Sonic Version](./CheckVersion.md#check-sonic-version) and [Build Saiserver Docker](./BuildSaiserverDocker.md)


