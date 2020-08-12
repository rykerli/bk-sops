# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from gcloud.core.models import Project
from pipeline.core.data.var import LazyVariable
from pipeline_plugins.base.utils.inject import supplier_account_for_project
from pipeline_plugins.components.utils.sites.open.utils import cc_get_ips_info_by_str
from pipeline_plugins.variables.utils import get_set_list, get_service_template_list, search_topo_tree, list_biz_hosts

SELECT_ALL = "all"


class SetModuleIpSelector(LazyVariable):
    code = "set_module_ip_picker"
    name = _("集群模块IP选择器")
    type = "general"
    tag = "set_module_ip_picker.ip_selector"
    form = "%svariables/cmdb/var_set_module_ip_picker.js" % settings.STATIC_URL

    def get_value(self):
        var_ip_picker = self.value
        username = self.pipeline_data["executor"]
        project_id = self.pipeline_data["project_id"]
        project = Project.objects.get(id=project_id)
        bk_biz_id = project.bk_biz_id if project.from_cmdb else ""
        bk_supplier_account = supplier_account_for_project(project_id)

        produce_method = var_ip_picker["var_ip_method"]
        if produce_method == "custom":
            custom_value = var_ip_picker["var_ip_custom_value"]
            data = cc_get_ips_info_by_str(username, bk_biz_id, custom_value)
            ip_list = data["ip_result"]
            data = ",".join([ip["InnerIP"] for ip in ip_list])
        elif produce_method == "select":
            select_value = var_ip_picker["var_ip_select_value"]
            # 集群全选，筛选条件不为空则调接口获取集群id列表
            if SELECT_ALL in select_value["var_set"]:
                set_list = get_set_list(username, bk_biz_id, bk_supplier_account)
                set_names_result = [set_item["bk_set_name"] for set_item in set_list]
            else:
                set_names_result = select_value["var_set"]
            # 服务模板全选，则调接口获取服务模板列表
            if SELECT_ALL in select_value["var_module"]:
                service_template_list = get_service_template_list(username, bk_biz_id, bk_supplier_account)
                modules_names_result = [
                    service_template_item["name"] for service_template_item in service_template_list
                ]
            else:
                modules_names_result = select_value["var_module"]
            # 需要筛选的集群、模块
            if select_value["var_filter_set"]:
                set_names_result = filter_data(set_names_result, select_value["var_filter_set"])
            if select_value["var_filter_module"]:
                modules_names_result = filter_data(modules_names_result, select_value["var_filter_module"])
            # 根据业务id获取所有集群下模块列表
            module_ids = get_module_by_set(username, bk_biz_id, set_names_result, modules_names_result)
            # 获取主机属性
            kwargs = {
                "bk_module_ids": module_ids,
                "fields": select_value["var_module_name"] if select_value["var_module_name"] else "InnerIP",
            }
            host_list = list_biz_hosts(username, bk_biz_id, bk_supplier_account, kwargs=kwargs)
            print(host_list)
        elif produce_method == "manual":
            data = ""
        else:
            data = ""
        return data


def filter_data(origin_list, filter_list):
    """
    筛选数据
    @param origin_list:
    @param filter_list:需要筛选出来的数据
    @return:
    """
    return [filter_item for filter_item in filter_list if filter_item in origin_list]


def get_module_by_set(username, bk_biz_id, select_set_names, filter_services_template):
    module_ids = []
    # step1. 获取topo tree
    topo_tree_result = search_topo_tree(username, bk_biz_id)
    # step2. 根据选中的set ids过滤出set
    for topo_tree in topo_tree_result:
        for topo in topo_tree["bk_topo_tree"]:
            if topo["bk_obj_id"] == "set" and topo["bk_inst_name"] in select_set_names:
                # 根据服务模板取模块
                for module_obj in topo["children"]:
                    if module_obj["bk_obj_id"] == "module" and module_obj["bk_inst_name"] in filter_services_template:
                        module_ids.append(module_obj["bk_inst_id"])
    return module_ids
