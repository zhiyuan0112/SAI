from sai_test_base import T0TestBase
from sai_utils import *


class EcmpHashFieldSportTestV4(T0TestBase):
    """
    Verify loadbalance on NexthopGroup ipv4 by source port.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self,
                         is_create_route_for_nhopgrp=True,
                         is_create_route_for_lag=False,
                        )
        
    def test_load_balance_on_sportv4(self):
        """
        1. Generate different packets by updating src port
        2. Send these packets on port1
        3. Check if packets are received on ports of lag1-4 equally
        """
        print("Ecmp l3 load balancing test based on src port")
        max_itrs = 400
        begin_port = 2000
        recv_dev_port_idxs = self.get_dev_port_indexes(
            list(filter(lambda item: item != 1, self.dut.nhp_grpv4_list[0].member_port_indexs)))
        cnt_ports = len(recv_dev_port_idxs)
        rcv_count = [0 for _ in range(cnt_ports)]

        ip_src = self.servers[0][1].ipv4
        ip_dst = self.servers[60][1].ipv4
        for port_index in range(0, max_itrs):
            src_port = begin_port + port_index
            pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                    eth_src=self.servers[1][1].mac,
                                    ip_dst=ip_dst,
                                    ip_src=ip_src,
                                    tcp_sport= src_port,
                                    ip_id=105,
                                    ip_ttl=64)

            exp_pkt1 = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         tcp_sport= src_port,
                                         ip_id=105,
                                         ip_ttl=63)

            exp_pkt2 = simple_tcp_packet(eth_dst=self.t1_list[2][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         tcp_sport= src_port,
                                         ip_id=105,
                                         ip_ttl=63)

            exp_pkt3 = simple_tcp_packet(eth_dst=self.t1_list[3][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         tcp_sport= src_port,
                                         ip_id=105,
                                         ip_ttl=63)

            exp_pkt4 = simple_tcp_packet(eth_dst=self.t1_list[4][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         tcp_sport= src_port,
                                         ip_id=105,
                                         ip_ttl=63)

            send_packet(self, self.dut.port_obj_list[1].dev_port_index, pkt)
            rcv_idx = verify_any_packet_any_port(
                self, [exp_pkt1, exp_pkt2, exp_pkt3, exp_pkt4], recv_dev_port_idxs)
            rcv_count[rcv_idx] += 1

        print(rcv_count)
        for i in range(0, cnt_ports):
            self.assertTrue((rcv_count[i] >= (max_itrs / cnt_ports * 0.8)), "Not all paths are equally balanced")

    def runTest(self):
        self.test_load_balance_on_sportv4()

    def tearDown(self):
        super().tearDown()


class EcmpHashFieldSportTestV6(T0TestBase):
    """
    Verify loadbalance on NexthopGroup ipv6 by source port.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self,
                         is_create_route_for_nhopgrp=True,
                         is_create_route_for_lag=False,
                        )
        
    def test_load_balance_on_sportv6(self):
        """
        1. Generate different packets by updating src port
        2. Send these packets on port1
        3. Check if packets are received on ports of lag1-4 equally
        """
        print("Ecmp l3 load balancing test based on src port")
        max_itrs = 400
        begin_port = 2000
        recv_dev_port_idxs = self.get_dev_port_indexes(
            list(filter(lambda item: item != 1, self.dut.nhp_grpv6_list[0].member_port_indexs)))
        cnt_ports = len(recv_dev_port_idxs)
        rcv_count = [0 for _ in range(cnt_ports)]

        ip_src = self.servers[0][1].ipv6
        ip_dst = self.servers[60][1].ipv6
        for port_index in range(0, max_itrs):
            src_port = begin_port + port_index
            pkt = simple_tcpv6_packet(eth_dst=ROUTER_MAC,
                                      eth_src=self.servers[1][1].mac,
                                      ipv6_dst=ip_dst,
                                      ipv6_src=ip_src,
                                      tcp_sport= src_port,
                                      ipv6_hlim=64)

            exp_pkt1 = simple_tcpv6_packet(eth_dst=self.t1_list[1][100].mac,
                                          eth_src=ROUTER_MAC,
                                          ipv6_dst=ip_dst,
                                          ipv6_src=ip_src,
                                          tcp_sport= src_port,
                                          ipv6_hlim=63)
            
            exp_pkt2 = simple_tcpv6_packet(eth_dst=self.t1_list[2][100].mac,
                                           eth_src=ROUTER_MAC,
                                           ipv6_dst=ip_dst,
                                           ipv6_src=ip_src,
                                           tcp_sport= src_port,
                                           ipv6_hlim=63)

            exp_pkt3 = simple_tcpv6_packet(eth_dst=self.t1_list[3][100].mac,
                                           eth_src=ROUTER_MAC,
                                           ipv6_dst=ip_dst,
                                           ipv6_src=ip_src,
                                           tcp_sport= src_port,
                                           ipv6_hlim=63)
            
            exp_pkt4 = simple_tcpv6_packet(eth_dst=self.t1_list[4][100].mac,
                                           eth_src=ROUTER_MAC,
                                           ipv6_dst=ip_dst,
                                           ipv6_src=ip_src,
                                           tcp_sport= src_port,
                                           ipv6_hlim=63)

            send_packet(self, self.dut.port_obj_list[1].dev_port_index, pkt)
            rcv_idx = verify_any_packet_any_port(
                self, [exp_pkt1, exp_pkt2, exp_pkt3, exp_pkt4], recv_dev_port_idxs)
            rcv_count[rcv_idx] += 1

        print(rcv_count)
        for i in range(0, cnt_ports):
            self.assertTrue((rcv_count[i] >= (max_itrs / cnt_ports * 0.8)), "Not all paths are equally balanced")

    def runTest(self):
        self.test_load_balance_on_sportv6()

    def tearDown(self):
        super().tearDown()


