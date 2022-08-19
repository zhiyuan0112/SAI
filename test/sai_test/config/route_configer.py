# Copyright (c) 2021 Microsoft Open Technologies, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#    THIS CODE IS PROVIDED ON AN *AS IS* BASIS, WITHOUT WARRANTIES OR
#    CONDITIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT
#    LIMITATION ANY IMPLIED WARRANTIES OR CONDITIONS OF TITLE, FITNESS
#    FOR A PARTICULAR PURPOSE, MERCHANTABILITY OR NON-INFRINGEMENT.
#
#    See the Apache Version 2.0 License for specific language governing
#    permissions and limitations under the License.
#
#    Microsoft would like to thank the following companies for their review and
#    assistance with these files: Intel Corporation, Mellanox Technologies Ltd,
#    Dell Products, L.P., Facebook, Inc., Marvell International Ltd.
#
#


from sai_thrift.sai_adapter import *
from sai_utils import *  # pylint: disable=wildcard-import; lgtm[py/polluting-import]
from constant import *  # pylint: disable=wildcard-import; lgtm[py/polluting-import]
from typing import TYPE_CHECKING

from data_module.device import Device
from data_module.vlan import Vlan
from data_module.lag import Lag
from typing import Dict, List

from data_module.nexthop import Nexthop

if TYPE_CHECKING:
    from sai_test_base import T0TestBase


def t0_route_config_helper(test_obj: 'T0TestBase', is_create_default_route=True, is_create_default_loopback_interface=False, is_create_route_for_lag=True):
    """
    Make t0 route configurations base on the configuration in the test plan.
    Set the configuration in test directly.

    Set the following test_obj attributes:
        int: default_vrf
        port_rif_list[0]
        default_ipv6_route_entry
        default_ipv4_route_entry
        neighbor and route for lag
    """
    route_configer = RouteConfiger(test_obj)
    if is_create_default_route:
        route_configer.create_default_route()
        route_configer.create_router_interface_by_port_idx(port_idx=0)

    if is_create_default_loopback_interface:
        route_configer.create_default_loopback_interface()

    if is_create_route_for_lag:
        test_obj.servers[11][0].ip_prefix = '24'
        test_obj.servers[11][0].ip_prefix_v6 = '112'
        route_configer.create_neighbor_by_lag(
            nexthop_device=test_obj.t1_list[1][100], lag=test_obj.dut.lag1)
        route_configer.create_route_path_by_nexthop_from_lag(
            dest_device=test_obj.servers[11][0],
            nexthop_device=test_obj.t1_list[1][100],
            lag=test_obj.dut.lag1)

        test_obj.servers[12][0].ip_prefix = '24'
        test_obj.servers[12][0].ip_prefix_v6 = '112'
        route_configer.create_neighbor_by_lag(
            nexthop_device=test_obj.t1_list[2][100], lag=test_obj.dut.lag2)
        route_configer.create_route_path_by_nexthop_from_lag(
            dest_device=test_obj.servers[12][0],
            nexthop_device=test_obj.t1_list[2][100],
            lag=test_obj.dut.lag2)

        test_obj.servers[13][0].ip_prefix = '24'
        test_obj.servers[13][0].ip_prefix_v6 = '112'
        route_configer.create_neighbor_by_lag(
            nexthop_device=test_obj.t1_list[3][100], lag=test_obj.dut.lag3)
        route_configer.create_route_path_by_nexthop_from_lag(
            dest_device=test_obj.servers[13][0],
            nexthop_device=test_obj.t1_list[3][100],
            lag=test_obj.dut.lag3)

        route_configer.create_nexthop_group_by_nexthops()

