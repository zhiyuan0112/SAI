# PTF-SAIv2 Overview
*This article will introduce PTF-SAIv2 and the detailed process of entire PTF-SAIv2 testing.*

- [PTF-SAIv2 Overview](#ptf-saiv2-overview)
  - [SAI PTF v2 introduction](#sai-ptf-v2-introduction)
    - [Logical Topology](#logical-topology)
    - [Physical Connection](#physical-connection)
  - [Setup Testbed](#setup-testbed)
    - [Build PTF-SAIv2 components](#build-ptf-saiv2-components)
    - [Setup the testbed by sonic-mgmt](#setup-the-testbed-by-sonic-mgmt)
    - [Setup DUT (Device under testing)](#setup-dut-device-under-testing)
    - [Setup ptf-sai docker and run test](#setup-ptf-sai-docker-and-run-test)
  - [Reference](#reference)



## SAI PTF v2 introduction
*In this part, we will get to know what's the SAI-PTF v2 framework.*

SAI-PTF v2 is upgraded from previous [SAI-PTF fremework](../../test/saithrift/README.md).
SAI PTFv2 has two parts, [PTF (Packet Test Framework)](https://github.com/p4lang/ptf) and [SAI PRC framework](../../meta/rpc/README.md).

### Logical Topology
![Logical topology](./img/logic_connection.png#=120x120)

In the chart above the components are:
- PTF container - run test cases, and use an RPC client to invoke the SAI interfaces on DUT
- SAI Server container - run inside DUT/switch, which exposes the SAI SDK APIs from the libsai


### Physical Connection
Below is the [Physical connection of testbed](./ExamplePhysicalConnection.md):
![Physical connection](./img/physical_connection.png)

Key components in the physical connection:

* Test servers
* Fanout switches
  * Root fanout switch (optional)
  * Leaf fanout switch
* SONiC DUT

Key aspects of the physical connection:

1. Every DUT port is connected to one of leaf fanout switches.
2. Every leaf fanout switch has unique VLAN tag for every DUT port.
3. Root fanout switch connects leaf fanout switches and test servers using 802.1Q trunks. *The root fanout switch is not mandatory if there is only one testbed or a test server is only used by one testbed. In this case, the leaf fanout switch can be directly connected with NIC of test server by 802.1Q trunk.*
4. Any test server can access any DUT port by sending a packet with the port VLAN tag (The root fanout switch should have this VLAN number enabled on the server trunk)


 > Note: By default, we use PTF32 topology for SAI PTF testing. With PTF32 topology, it will use 32 ports, if needs to test against more ports, like 64 ports, please use the PTF64 topology or other customized configuration.

 > Compared with other [SONiC Logical topologies](https://github.com/sonic-net/sonic-mgmt/blob/master/docs/testbed/README.testbed.Overview.md#logical-topologies), SAI-PTFv2 is simpler, it only gets connected from PTF to DUT. 

 > For more detail about the SONiC testbed topology please refer to [sonic testbed overview](https://github.com/sonic-net/sonic-mgmt/blob/master/docs/testbed/README.testbed.Overview.md).

## Setup Testbed
*In this part, we will build PTF-SAIv2 infras using sonic-buildimage.*

 > Note: If you want to setup the test enviroment, please refer to [SAI PTF introduction and manually setup Testbed](ManuallySetupTestbedGuide.md).

In the following, we use other SONiC scripts to help setup the [SAI PTF topology](https://github.com/sonic-net/sonic-mgmt/blob/master/docs/testbed/README.testbed.Overview.md#ptf-type-topology) environment with all the testing components mentioned in [SAI PTF introduction and manually setup Testbed](ManuallySetupTestbedGuide.md).

### Build PTF-SAIv2 components
*In this section, we will build the test related resources.*

For SAI-PTFv2 test, we need to build components:
1. Docker PTF, which contains all the runtime dependences
2. Docker SAIServerv2, which contains the RPC Server (as described in ##Instructuon section), SAI SDK and all the running dependences
3. python-saithrift, the RPC client, this binary will be generated when build the docker saiserverv2

> Note: SAIServer (RPC Server) and python-saithrift (RPC client) must be built from a same SAI version, when deploying you environment, please make sure they are from same version.

Precondition:

Before start the build process, please make sure you get the right sonic buildimage branch.
For how to check the sai header version and sonic branch from a certain sonic image please refer to
[Check SAI Header Version And SONiC Branch](CheckVersion.md)

> Note: the example below will base on the sonic 202205 branch

1. Checkout code in sonic-buildimage repo
    > please check the  with the branch and commit id previous checked   

    ```
    git clone https://github.com/Azure/sonic-buildimage.git
    cd sonic-buildimage

    git checkout <specific branch>
    git reset --hard <specific commit id>
    ```
    Here we use 202205 branch for example:
    ```
    git clone https://github.com/Azure/sonic-buildimage.git
    cd sonic-buildimage
    git checkout 202205    
    ```

2. Build PTF-SAIv2 infras 

    - build saiserverv2
        ```
        # Init env
        make init
        # BLDENV=buster: Current image is buster
        # PLATFORM=<vendor name> Setup platform environment e.g. broadcom
        make BLDENV=buster configure PLATFORM=broadcom

        # SAITHRIFT_V2=y: build the saiserver version 2rd
        # build brcm saiserverv2 docker 
        # build brcm saiserverv2 docker 
        # build brcm saiserverv2 docker 
        make BLDENV=buster SAITHRIFT_V2=y -f Makefile.work target/docker-saiserverv2-brcm.gz
        ```

    - build docker ptf-sai
        ```
        # build docker ptf-sai
        # Clean environment
        make reset

        # Setup platform environment e.g. virtual switch
        make BLDENV=buster configure PLATFORM=vs

        make BLDENV=buster SAITHRIFT_V2=y target/docker-ptf-sai.gz
        ```

3. Locate the generated binary and dockers

    - docker saiserverv2 at <local_folder>/sonic-buildimage/target/docker-saiserverv2-brcm.gz
    - docker ptf-sai at <local_folder>/target/docker-ptf-sai.gz
    - python_saithrift at <local_folder>/target/debs/buster/python-saithrift_0.9.4_amd64.deb


    > Note: for different platform (BLDENV=buster), the output folder might be different, i.e. BLDENV=bullseye, it will be <local_folder>/target/debs/bullseye

 
### Setup the testbed by sonic-mgmt

*In this section, we will set up the physical switch testbed by sonic-mgmt.*

prepration:
 Install the sonic image in the DUT, as for how to install a sonic image on the supported switch, please refer to this doc [Install sonic eos image](https://github.com/Azure/SONiC/wiki/Quick-Start#install-sonic-eos-image)
 You have a local docker rigistry which can be used to push and pull dockers

1. upload the build out dockers
   We need to upload those docker to your local available docker registery:
    - docker saiserverv2 at <local_folder>/sonic-buildimage/target/docker-saiserverv2-brcm.gz
    - docker ptf-sai at <local_folder>/target/docker-ptf-sai.gz
    ```
    docker load -i <local_folder>/sonic-buildimage/target/docker-saiserverv2-brcm.gz
    docker load -i <local_folder>/target/docker-ptf-sai.gz

    docker push <docker-registry-addreee>/docker-saiserverv2-brcm:<TAG_WITH_OS_VERSION>
    docker push <docker-registry-addreee>/docker-ptf-sai:<TAG_WITH_OS_VERSION>
    ```
    > For the setup of ptf-sai docker, it similiar with this section [Setup Docker Registry for docker-ptf](https://github.com/Azure/sonic-mgmt/blob/master/docs/testbed/README.testbed.Setup.md#setup-docker-registry-for-docker-ptf). But here, we need to use `docker-ptf-sai`.

2. Add docker registry for sonic-mgmt
   sonic-mgmt will try to pull the dependent ptf docker during the deployment process, we need to use the local docker registery here:
    ```
    # Edit file <local_folder>/sonic-mgmt/ansible/vars/docker_registry.yml with your local docker reigstry
    docker_registry_host: <docker-reigstry>:<port>
    ```

3. Deploy SAI Test Topology With SONiC-MGMT
    
    For the detailed steps please refer to [Deploy SAI Test Topology With SONiC-MGMT](DeploySAITestTopologyWithSONiC-MGMT.md)

    After setup the SONiC-MGMT env, we can use the command to setup the topology.
    ```
    /data/<repo_sonic-mgmt>/testbed-cli.sh -t testbed.yaml add-topo <config_name> password.txt
    ```

### Setup DUT (Device under testing)
*In this section, we will introduce how to setup the saiserverv2 docker in DUT.*
1. Stop all the other services besides `database`, which might impact PTF-SAIv2 testing. (Recommended)
 
   You may activate some services according to your scenario, but please be sure to stop `swss` and `syncd`.
    ```shell
    services=("swss" "syncd" "radv" "lldp" "dhcp_relay" "teamd" "bgp" "pmon" "telemetry" "acms" "snmp")
    stop_service(){
        for serv in ${services[*]}; do
            echo "stop service: [$serv]."
            sudo systemctl stop $serv
        done
    }
    stop_service
    ```
3. Upload the saiserverv2 docker you built from the previous section to your DUT or Pull saiserverv2 docker image from the registry.

4. Start your saiserver binary from saiserverv2 docker:
    
    After successfully starting the saiserver binary, we can get those outputs from the shell:
    ```
    admin@s6000:~$ usr/sbin/saiserver -p /etc/sai.d/sai.profile -f /usr/share/sonic/hwsku/port_config.ini 

    profile map file: /usr/share/sonic/hwsku/sai.profile 

    port map file: /usr/share/sonic/hwsku/port_config.ini 

    insert: SAI_INIT_CONFIG_FILE:/usr/share/sonic/hwsku/td2-s6000-32x40G.config.bcm 

    insert: SAI_NUM_ECMP_MEMBERS:32 

    Starting SAI RPC server on port 9092 
    ```

### Setup ptf-sai docker and run test
*In the last section, we will setup our testing environment and run a sanity test on PTF side.*

1. Log in to the ptf-sai docker, you can find the IP address of docker which is connected to the DUT in [testbed.yaml](https://github.com/Azure/sonic-mgmt/blob/master/ansible/testbed.yaml).  

2. Make sure Github is accessible on ptf-sai docker and download the SAI repo which contains PTF-SAIv2 test cases 
    ```
    rm -rf ./SAI
    git clone https://github.com/opencomputeproject/SAI.git
    cd SAI
    git master v1.9
    ```

3. Install the sai python header `python-saithriftv2_0.9.4_amd64.deb` into ptf-sai docker.
    ```
    # install the deb package into ptf-sai docker
    dpkg -i python-saithriftv2_0.9.4_amd64.deb          
    ```

4. Start PTF-SAIv2 testing within ptf-sai docker
    ```shell
    # set the platform name
    export PLATFORM=<vendor name>

    # run a sanitytest
    ptf --test-dir ptf saisanity.L2SanityTest --interface '<Port_index@eth_name>' -t "thrift_server='<DUT ip address>'"

    # use a broadcom switch with 32-port as an example 
   export PLATFORM=brcm
   ptf --test-dir /tmp/SAI/ptf saisanity.L2SanityTest --interface '0@eth0' --interface '1@eth1' --interface '2@eth2' --interface '3@eth3' --interface '4@eth4' --interface '5@eth5' --interface '6@eth6' --interface '7@eth7' --interface '8@eth8' --interface '9@eth9' --interface '10@eth10' --interface '11@eth11' --interface '12@eth12' --interface '13@eth13' --interface '14@eth14' --interface '15@eth15' --interface '16@eth16' --interface '17@eth17' --interface '18@eth18' --interface '19@eth19' --interface '20@eth20' --interface '21@eth21' --interface '22@eth22' --interface '23@eth23' --interface '24@eth24' --interface '25@eth25' --interface '26@eth26' --interface '27@eth27' --interface '28@eth28' --interface '29@eth29' --interface '30@eth30' --interface '31@eth31' "--test-params=thrift_server='<DUT ip address>'"
    ```

Specification for parameter ``--interface '<Port_index@eth_name>'``
- Port_index
```shell
# check local interfaces
> ifconfig
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 9216
...

eth1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 9216
...
```
- eth_name
```python
# eth0, eth1 ... are the eth_name
# Port_index will be used in test cases like
# If we have parameter 1@eth1, then 1 will map to eth1
send_packet(self, 1, pkt)
```

Finally, we can see the result as shown below:

```
Using packet manipulation module: ptf.packet_scapy 

saisanity.L2SanityTest ... Waiting for the switch to get ready, 5 seconds ... 

...

Check port31 forwarding... 

ok 

---------------------------------------------------------------------- 

Ran 1 test in 21.184s 
 

OK 
```

## Reference

* [SAI PTF introduction and manually setup Testbed](ManuallySetupTestbedGuide.md)
* [sonic-buildimage user guide](https://github.com/Azure/sonic-buildimage)
* [Deploy SAI Test Topology With SONiC-MGMT](DeploySAITestTopologyWithSONiC-MGMT.md)
* [Setup Docker builder for debugging](SetupDockerBuilderForDebugging.md)