class EcmpHashFieldDportTestV4(T0TestBase):
    """
    Verify loadbalance on NexthopGroup ipv4 by destination port.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self,
                         is_create_route_for_nhopgrp=True,
                         is_create_route_for_lag=False,
                        )
        
    def test_load_balance_on_dportv4(self):
        """
        1. Generate different packets by updating dst port
        2. Send these packets on port1
        3. Check if packets are received on ports of lag1-4 equally
        """
        print("Ecmp l3 load balancing test based on dst port")
        max_itrs = 400
        begin_port = 2000
        recv_dev_port_idxs = self.get_dev_port_indexes(
            list(filter(lambda item: item != 1, self.dut.nhp_grpv4_list[0].member_port_indexs)))
        cnt_ports = len(recv_dev_port_idxs)
        rcv_count = [0 for _ in range(cnt_ports)]

        ip_src = self.servers[0][1].ipv4
        ip_dst = self.servers[60][1].ipv4
        for port_index in range(0, max_itrs):
            dst_port = begin_port + port_index
            pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                    eth_src=self.servers[1][1].mac,
                                    ip_dst=ip_dst,
                                    ip_src=ip_src,
                                    tcp_dport= dst_port,
                                    ip_id=105,
                                    ip_ttl=64)

            exp_pkt1 = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         tcp_dport= dst_port,
                                         ip_id=105,
                                         ip_ttl=63)

            exp_pkt2 = simple_tcp_packet(eth_dst=self.t1_list[2][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         tcp_dport= dst_port,
                                         ip_id=105,
                                         ip_ttl=63)

            exp_pkt3 = simple_tcp_packet(eth_dst=self.t1_list[3][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         tcp_dport= dst_port,
                                         ip_id=105,
                                         ip_ttl=63) 

            exp_pkt4 = simple_tcp_packet(eth_dst=self.t1_list[4][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         tcp_dport= dst_port,
                                         ip_id=105,
                                         ip_ttl=63) 

            send_packet(self, self.dut.port_obj_list[1].dev_port_index, pkt)
            rcv_idx = verify_any_packet_any_port(
                self, [exp_pkt1, exp_pkt2, exp_pkt3, exp_pkt4], recv_dev_port_idxs)
            rcv_count[rcv_idx] += 1

        print(rcv_count)
        for i in range(0, cnt_ports):
            self.assertTrue((rcv_count[i] >= (max_itrs / cnt_ports * 0.8)), "Not all paths are equally balanced")

    def runTest(self):
        self.test_load_balance_on_dportv4()

    def tearDown(self):
        super().tearDown()


class EcmpHashFieldDportTestV6(T0TestBase):
    """
    Verify loadbalance on NexthopGroup ipv6 by destination port.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self,
                         is_create_route_for_nhopgrp=True,
                         is_create_route_for_lag=False,
                        )
        
    def test_load_balance_on_dportv6(self):
        """
        1. Generate different packets by updating dst port
        2. Send these packets on port1
        3. Check if packets are received on ports of lag1-4 equally
        """
        print("Ecmp l3 load balancing test based on dst port")
        max_itrs = 400
        begin_port = 2000
        recv_dev_port_idxs = self.get_dev_port_indexes(
            list(filter(lambda item: item != 1, self.dut.nhp_grpv6_list[0].member_port_indexs)))
        cnt_ports = len(recv_dev_port_idxs)
        rcv_count = [0 for _ in range(cnt_ports)]

        ip_src = self.servers[0][1].ipv6
        ip_dst = self.servers[60][1].ipv6
        for port_index in range(0, max_itrs):
            dst_port = begin_port + port_index
            pkt = simple_tcpv6_packet(eth_dst=ROUTER_MAC,
                                      eth_src=self.servers[1][1].mac,
                                      ipv6_dst=ip_dst,
                                      ipv6_src=ip_src,
                                      tcp_dport= dst_port,
                                      ipv6_hlim=64)

            exp_pkt1 = simple_tcpv6_packet(eth_dst=self.t1_list[1][100].mac,
                                           eth_src=ROUTER_MAC,
                                           ipv6_dst=ip_dst,
                                           ipv6_src=ip_src,
                                           tcp_dport= dst_port,
                                           ipv6_hlim=63)

            exp_pkt2 = simple_tcpv6_packet(eth_dst=self.t1_list[2][100].mac,
                                           eth_src=ROUTER_MAC,
                                           ipv6_dst=ip_dst,
                                           ipv6_src=ip_src,
                                           tcp_dport= dst_port,
                                           ipv6_hlim=63)

            exp_pkt3 = simple_tcpv6_packet(eth_dst=self.t1_list[3][100].mac,
                                           eth_src=ROUTER_MAC,
                                           ipv6_dst=ip_dst,
                                           ipv6_src=ip_src,
                                           tcp_dport= dst_port,
                                           ipv6_hlim=63) 

            exp_pkt4 = simple_tcpv6_packet(eth_dst=self.t1_list[4][100].mac,
                                           eth_src=ROUTER_MAC,
                                           ipv6_dst=ip_dst,
                                           ipv6_src=ip_src,
                                           tcp_dport= dst_port,
                                           ipv6_hlim=63) 

            send_packet(self, self.dut.port_obj_list[1].dev_port_index, pkt)
            rcv_idx = verify_any_packet_any_port(
                self, [exp_pkt1, exp_pkt2, exp_pkt3, exp_pkt4], recv_dev_port_idxs)
            rcv_count[rcv_idx] += 1

        print(rcv_count)
        for i in range(0, cnt_ports):
            self.assertTrue((rcv_count[i] >= (max_itrs / cnt_ports * 0.8)), "Not all paths are equally balanced")

    def runTest(self):
        self.test_load_balance_on_dportv6()

    def tearDown(self):
        super().tearDown()