class RouteConfiger(object):
    """
    Class use to make all the route configurations.
    """

    def __init__(self, test_obj: 'T0TestBase') -> None:
        """
        Init Route configer.

        Args:
            test_obj: the test object
        """
        self.test_obj = test_obj
        self.client = test_obj.client

    def create_default_route(self):
        self.get_default_virtual_router()
        self.create_default_v4_v6_route_entry()

    def get_default_virtual_router(self):
        """
        Get default virtual_router_id
        """
        print("Get default virtual router id...")
        attr = sai_thrift_get_switch_attribute(
            self.client, default_virtual_router_id=True)
        self.test_obj.assertNotEqual(attr['default_virtual_router_id'], 0)
        self.test_obj.dut.default_vrf = attr['default_virtual_router_id']

    def create_default_loopback_interface(self):
        """
        Create loopback interface on default virtual router.
        """
        self.test_obj.dut.loopback_intf = sai_thrift_create_router_interface(self.client,
                                                                             type=SAI_ROUTER_INTERFACE_TYPE_LOOPBACK, virtual_router_id=self.test_obj.dut.default_vrf)
        self.test_obj.assertEqual(self.test_obj.status(), SAI_STATUS_SUCCESS)

    def create_default_v4_v6_route_entry(self):
        """
        Create default v4 and v6 route entry.
        """

        print("Create default v4&v6 route entry...")
        v6_default = sai_thrift_ip_prefix_t(addr_family=1,
                                            addr=sai_thrift_ip_addr_t(
                                                ip6=DEFAULT_IP_V6_PREFIX),
                                            mask=sai_thrift_ip_addr_t(ip6=DEFAULT_IP_V6_PREFIX))
        self.test_obj.dut.default_ipv6_route_entry = sai_thrift_route_entry_t(vr_id=self.test_obj.dut.default_vrf,
                                                                              destination=v6_default)
        status = sai_thrift_create_route_entry(
            self.client,
            route_entry=self.test_obj.dut.default_ipv6_route_entry,
            packet_action=SAI_PACKET_ACTION_DROP)
        self.test_obj.assertEqual(status, SAI_STATUS_SUCCESS)

        self.test_obj.dut.default_ipv4_route_entry = sai_thrift_route_entry_t(vr_id=self.test_obj.dut.default_vrf,
                                                                              destination=sai_ipprefix(DEFAULT_IP_V4_PREFIX))
        status = sai_thrift_create_route_entry(
            self.client,
            route_entry=self.test_obj.dut.default_ipv4_route_entry,
            packet_action=SAI_PACKET_ACTION_DROP)
        self.test_obj.assertEqual(self.test_obj.status(), SAI_STATUS_SUCCESS)

    def create_route_path_by_nexthop_from_vlan(
            self, dest_device: Device, nexthop_device: Device, vlan: Vlan, virtual_router=None):
        """
        Create a complete route path to a dest_device device, via from nexthop.
        Set vlan attribute: nexthopv4, nexthopv6
        Set device attribute: nexthopv4, nexthopv6
        Set Device attribute: routev4, routev6

        Attrs:
            dest_device: Simulating the destinate device that this dut direct connect to.
            nexthop_device: Simulating the bypass device that the packet will be forwarded to.
            vlan: Vlan in the path
            virtual_router_id: virtual route id, if not defined, will use default route

        Return: routev4, routev6, nhopv4, nhopv6
        """
        nhopv4, nhopv6 = self.create_nexthop_by_vlan(
            vlan, nexthop_device, virtual_router)
        routev4, routev6 = self.create_route_path_by_nexthop(
            dest_device, nhopv4, nhopv6, virtual_router)
        return routev4, routev6, nhopv4, nhopv6

    def create_route_path_by_nexthop_from_lag(
            self, dest_device: Device, nexthop_device: Device, lag: Lag, virtual_router=None):
        """
        Create a complete route path to a dest_device device, via from nexthop.
        Set dut attribute: nexthopv4_list, nexthopv6_list
        Set vlan attribute: nexthopv4, nexthopv6
        Set device attribute: nexthopv4, nexthopv6
        Set Device attribute: routev4, routev6

        Attrs:
            dest_device: Simulating the destinate device that this dut direct connect to.
            nexthop_device: Simulating the bypass device that the packet will be forwarded to.
            lag: lag in the path
            virtual_router_id: virtual route id, if not defined, will use default route

        Return: routev4, routev6, nhopv4, nhopv6
        """
        nhopv4, nhopv6 = self.create_nexthop_by_lag(
            lag, nexthop_device, virtual_router)
        routev4, routev6 = self.create_route_path_by_nexthop(
            dest_device, nhopv4, nhopv6, virtual_router)
        return routev4, routev6, nhopv4, nhopv6

    def create_route_path_by_nexthop_from_port(
            self, dest_device: Device, nexthop_device: Device, port_idx, virtual_router=None):
        """
        Create a complete route path to a dest_device device, via from nexthop.
        Set dut attribute: nexthopv4_list, nexthopv6_list, port_nhop_v4_list, port_nhop_v6_list
        Set vlan attribute: nexthopv4, nexthopv6
        Set device attribute: nexthopv4, nexthopv6
        Set Device attribute: routev4, routev6

        Attrs:
            dest_device: Simulating the destinate device that this dut direct connect to.
            nexthop_device: Simulating the bypass device that the packet will be forwarded to.
            port_idx: port_idx in the path
            virtual_router_id: virtual route id, if not defined, will use default route

        Return: routev4, routev6, nhopv4, nhopv6
        """
        nhopv4, nhopv6 = self.create_nexthop_by_port_idx(
            port_idx, nexthop_device, virtual_router)
        routev4, routev6 = self.create_route_path_by_nexthop(
            dest_device, nhopv4, nhopv6, virtual_router)
        return routev4, routev6, nhopv4, nhopv6

    def create_route_path_by_nexthop_from_bridge_port(
            self, dest_device: Device, nexthop_device: Device, bridge_port_idx, virtual_router=None):
        """
        Create a complete route path to a dest_device device, via from nexthop.
        Set dut attribute: nexthopv4_list, nexthopv6_list, bridge_port_nhop_v4_list, bridge_port_nhop_v6_list
        Set vlan attribute: nexthopv4, nexthopv6
        Set device attribute: nexthopv4, nexthopv6
        Set Device attribute: routev4, routev6

        Attrs:
            dest_device: Simulating the destinate device that this dut direct connect to.
            nexthop_device: Simulating the bypass device that the packet will be forwarded to.
            bridge_port_idx: bridge_port_idx in the path
            virtual_router_id: virtual route id, if not defined, will use default route

        Return: routev4, routev6, nhopv4, nhopv6
        """
        nhopv4, nhopv6 = self.create_nexthop_by_bridge_port_idx(
            bridge_port_idx, nexthop_device, virtual_router)
        routev4, routev6 = self.create_route_path_by_nexthop(
            dest_device, nhopv4, nhopv6, virtual_router)
        return routev4, routev6, nhopv4, nhopv6

    def create_route_path_by_rif_from_lag(
            self, dest_device: Device, lag: Lag, virtual_router=None):
        """
        Create a complete route path from a port device to a dest_device device, via port from route interface.

        Set Device attribute: routev4, routev6

        Attrs:
            dest_device: Simulating the destinate device that this dut direct connect to.
            lag: Lag interface for the route
            virtual_router_id: virtual route id, if not defined, will use default route

        Return: routev4, routev6, rif
        """
        rif = self.create_router_interface_by_lag(
            lag, virtual_router=virtual_router)
        routev4, routev6 = self.create_route_path_by_rif(
            dest_device=dest_device, rif=rif, virtual_router=virtual_router)
        return routev4, routev6, rif

    def create_route_path_by_rif_from_port(
            self, dest_device: Device, port_idx, virtual_router=None):
        """
        Create a complete route path from a port device to a dest_device device, via port from route interface.

        Set Device attribute: routev4, routev6

        Attrs:
            dest_device: Simulating the destinate device that this dut direct connect to.
            port_idx: port_idx
            virtual_router_id: virtual route id, if not defined, will use default route

        Return: routev4, routev6, rif
        """
        rif = self.create_router_interface_by_port_idx(
            port_idx, virtual_router=virtual_router)
        routev4, routev6 = self.create_route_path_by_rif(
            dest_device=dest_device, rif=rif, virtual_router=virtual_router)
        return routev4, routev6, rif

    def create_route_path_by_rif_from_bridge_port(
            self, dest_device: Device, bridge_port_idx, virtual_router=None):
        """
        Create a complete route path from a port device to a dest_device device, via port from route interface.

        Set Device attribute: routev4, routev6

        Attrs:
            dest_device: Simulating the destinate device that this dut direct connect to.
            bridge_port_idx: bridge_port_idx
            virtual_router_id: virtual route id, if not defined, will use default route

        Return: routev4, routev6, rif
        """
        rif = self.create_router_interface_by_bridge_port_idx(
            bridge_port_idx, virtual_router=virtual_router)
        routev4, routev6 = self.create_route_path_by_rif(
            dest_device=dest_device, rif=rif, virtual_router=virtual_router)
        return routev4, routev6, rif

    def create_route_path_by_rif(
            self, dest_device: Device, rif, virtual_router=None):
        """
        Create a complete route path to a dest_device device, via route interface.

        Set Device attribute: routev4, routev6

        Attrs:
            dest_device: Simulating the destinate device that this dut direct connect to.
            rif: route_interface
            virtual_router_id: virtual route id, if not defined, will use default route

        Return: routev4, routev6
        """
        vr_id = self.choice_virtual_route(virtual_router)
        if dest_device.ip_prefix:
            net_routev4 = sai_thrift_route_entry_t(
                vr_id=vr_id, destination=sai_ipprefix(dest_device.ipv4+'/'+dest_device.ip_prefix))
        else:
            # destination cannot use sai_ipaddress
            net_routev4 = sai_thrift_route_entry_t(
                vr_id=vr_id, destination=sai_ipprefix(dest_device.ipv4+'/32'))
        status = sai_thrift_create_route_entry(
            self.client, net_routev4, next_hop_id=rif)
        self.test_obj.assertEqual(status, SAI_STATUS_SUCCESS)

        if dest_device.ip_prefix_v6:
            net_routev6 = sai_thrift_route_entry_t(
                vr_id=vr_id, destination=sai_ipprefix(dest_device.ipv6+'/'+dest_device.ip_prefix_v6))
        else:
            # destination cannot use sai_ipaddress
            net_routev6 = sai_thrift_route_entry_t(
                vr_id=vr_id, destination=sai_ipprefix(dest_device.ipv6+'/128'))
        status = sai_thrift_create_route_entry(
            self.client, net_routev6, next_hop_id=rif)
        self.test_obj.assertEqual(status, SAI_STATUS_SUCCESS)
        dest_device.routev4 = net_routev4
        dest_device.routev6 = net_routev6
        self.test_obj.dut.routev4_list.append(net_routev4)
        self.test_obj.dut.routev6_list.append(net_routev6)

        return net_routev4, net_routev6

    def create_route_path_by_nexthop(
            self, dest_device: Device, nexthopv4: Nexthop, nexthopv6: Nexthop, virtual_router=None):
        """
        Create a complete route path to a dest_device device, via from nexthop.

        Set Device attribute: routev4, routev6

        Attrs:
            dest_device: Simulating the destinate device that this dut direct connect to.
            nexthopv4: nexthopv4
            nexthopv6: nexthopv6
            virtual_router_id: virtual route id, if not defined, will use default route

        Return: routev4, routev6
        """
        vr_id = self.choice_virtual_route(virtual_router)
        if dest_device.ip_prefix:
            net_routev4 = sai_thrift_route_entry_t(
                vr_id=vr_id, destination=sai_ipprefix(dest_device.ipv4+'/'+dest_device.ip_prefix))
        else:
            # destination cannot use sai_ipaddress
            net_routev4 = sai_thrift_route_entry_t(
                vr_id=vr_id, destination=sai_ipprefix(dest_device.ipv4+'/32'))
        status = sai_thrift_create_route_entry(
            self.client, net_routev4, next_hop_id=nexthopv4.nexthop_id)
        self.test_obj.assertEqual(status, SAI_STATUS_SUCCESS)

        if dest_device.ip_prefix_v6:
            net_routev6 = sai_thrift_route_entry_t(
                vr_id=vr_id, destination=sai_ipprefix(dest_device.ipv6+'/'+dest_device.ip_prefix_v6))
        else:
            # destination cannot use sai_ipaddress
            net_routev6 = sai_thrift_route_entry_t(
                vr_id=vr_id, destination=sai_ipprefix(dest_device.ipv6+'/128'))
        status = sai_thrift_create_route_entry(
            self.client, net_routev6, next_hop_id=nexthopv6.nexthop_id)
        self.test_obj.assertEqual(status, SAI_STATUS_SUCCESS)

        dest_device.routev4 = net_routev4
        dest_device.routev6 = net_routev6
        self.test_obj.dut.routev4_list.append(net_routev4)
        self.test_obj.dut.routev6_list.append(net_routev6)

        return net_routev4, net_routev6

    def create_neighbor_by_vlan(self, nexthop_device: Device, vlan: Vlan, virtual_router=None, no_host=True):
        """
        Create host neighbor vlan route interface, those neighbor are host neighbor.

        Set Device attribtue: local_neighborv4_id, local_neighborv6_id
        Set Dut attribute: neighborv4_list, neighborv6_list

        Attrs:
            nexthop_device: Simulating the bypass device that the packet will be forwarded to.
            vlan: The vlan which will be used as the egress.
            port_idx: The index of the port which will be used as the egress port.
            no_host: Neighbor in no_host (neighbor direct) mode

        return neighborv4, neighborv6
        """
        rif = self.create_router_interface_by_vlan(vlan, virtual_router)
        v4, v6 = self.create_neighbor_by_rif(nexthop_device, rif, no_host)
        return v4, v6

    def create_neighbor_by_lag(self, nexthop_device: Device, lag: Lag, virtual_router=None, no_host=True):
        """
        Create host neighbor lag route interface, those neighbor are host neighbor.

        Set Device attribtue: local_neighborv4_id, local_neighborv6_id
        Set Dut attribute: neighborv4_list, neighborv6_list

        Attrs:
            nexthop_device: Simulating the bypass device that the packet will be forwarded to.
            lag: The lag which will be used as the egress.
            virtual_router_id: virtual route id, if not defined, will use default route
            no_host: Neighbor in no_host (neighbor direct) mode

        return neighborv4, neighborv6
        """
        rif = self.create_router_interface_by_lag(lag, virtual_router)
        v4, v6 = self.create_neighbor_by_rif(nexthop_device, rif, no_host)
        return v4, v6

    def create_neighbor_by_port_idx(self, nexthop_device: Device, port_idx, virtual_router=None, no_host=True):
        """
        Create host neighbor port, those neighbor are host neighbor.

        Set Device attribtue: local_neighborv4_id, local_neighborv6_id
        Set Dut attribute: neighborv4_list, neighborv6_list

        Attrs:
            nexthop_device: Simulating the bypass device that the packet will be forwarded to.
            port_idx: The index of the port which will be used as the egress port.
            virtual_router_id: virtual route id, if not defined, will use default route
            no_host: Neighbor in no_host (neighbor direct) mode

        return neighborv4, neighborv6
        """
        rif = self.create_router_interface_by_port_idx(
            port_idx, virtual_router)
        v4, v6 = self.create_neighbor_by_rif(nexthop_device, rif, no_host)
        return v4, v6

    def create_neighbor_by_bridge_port_idx(self, nexthop_device: Device, bridge_port_idx, virtual_router=None, no_host=True):
        """
        Create host neighbor bridge port, those neighbor are host neighbor.

        Set Device attribtue: local_neighborv4_id, local_neighborv6_id
        Set Dut attribute: neighborv4_list, neighborv6_list

        Attrs:
            nexthop_device: Simulating the bypass device that the packet will be forwarded to.
            bridge_port_idx: The index of the port which will be used as the egress port.
            virtual_router_id: virtual route id, if not defined, will use default route
            no_host: Neighbor in no_host (neighbor direct) mode

        return neighborv4, neighborv6
        """
        rif = self.create_router_interface_by_bridge_port_idx(
            bridge_port_idx, virtual_router)
        v4, v6 = self.create_neighbor_by_rif(nexthop_device, rif, no_host)
        return v4, v6

    def create_neighbor_by_rif(self, nexthop_device: Device, rif, virtual_router=None, no_host=True):
        """
        Create neighbor(no_host, for in-direct route).

        Set Device attribtue: neighborv4_id, neighborv6_id
        Set Dut attribute: neighborv4_list, neighborv6_list

        Attrs:
            nexthop_device: Simulating the bypass device that the packet will be forwarded to.
            port_idx: The index of the port which will be used as the egress port.
            virtual_router_id: virtual route id, if not defined, will use default route
            no_host: Neighbor in no_host (neighbor direct) mode

        return neighborv4, neighborv6
        """
        vr_id = self.choice_virtual_route(virtual_router)
        nbr_entry_v4 = sai_thrift_neighbor_entry_t(
            rif_id=rif,
            ip_address=sai_ipaddress(nexthop_device.ipv4))
        status = sai_thrift_create_neighbor_entry(
            self.client,
            nbr_entry_v4,
            dst_mac_address=nexthop_device.mac,
            no_host_route=no_host)
        self.test_obj.assertEqual(status, SAI_STATUS_SUCCESS)

        if nexthop_device.ipv6:
            nbr_entry_v6 = sai_thrift_neighbor_entry_t(
                rif_id=rif,
                ip_address=sai_ipaddress(nexthop_device.ipv6))
            status = sai_thrift_create_neighbor_entry(
                self.client,
                nbr_entry_v6,
                dst_mac_address=nexthop_device.mac,
                no_host_route=no_host)
            self.test_obj.assertEqual(status, SAI_STATUS_SUCCESS)
        else:
            nbr_entry_v6 = None

        if no_host:
            nexthop_device.neighborv4_id = nbr_entry_v4
            nexthop_device.neighborv6_id = nbr_entry_v6
        else:
            nexthop_device.local_neighborv4_id = nbr_entry_v4
            nexthop_device.local_neighborv6_id = nbr_entry_v6

        self.test_obj.dut.neighborv4_list.append(nbr_entry_v4)
        if nbr_entry_v6:
            self.test_obj.dut.neighborv6_list.append(nbr_entry_v6)
        return nbr_entry_v4, nbr_entry_v6

    def create_router_interface_by_vlan(self, vlan: Vlan, virtual_router=None):
        """
        Create vlan intreface.
        It will check if the vlan already created a route interface

        Set vlan attribute rif

        Attrs:
            vlan: vlan object that this vlan interface mapping
            virtual_router_id: virtual route id, if not defined, will use default route
            virtual_router_id: virtual route id, if not defined, will use default route

        return vlan interface id
        """
        if not vlan.rif:
            vr_id = self.choice_virtual_route(virtual_router)
            rif = sai_thrift_create_router_interface(self.client,
                                                     virtual_router_id=vr_id,
                                                     type=SAI_ROUTER_INTERFACE_TYPE_VLAN,
                                                     port_id=vlan.vlan_id)
            self.test_obj.assertEqual(
                self.test_obj.status(), SAI_STATUS_SUCCESS)
            vlan.rif = rif
        return vlan.rif

    def create_router_interface_by_lag(self, lag: Lag, virtual_router=None):
        """
        Create lag intreface.
        It will check if the lag already created a route interface

        Set lag attribute lag_id

        Attrs:
            lag: Lag object that this lag interface mapping
            virtual_router_id: virtual route id, if not defined, will use default route
            virtual_router_id: virtual route id, if not defined, will use default route

        return rif
        """
        if not lag.rif:
            vr_id = self.choice_virtual_route(virtual_router)
            rif = sai_thrift_create_router_interface(self.client,
                                                     virtual_router_id=vr_id,
                                                     type=SAI_ROUTER_INTERFACE_TYPE_PORT,
                                                     port_id=lag.lag_id)
            lag.rif = rif
            self.test_obj.assertEqual(
                self.test_obj.status(), SAI_STATUS_SUCCESS)
        return lag.rif

    def create_router_interface_by_port_idx(self, port_idx, virtual_router=None):
        """
        Create route interface by port index for a port.
        It will check if the port already created a route interface

        Set dut attribute port_rif_list

        Attrs:
            port_idx: port index
            virtual_router_id: virtual route id, if not defined, will use default route

        return: route interface
        """
        if not self.test_obj.dut.port_rif_list[port_idx]:
            vr_id = self.choice_virtual_route(virtual_router)
            port_id = self.test_obj.dut.port_list[port_idx]
            rif_id = sai_thrift_create_router_interface(
                self.client, virtual_router_id=vr_id, type=SAI_ROUTER_INTERFACE_TYPE_PORT, port_id=port_id)
            self.test_obj.dut.port_rif_list[port_idx] = rif_id
            self.test_obj.assertEqual(
                self.test_obj.status(), SAI_STATUS_SUCCESS)

        return self.test_obj.dut.port_rif_list[port_idx]

    def create_router_interface_by_bridge_port_idx(self, bridge_port_idx, virtual_router=None):
        """
        Create route interface by bridge port index for a port.
        It will check if the bridge port already created a route interface

        Set dut attribute bridge_port_rif_list

        Attrs:
            bridge_port_idx: bridge port index
            virtual_router_id: virtual route id, if not defined, will use default route

        return: route interface
        """
        if not self.test_obj.dut.bridge_port_rif_list[bridge_port_idx]:
            vr_id = self.choice_virtual_route(virtual_router)
            bridge_port_id = self.test_obj.dut.port_list[bridge_port_idx]
            rif_id = sai_thrift_create_router_interface(
                self.client, virtual_router_id=vr_id, type=SAI_ROUTER_INTERFACE_TYPE_BRIDGE, port_id=bridge_port_id)
            self.test_obj.dut.bridge_port_rif_list[bridge_port_idx] = rif_id
            self.test_obj.assertEqual(
                self.test_obj.status(), SAI_STATUS_SUCCESS)

        return self.test_obj.dut.bridge_port_rif_list[bridge_port_idx]

    def create_nexthop_by_vlan(self, vlan: Vlan, nexthop_device: Device, virtual_router=None):
        """
        Create nexthop by vlan.

        Set dut attribute: nexthopv4_list, nexthopv6_list
        Set vlan attribute: nexthopv4, nexthopv6
        Set device attribute: nexthopv4, nexthopv6

        Attrs:
            port_idx: bridge port index
            nexthop_device: Simulating the bypass device, use this device to get the ipaddress, ipprefix_v4 and ipprefix_v6
            virtual_router_id: virtual route id, if not defined, will use default route

        return nexthop id
        """
        rif = self.create_router_interface_by_vlan(vlan, virtual_router)
        v4, v6 = self.create_nexthop_by_rif(rif, nexthop_device)
        v4.rif_id = rif
        v6.rif_id = rif
        vlan.nexthopv4 = v4
        vlan.nexthopv6 = v6

        return v4, v6

    def create_nexthop_by_lag(self, lag: Lag, nexthop_device: Device, virtual_router=None):
        """
        Create nexthop by lag.

        Set dut attribute: nexthopv4_list, nexthopv6_list
        Set lag attribute: nexthopv4, nexthopv6
        Set device attribute: nexthopv4, nexthopv6

        Attrs:
            port_idx: bridge port index
            nexthop_device: Simulating the bypass device, use this device to get the ipaddress, ipprefix_v4 and ipprefix_v6
            virtual_router_id: virtual route id, if not defined, will use default route

        return nexthop id
        """
        rif = self.create_router_interface_by_lag(lag, virtual_router)
        v4, v6 = self.create_nexthop_by_rif(rif, nexthop_device)
        v4.rif_id = rif
        v6.rif_id = rif
        v4.lag = lag
        v6.lag = lag
        lag.nexthopv4 = v4
        lag.nexthopv6 = v6
        return v4, v6

    def create_nexthop_by_port_idx(self, port_idx, nexthop_device: Device, ipprefix_v4=None, ipprefix_v6=None, virtual_router=None):
        """
        Create nexthop by port index for a port.

        Set dut attribute: nexthopv4_list, nexthopv6_list, port_nhop_v4_list, port_nhop_v6_list
        Set device attribute: nexthopv4, nexthopv6

        Attrs:
            port_idx: bridge port index
            nexthop_device: Simulating the bypass device, use this device to get the ipaddress, ipprefix_v4 and ipprefix_v6
            virtual_router_id: virtual route id, if not defined, will use default route

        return nexthop id
        """
        rif = self.create_router_interface_by_port_idx(
            port_idx, virtual_router)
        v4, v6 = self.create_nexthop_by_rif(rif, nexthop_device)
        v4.rif_id = rif
        v6.rif_id = rif
        v4.port_idx = port_idx
        v6.port_idx = port_idx
        self.test_obj.dut.port_nhop_v4_list.append(v4)
        self.test_obj.dut.port_nhop_v6_list.append(v6)
        return v4, v6

    def create_nexthop_by_bridge_port_idx(self, bridge_port_idx, nexthop_device: Device, ipprefix_v4=None, ipprefix_v6=None, virtual_router=None):
        """
        Create nexthop by bridge port index for a port.

        Set dut attribute: nexthopv4_list, nexthopv6_list, bridge_port_nhop_v4_list, bridge_port_nhop_v6_list
        Set device attribute: nexthopv4, nexthopv6

        Attrs:
            bridge_port_idx: bridge port index
            nexthop_device: Simulating the bypass device, use this device to get the ipaddress, ipprefix_v4 and ipprefix_v6
            virtual_router_id: virtual route id, if not defined, will use default route

        return nexthop id
        """
        rif = self.create_router_interface_by_bridge_port_idx(
            bridge_port_idx, virtual_router)
        v4, v6 = self.create_nexthop_by_rif(rif, nexthop_device)
        v4.rif_id = rif
        v6.rif_id = rif
        self.test_obj.dut.bridge_port_nhop_v4_list.append(v4)
        self.test_obj.dut.bridge_port_nhop_v6_list.append(v6)
        return v4, v6

    def create_nexthop_group_by_nexthops(self):
        """
        Create nexthop group by nexthops.
        """
        self.test_obj.nhop_group1 = sai_thrift_create_next_hop_group(
            self.test_obj.client, type=SAI_NEXT_HOP_GROUP_TYPE_ECMP)

        self.test_obj.nh_group_member1 = sai_thrift_create_next_hop_group_member(
            self.test_obj.client,
            next_hop_group_id=self.test_obj.nhop_group1,
            next_hop_id=self.test_obj.dut.lag2.nexthopv4.nexthop_id)

        self.test_obj.nh_group_member1 = sai_thrift_create_next_hop_group_member(
            self.test_obj.client,
            next_hop_group_id=self.test_obj.nhop_group1,
            next_hop_id=self.test_obj.dut.lag3.nexthopv4.nexthop_id)

        self.test_obj.ecmp_route0 = sai_thrift_route_entry_t(
            switch_id=self.test_obj.dut.switch_id,
            destination=sai_ipprefix('192.168.60.0/24'),
            vr_id=self.test_obj.dut.default_vrf)
        status = sai_thrift_create_route_entry(
            self.test_obj.client, self.test_obj.ecmp_route0, next_hop_id=self.test_obj.nhop_group1)
        self.test_obj.assertEqual(status, SAI_STATUS_SUCCESS)

    def create_nexthop_by_rif(self, rif, nexthop_device: Device):
        """
        Create nexthop by bridge port index for a port.

        Set dut attribute: nexthopv4_list, nexthopv6_list
        Set device attribute: nexthopv4, nexthopv6

        Attrs:
            rif: route interface id
            nexthop_device: Simulating the bypass device, use this device to get the ipaddress, ipprefix_v4 and ipprefix_v6
            virtual_router_id: virtual route id, if not defined, will use default route

        return nexthop_v4 and nexthop_v6 id
        """
        if nexthop_device.ip_prefix:
            nhopv4_id = sai_thrift_create_next_hop(self.client, ip=sai_ipprefix(
                nexthop_device.ipv4 + '/' + nexthop_device.ip_prefix), router_interface_id=rif, type=SAI_NEXT_HOP_TYPE_IP)
        else:
            nhopv4_id = sai_thrift_create_next_hop(self.client, ip=sai_ipaddress(
                nexthop_device.ipv4), router_interface_id=rif, type=SAI_NEXT_HOP_TYPE_IP)
        self.test_obj.assertEqual(self.test_obj.status(), SAI_STATUS_SUCCESS)

        if nexthop_device.ip_prefix_v6:
            nhopv6_id = sai_thrift_create_next_hop(self.client, ip=sai_ipprefix(
                nexthop_device.ipv6 + '/' + nexthop_device.ip_prefix_v6), router_interface_id=rif, type=SAI_NEXT_HOP_TYPE_IP)
        else:
            nhopv6_id = sai_thrift_create_next_hop(self.client, ip=sai_ipaddress(
                nexthop_device.ipv6), router_interface_id=rif, type=SAI_NEXT_HOP_TYPE_IP)
        self.test_obj.assertEqual(self.test_obj.status(), SAI_STATUS_SUCCESS)
        nhopv4: Nexthop = Nexthop(nhopv4_id, nexthop_device)
        nhopv6: Nexthop = Nexthop(nhopv6_id, nexthop_device)
        self.test_obj.dut.nexthopv4_list.append(nhopv4)
        self.test_obj.dut.nexthopv6_list.append(nhopv6)
        nexthop_device.nexthopv4 = nhopv4
        nexthop_device.nexthopv6 = nhopv6

        return nhopv4, nhopv6

    def create_ecmp_by_lags(self, lags: List[Lag]):
        """
        Create ecmp(next hop group) by lags, each lag will be binding to a nexthop
        """
        pass

    def create_ecmp_by_nexthops(self, nhops: List[Nexthop]):
        """
        Create ecmp(next hop group) by Nexthop, each lag will be binding to a nexthop
        """
        pass

    def create_ecmp_by_ports(self, port_idx: List):
        """
        Create ecmp(next hop group) by ports.
        """
        pass

    def choice_virtual_route(self, virtual_router=None):
        """
        Depends on if virtual_router_id is None, return the default virtual or deinded vr.

        Attrs
            virtual_router_id: defined vr
        """

        if virtual_router is None:
            return self.test_obj.dut.default_vrf

        return virtual_router
