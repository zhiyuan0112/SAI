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


def t0_lag_config_helper(test_obj, is_create_lag=True):
    """
    Make lag configurations base on the configuration in the test plan.
    set the configuration in test directly.

    set the following test_obj attributes:
        lag object
    
    """
    lag_configer = LagConfiger(test_obj)

    if is_create_lag:
        test_obj.dut.lag1 = lag_configer.create_lag([17, 18])
        test_obj.dut.lag2 = lag_configer.create_lag([19, 20])
        test_obj.lag1_neighbor = test_obj.t1s[1][0]
        test_obj.lag2_neighbor = test_obj.t1s[2][0]
        

    """
    lag_configer.set_lag_hash_algorithm()
    lag_configer.setup_lag_v4_hash()
    lag_configer.set_lag_hash_seed()
    """


class LagConfiger(object):
    """
    Class use to make all the Lag configurations.
    """

    def __init__(self, test_obj) -> None:
        """
        Init Lag configrer.
        
        Args:
            test_obj: the test object
        """
        self.test_obj = test_obj
        self.client = test_obj.client
    
    def create_lag(self, lag_port_idxs):
        """
        Create lag and its members.

        Args:
            lag_port_idxs: lag port indexs

        Returns:
            Lag: lag object
        """

        lag = Lag()
        lag_id = sai_thrift_create_lag(self.client)
        lag_members = self.create_lag_member(lag_id, lag_port_idxs)
        self.test_obj.assertEqual(self.test_obj.status(), SAI_STATUS_SUCCESS)
        lag.lag_id = lag_id
        lag.lag_members = lag_members
        return lag
    
    def create_lag_member(self, lag_id, lag_port_idxs):
        """
        Create lag members for a lag.

        Args:
            lag: lag object
            lag_port_idxs: lag member port indexs

        Returns:
            lag_members: list of lag_member
        """

        lag_members = []
        for port_index in lag_port_idxs:
            lag_member = sai_thrift_create_lag_member(self.client, 
                                                      lag_id=lag_id, 
                                                      port_id=self.test_obj.dut.port_list[port_index])
            self.test_obj.assertEqual(self.test_obj.status(), SAI_STATUS_SUCCESS)
            lag_members.append(lag_member)
        return lag_members
    
    def set_lag_hash_algorithm(self, algo=SAI_HASH_ALGORITHM_CRC):
        """
        Set lag hash algorithm.

        Args:
            algo (int): hash algorithm id
        """
        sai_thrift_set_switch_attribute(self.client, lag_default_hash_algorithm=algo)

    def setup_lag_v4_hash(self, hash_fields_list=None, lag_hash_ipv4=None):
        if hash_fields_list is None:
            hash_fields_list = [SAI_NATIVE_HASH_FIELD_SRC_IP,
                                SAI_NATIVE_HASH_FIELD_DST_IP,
                                SAI_NATIVE_HASH_FIELD_IP_PROTOCOL,
                                SAI_NATIVE_HASH_FIELD_L4_DST_PORT,
                                SAI_NATIVE_HASH_FIELD_L4_SRC_PORT]

        if lag_hash_ipv4 is None:
            # create new hash
            s32list = sai_thrift_s32_list_t(count=len(hash_fields_list), int32list=hash_fields_list)
            lag_hash_ipv4 = sai_thrift_create_hash(self.client, native_hash_field_list=s32list)
            self.test_obj.assertTrue(lag_hash_ipv4 != 0, "Failed to create IPv4 lag hash")
            status = sai_thrift_set_switch_attribute(self.client, lag_hash_ipv4=lag_hash_ipv4)
            self.test_obj.assertEqual(status, SAI_STATUS_SUCCESS)
        else:
            # update existing hash
            s32list = sai_thrift_s32_list_t(count=len(hash_fields_list), int32list=hash_fields_list)
            status = sai_thrift_set_hash_attribute(self.client, lag_hash_ipv4, native_hash_field_list=s32list)
            self.test_obj.assertEqual(status, SAI_STATUS_SUCCESS)

    def set_lag_hash_seed(self, seed=400):
        """
        Set lag hash seed.

        Args:
            seed: hash seed value
        """
        status = sai_thrift_set_switch_attribute(self.client, lag_default_hash_seed=seed)
        self.test_obj.assertEqual(status, SAI_STATUS_SUCCESS)

    def remove_lag_member(self, lag_member):
        sai_thrift_remove_lag_member(self, lag_member)

    def remove_all_lag_members(self, lag_members):
        for lag_member in lag_members:
            sai_thrift_remove_lag_member(self.client, lag_member)
    
    def remove_lag(self, lag_id):
        sai_thrift_remove_lag(self.client, lag_id)

class Lag(object):
    """
    Represent the lag object.
    Attrs:
        lag_id: lag id
        lag_members: lag members
    """
    def __init__(self, lag_id=None, lag_members=None):
        self.lag_id = lag_id
        self.lag_members = lag_members