class EcmpHashFieldSIPTestV4(T0TestBase):
    """
    Verify loadbalance on NexthopGroup ipv4 by source port.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self,
                         is_create_route_for_nhopgrp=True,
                         is_create_route_for_lag=False,
                        )
        
    def test_load_balance_on_sipv4(self):
        """
        1. Generate different packets by updating src ip (192.168.0.1-192.168.0.10)
        2. Send these packets on port1
        3. Check if packets are received on ports of lag1-4 equally
        """
        print("Ecmp l3 load balancing test based on src ip")
        max_itrs = 400
        recv_dev_port_idxs = self.get_dev_port_indexes(
            list(filter(lambda item: item != 1, self.dut.nhp_grpv4_list[0].member_port_indexs)))
        cnt_ports = len(recv_dev_port_idxs)
        rcv_count = [0 for _ in range(cnt_ports)]

        ip_dst = self.servers[60][1].ipv4
        for index in range(0, max_itrs):
            ip_index = index % 10
            ip_src = self.servers[0][ip_index+1].ipv4
            pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                    eth_src=self.servers[1][1].mac,
                                    ip_dst=ip_dst,
                                    ip_src=ip_src,
                                    ip_id=105,
                                    ip_ttl=64)

            exp_pkt1 = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         ip_id=105,
                                         ip_ttl=63)

            exp_pkt2 = simple_tcp_packet(eth_dst=self.t1_list[2][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         ip_id=105,
                                         ip_ttl=63)

            exp_pkt3 = simple_tcp_packet(eth_dst=self.t1_list[3][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         ip_id=105,
                                         ip_ttl=63) 

            exp_pkt4 = simple_tcp_packet(eth_dst=self.t1_list[4][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         ip_id=105,
                                         ip_ttl=63) 

            send_packet(self, self.dut.port_obj_list[1].dev_port_index, pkt)
            rcv_idx = verify_any_packet_any_port(
                self, [exp_pkt1, exp_pkt2, exp_pkt3, exp_pkt4], recv_dev_port_idxs)
            rcv_count[rcv_idx] += 1

        print(rcv_count)
        for i in range(0, cnt_ports):
            self.assertTrue((rcv_count[i] >= (max_itrs / cnt_ports * 0.8)), "Not all paths are equally balanced")

    def runTest(self):
        self.test_load_balance_on_sipv4()

    def tearDown(self):
        super().tearDown()


class EcmpHashFieldSIPTestV6(T0TestBase):
    """
    Verify loadbalance on NexthopGroup ipv6 by source port.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self,
                         is_create_route_for_nhopgrp=True,
                         is_create_route_for_lag=False,
                        )
        
    def test_load_balance_on_sipv6(self):
        """
        1. Generate different packets by updating src ip (192.168.0.1-192.168.0.10)
        2. Send these packets on port1
        3. Check if packets are received on ports of lag1-4 equally
        """
        print("Ecmp l3 load balancing test based on src ip")
        max_itrs = 400
        recv_dev_port_idxs = self.get_dev_port_indexes(
            list(filter(lambda item: item != 1, self.dut.nhp_grpv6_list[0].member_port_indexs)))
        cnt_ports = len(recv_dev_port_idxs)
        rcv_count = [0 for _ in range(cnt_ports)]

        ip_dst = self.servers[60][1].ipv6
        for index in range(0, max_itrs):
            ip_index = index % 10
            ip_src = self.servers[0][ip_index+1].ipv6
            pkt = simple_tcpv6_packet(eth_dst=ROUTER_MAC,
                                      eth_src=self.servers[1][1].mac,
                                      ipv6_dst=ip_dst,
                                      ipv6_src=ip_src,
                                      ipv6_hlim=64)

            exp_pkt1 = simple_tcpv6_packet(eth_dst=self.t1_list[1][100].mac,
                                           eth_src=ROUTER_MAC,
                                           ipv6_dst=ip_dst,
                                           ipv6_src=ip_src,
                                           ipv6_hlim=63)

            exp_pkt2 = simple_tcpv6_packet(eth_dst=self.t1_list[2][100].mac,
                                           eth_src=ROUTER_MAC,
                                           ipv6_dst=ip_dst,
                                           ipv6_src=ip_src,
                                           ipv6_hlim=63)

            exp_pkt3 = simple_tcpv6_packet(eth_dst=self.t1_list[3][100].mac,
                                           eth_src=ROUTER_MAC,
                                           ipv6_dst=ip_dst,
                                           ipv6_src=ip_src,
                                           ipv6_hlim=63) 

            exp_pkt4 = simple_tcpv6_packet(eth_dst=self.t1_list[4][100].mac,
                                           eth_src=ROUTER_MAC,
                                           ipv6_dst=ip_dst,
                                           ipv6_src=ip_src,
                                           ipv6_hlim=63) 

            send_packet(self, self.dut.port_obj_list[1].dev_port_index, pkt)
            rcv_idx = verify_any_packet_any_port(
                self, [exp_pkt1, exp_pkt2, exp_pkt3, exp_pkt4], recv_dev_port_idxs)
            rcv_count[rcv_idx] += 1

        print(rcv_count)
        for i in range(0, cnt_ports):
            self.assertTrue((rcv_count[i] >= (max_itrs / cnt_ports * 0.8)), "Not all paths are equally balanced")

    def runTest(self):
        self.test_load_balance_on_sipv6()

    def tearDown(self):
        super().tearDown()


"""
Skip test for broadcom, can't load balance on protocol such as tcp and udp. Item: 15023123
"""

class EcmpHashFieldProtoTestV4(T0TestBase):
    """
    Verify loadbalance on NexthopGroup ipv4 by protocol.
    """
    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self,
                         is_create_route_for_nhopgrp=True,
                         is_create_route_for_lag=False,
                         skip_reason ="SKIP! Skip test for broadcom, can't load balance on protocol such as tcp and udp. Item: 15023123",
                        )
        
    def test_load_balance_on_protocolv4(self):
        """
        1. Generate different packets with tcp and udp
        2. Send these packets on port1
        3. Check if packets are received on ports of lag1-4 equally
        """
        print("Ecmp l3 load balancing test based on protocol")
        max_itrs = 400
        recv_dev_port_idxs = self.get_dev_port_indexes(
            list(filter(lambda item: item != 1, self.dut.nhp_grpv4_list[0].member_port_indexs)))
        cnt_ports = len(recv_dev_port_idxs)
        rcv_count = [0 for _ in range(cnt_ports)]

        ip_src = self.servers[0][1].ipv4
        ip_dst = self.servers[60][1].ipv4
        for index in range(0, max_itrs):
            if index % 2 == 0:
                pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                        eth_src=self.servers[1][1].mac,
                                        ip_dst=ip_dst,
                                        ip_src=ip_src,
                                        ip_id=105,
                                        ip_ttl=64)

                exp_pkt1 = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                             eth_src=ROUTER_MAC,
                                             ip_dst=ip_dst,
                                             ip_src=ip_src,
                                             ip_id=105,
                                             ip_ttl=63)

                exp_pkt2 = simple_tcp_packet(eth_dst=self.t1_list[2][100].mac,
                                             eth_src=ROUTER_MAC,
                                             ip_dst=ip_dst,
                                             ip_src=ip_src,
                                             ip_id=105,
                                             ip_ttl=63)

                exp_pkt3 = simple_tcp_packet(eth_dst=self.t1_list[3][100].mac,
                                             eth_src=ROUTER_MAC,
                                             ip_dst=ip_dst,
                                             ip_src=ip_src,
                                             ip_id=105,
                                             ip_ttl=63) 

                exp_pkt4 = simple_tcp_packet(eth_dst=self.t1_list[4][100].mac,
                                             eth_src=ROUTER_MAC,
                                             ip_dst=ip_dst,
                                             ip_src=ip_src,
                                             ip_id=105,
                                             ip_ttl=63) 
            else:
                pkt = simple_udp_packet(eth_dst=ROUTER_MAC,
                                        eth_src=self.servers[1][1].mac,
                                        ip_dst=ip_dst,
                                        ip_src=ip_src,
                                        ip_id=105,
                                        ip_ttl=64)

                exp_pkt1 = simple_udp_packet(eth_dst=self.t1_list[1][100].mac,
                                             eth_src=ROUTER_MAC,
                                             ip_dst=ip_dst,
                                             ip_src=ip_src,
                                             ip_id=105,
                                             ip_ttl=63)

                exp_pkt2 = simple_udp_packet(eth_dst=self.t1_list[2][100].mac,
                                             eth_src=ROUTER_MAC,
                                             ip_dst=ip_dst,
                                             ip_src=ip_src,
                                             ip_id=105,
                                             ip_ttl=63)

                exp_pkt3 = simple_udp_packet(eth_dst=self.t1_list[3][100].mac,
                                             eth_src=ROUTER_MAC,
                                             ip_dst=ip_dst,
                                             ip_src=ip_src,
                                             ip_id=105,
                                             ip_ttl=63) 

                exp_pkt4 = simple_udp_packet(eth_dst=self.t1_list[4][100].mac,
                                             eth_src=ROUTER_MAC,
                                             ip_dst=ip_dst,
                                             ip_src=ip_src,
                                             ip_id=105,
                                             ip_ttl=63) 

            send_packet(self, self.dut.port_obj_list[1].dev_port_index, pkt)
            rcv_idx = verify_any_packet_any_port(
                self, [exp_pkt1, exp_pkt2, exp_pkt3, exp_pkt4], recv_dev_port_idxs)
            rcv_count[rcv_idx] += 1

        print(rcv_count)
        for i in range(0, cnt_ports):
            self.assertTrue((rcv_count[i] >= (max_itrs / cnt_ports * 0.8)), "Not all paths are equally balanced")

    def runTest(self):
        self.test_load_balance_on_protocolv4()

    def tearDown(self):
        super().tearDown()


"""
Skip test for broadcom, can't load balance on protocol such as tcp and udp. Item: 15023123
"""

class EcmpHashFieldProtoTestV6(T0TestBase):
    """
    Verify loadbalance on NexthopGroup ipv6 by protocol.
    """
    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self,
                         is_create_route_for_nhopgrp=True,
                         is_create_route_for_lag=False,
                         skip_reason ="SKIP! Skip test for broadcom, can't load balance on protocol such as tcp and udp. Item: 15023123",
                        )
        
    def test_load_balance_on_protocolv6(self):
        """
        1. Generate different packets with tcp and udp
        2. Send these packets on port1
        3. Check if packets are received on ports of lag1-4 equally
        """
        print("Ecmp l3 load balancing test based on protocol")
        max_itrs = 400
        recv_dev_port_idxs = self.get_dev_port_indexes(
            list(filter(lambda item: item != 1, self.dut.nhp_grpv6_list[0].member_port_indexs)))
        cnt_ports = len(recv_dev_port_idxs)
        rcv_count = [0 for _ in range(cnt_ports)]

        ip_src = self.servers[0][1].ipv6
        ip_dst = self.servers[60][1].ipv6
        for index in range(0, max_itrs):
            if index % 2 == 0:
                pkt = simple_tcpv6_packet(eth_dst=ROUTER_MAC,
                                          eth_src=self.servers[1][1].mac,
                                          ipv6_dst=ip_dst,
                                          ipv6_src=ip_src,
                                          ipv6_hlim=64)

                exp_pkt1 = simple_tcpv6_packet(eth_dst=self.t1_list[1][100].mac,
                                               eth_src=ROUTER_MAC,
                                               ipv6_dst=ip_dst,
                                               ipv6_src=ip_src,
                                               ipv6_hlim=63)

                exp_pkt2 = simple_tcpv6_packet(eth_dst=self.t1_list[2][100].mac,
                                               eth_src=ROUTER_MAC,
                                               ipv6_dst=ip_dst,
                                               ipv6_src=ip_src,
                                               ipv6_hlim=63)

                exp_pkt3 = simple_tcpv6_packet(eth_dst=self.t1_list[3][100].mac,
                                               eth_src=ROUTER_MAC,
                                               ipv6_dst=ip_dst,
                                               ipv6_src=ip_src,
                                               ipv6_hlim=63)

                exp_pkt4 = simple_tcpv6_packet(eth_dst=self.t1_list[4][100].mac,
                                               eth_src=ROUTER_MAC,
                                               ipv6_dst=ip_dst,
                                               ipv6_src=ip_src,
                                               ipv6_hlim=63)
            else:
                pkt = simple_udpv6_packet(eth_dst=ROUTER_MAC,
                                          eth_src=self.servers[1][1].mac,
                                          ipv6_dst=ip_dst,
                                          ipv6_src=ip_src,
                                          ipv6_hlim=64)

                exp_pkt1 = simple_udpv6_packet(eth_dst=self.t1_list[1][100].mac,
                                               eth_src=ROUTER_MAC,
                                               ipv6_dst=ip_dst,
                                               ipv6_src=ip_src,
                                               ipv6_hlim=63)

                exp_pkt2 = simple_udpv6_packet(eth_dst=self.t1_list[2][100].mac,
                                               eth_src=ROUTER_MAC,
                                               ipv6_dst=ip_dst,
                                               ipv6_src=ip_src,
                                               ipv6_hlim=63)

                exp_pkt3 = simple_udpv6_packet(eth_dst=self.t1_list[3][100].mac,
                                               eth_src=ROUTER_MAC,
                                               ipv6_dst=ip_dst,
                                               ipv6_src=ip_src,
                                               ipv6_hlim=63)

                exp_pkt4 = simple_udpv6_packet(eth_dst=self.t1_list[4][100].mac,
                                               eth_src=ROUTER_MAC,
                                               ipv6_dst=ip_dst,
                                               ipv6_src=ip_src,
                                               ipv6_hlim=63)

            send_packet(self, self.dut.port_obj_list[1].dev_port_index, pkt)
            rcv_idx = verify_any_packet_any_port(
                self, [exp_pkt1, exp_pkt2, exp_pkt3, exp_pkt4], recv_dev_port_idxs)
            rcv_count[rcv_idx] += 1

        print(rcv_count)
        for i in range(0, cnt_ports):
            self.assertTrue((rcv_count[i] >= (max_itrs / cnt_ports * 0.8)), "Not all paths are equally balanced")

    def runTest(self):
        self.test_load_balance_on_protocolv6()

    def tearDown(self):
        super().tearDown()


class IngressNoDiffTestV4(T0TestBase):
    """
    Verify if different ingress ports will not impact the loadbalance (not change to other egress ports).
    """
    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self,
                         is_create_route_for_nhopgrp=True,
                         is_create_route_for_lag=False,
                        )
        
    def test_ingress_no_diff(self):
        """
        1. Generate Packets, with ``SIP:192.168.0.1`` ``DIP:192.168.60.1`` to match the exiting config
        2. Check vlan interface(svi added)
        3. Send packets from Port5 - Port8
        4. Verify packet received on a certain LAG's member, with corresponding SIP, DIP, and ``SMAC: SWITCH_MAC``
        5. Generate Packets, with ``SIP:192.168.0.1`` ``DIP:192.168.60.2``
        6. Send packets from Port5 - Port8
        7. Verify packet received on a certain LAG's member but different from step4
        """
        print("Ecmp l3 ingress no diff test")

        ip_src = self.servers[0][1].ipv4
        ip_dst1 = self.servers[60][1].ipv4
        ip_dst2 = self.servers[60][2].ipv4

        pkt1 = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                 eth_src=self.servers[1][1].mac,
                                 ip_dst=ip_dst1,
                                 ip_src=ip_src,
                                 ip_id=105,
                                 ip_ttl=64)
        exp_pkt1 = simple_tcp_packet(eth_dst=self.t1_list[3][100].mac,
                                     eth_src=ROUTER_MAC,
                                     ip_dst=ip_dst1,
                                     ip_src=ip_src,
                                     ip_id=105,
                                     ip_ttl=63)

        pkt2 = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                 eth_src=self.servers[1][1].mac,
                                 ip_dst=ip_dst2,
                                 ip_src=ip_src,
                                 ip_id=105,
                                 ip_ttl=64)
        exp_pkt2 = simple_tcp_packet(eth_dst=self.t1_list[2][100].mac,
                                     eth_src=ROUTER_MAC,
                                     ip_dst=ip_dst2,
                                     ip_src=ip_src,
                                     ip_id=105,
                                     ip_ttl=63)
        
        exp_port_idx1 = -1
        exp_port_idx2 = -1
        recv_dev_port_idxs = self.get_dev_port_indexes(
            list(filter(lambda item: item != 1, self.dut.nhp_grpv4_list[0].member_port_indexs)))
        
        for i in range(5, 9):
            # step 4
            send_packet(self, self.dut.port_obj_list[i].dev_port_index, pkt1)
            if exp_port_idx1 == -1:
                exp_port_idx1, _ = verify_packet_any_port(self, exp_pkt1, recv_dev_port_idxs)
            else:
                verify_packet(self, exp_pkt1, recv_dev_port_idxs[exp_port_idx1])

            # step 6
            send_packet(self, self.dut.port_obj_list[i].dev_port_index, pkt2)
            if exp_port_idx2 == -1:
                exp_port_idx2, _ = verify_packet_any_port(self, exp_pkt2, recv_dev_port_idxs)
            else:
                verify_packet(self, exp_pkt2, recv_dev_port_idxs[exp_port_idx2])
            
            # step 7
            self.assertTrue(exp_port_idx1 != exp_port_idx2, "Recived packets from the same port")
    
    def runTest(self):
        self.test_ingress_no_diff()

    def tearDown(self):
        super().tearDown()


class RemoveLagEcmpTestV4(T0TestBase):
    """
    When remove nexthop member, we expect traffic drop on the removed nexthop member.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self,
                         is_create_route_for_nhopgrp=True,
                         is_create_route_for_lag=False,
                        )
        self.route_configer.remove_nhop_member_by_lag_idx(
            nhp_grp_obj=self.dut.nhp_grpv4_list[0], lag_idx=3)
        
    def test_lag_ecmp_remove(self):
        """
        1. Remove the next hop from next-hop group in test_ecmp: next-hop with IP ``DIP:10.1.3.100`` on LAG3 
        2. Generate Packets, with different source IPs as ``SIP:192.168.0.1-192.168.0.10`` 
        3. Change other elements in the packets, including ``DIP:192.168.60.1`` ``L4_port``
        4. Verify Packets only can be received on LAG1 and LAG2, with ``SMAC: SWITCH_MAC_2`` (check loadbalanced in LAG and ECMP)
        """
        print("Ecmp remove lag test")

        ip_dst = self.servers[60][1].ipv4
        recv_dev_port_idxs = self.get_dev_port_indexes(
            list(filter(lambda item: item != 1, self.dut.nhp_grpv4_list[0].member_port_indexs)))
        pkts_num = 10
        for index in range(pkts_num):
            ip_src = self.servers[0][index + 1].ipv4
            
            pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                    eth_src=self.servers[1][1].mac,
                                    ip_dst=ip_dst,
                                    ip_src=ip_src,
                                    ip_id=105,
                                    ip_ttl=64)
            
            exp_pkt1 = simple_tcp_packet(eth_dst=self.t1_list[1][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         ip_id=105,
                                         ip_ttl=63)
            exp_pkt2 = simple_tcp_packet(eth_dst=self.t1_list[2][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         ip_id=105,
                                         ip_ttl=63)
            exp_pkt3 = simple_tcp_packet(eth_dst=self.t1_list[4][100].mac,
                                         eth_src=ROUTER_MAC,
                                         ip_dst=ip_dst,
                                         ip_src=ip_src,
                                         ip_id=105,
                                         ip_ttl=63)

            send_packet(self, self.dut.port_obj_list[1].dev_port_index, pkt)
            verify_any_packet_any_port(self, [exp_pkt1, exp_pkt2, exp_pkt3], recv_dev_port_idxs)

    def runTest(self):
        self.test_lag_ecmp_remove()

    def tearDown(self):
        self.route_configer.create_nhop_member_by_lag_port_idxs(
            nhp_grp_obj=self.dut.nhp_grpv4_list[0], lag_idx=3)
        super().tearDown()


class EcmpReuseLagNexthopTestV4(T0TestBase):
    """
    Verify the lags route can work when ecmp reuse lags' nexthop.
    """

    def setUp(self):
        """
        Test the basic setup process
        """
        T0TestBase.setUp(self,
                         is_create_route_for_nhopgrp=True,
                         is_create_route_for_lag=False,
                         is_reuse_lag_nhop=True,
                        )
        
    def test_ecmp_reuse_lag_nexthop(self):
        """
        1. make sure the route for ip subnet 192.168.60.0/24 and other lags routes 192.168.11.0/24 ~ 192.168.14.0/24 route are coexist (use the same nexthop)
        2. send packet within 192.168.60.0/24
        3. Verify received packet on LAG1~4 members
        4. Send packets within 192.168.11.0/24 ~ 192.168.14.0/24, respectively
        5. Verify Received packet belong to each LAG respectively
        """
        print("Reuse lag's nexthop")
        
        src_dev = self.servers[0][0]
        dst_dev = self.servers[60][0]
        recv_dev_port_idxs = self.get_dev_port_indexes(
            list(filter(lambda item: item != 1, self.dut.nhp_grpv4_list[0].member_port_indexs)))
        cnt_ports = len(recv_dev_port_idxs)
        rcv_count = [0 for _ in range(cnt_ports)]
        
        max_itrs = 400
        begin_port = 2000
        for port_index in range(0, max_itrs):
            src_port = begin_port + port_index
            pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                    eth_src=self.servers[1][1].mac,
                                    ip_dst=dst_dev.ipv4,
                                    ip_src=src_dev.ipv4,
                                    tcp_sport= src_port,
                                    ip_id=105,
                                    ip_ttl=64)

            exp_pkts = []
            for index in range(4):
                exp_pkt = simple_tcp_packet(eth_dst=self.t1_list[index + 1][100].mac,
                                    eth_src=ROUTER_MAC,
                                    ip_dst=dst_dev.ipv4,
                                    ip_src=src_dev.ipv4,
                                    tcp_sport= src_port,
                                    ip_id=105,
                                    ip_ttl=63)
                exp_pkts.append(exp_pkt)

            send_packet(self, self.dut.port_obj_list[1].dev_port_index, pkt)
            rcv_idx = verify_any_packet_any_port(self, exp_pkts, recv_dev_port_idxs)
            rcv_count[rcv_idx] += 1
        
        print(rcv_count)
        for i in range(0, cnt_ports):
            self.assertTrue((rcv_count[i] >= (max_itrs / cnt_ports * 0.8)), "Not all paths are equally balanced")
        print("Received packet on LAG1~4 members")
        
        print("Send packets within 192.168.11.0/24 ~ 192.168.14.0/24, respectively")
        for index in range(11, 15):
            dst_dev = self.servers[index][0]
            port_index = index - 11
            src_port = begin_port + port_index
            pkt = simple_tcp_packet(eth_dst=ROUTER_MAC,
                                    eth_src=self.servers[1][1].mac,
                                    ip_dst=dst_dev.ipv4,
                                    ip_src=src_dev.ipv4,
                                    tcp_sport= src_port,
                                    ip_id=105,
                                    ip_ttl=64)
            exp_pkt = simple_tcp_packet(eth_dst=self.t1_list[index-10][100].mac,
                                        eth_src=ROUTER_MAC,
                                        ip_dst=dst_dev.ipv4,
                                        ip_src=src_dev.ipv4,
                                        tcp_sport= src_port,
                                        ip_id=105,
                                        ip_ttl=63)
            send_packet(self, self.dut.port_obj_list[1].dev_port_index, pkt)
            recv_port_idxs = port_index * 2
            verify_any_packet_any_port(self, exp_pkt, recv_dev_port_idxs[recv_port_idxs:recv_port_idxs+2])

    def runTest(self):
        self.test_ecmp_reuse_lag_nexthop()

    def tearDown(self):
        super().tearDown()
