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
from django.conf.urls import url
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from gcloud.conf import settings
from pipeline_plugins.base.utils.inject import (
    supplier_account_inject
)
from pipeline_plugins.variables.query.sites.open import select
from pipeline_plugins.variables.utils import get_set_list, get_service_template_list

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


@supplier_account_inject
def cc_get_set(request, biz_cc_id, supplier_account):
    """
    @summary: 批量获取业务下所有集群
    @param request:
    @param biz_cc_id:
    @param supplier_account:
    @return:
    """
    cc_set_result = get_set_list(request.user.username, biz_cc_id, supplier_account)
    result = [{'value': set_item['bk_set_name'], 'text': set_item['bk_set_name']} for
              set_item in cc_set_result]
    result.insert(0, {'value': 'all', 'text': _('所有集群(all)')})

    return JsonResponse({"result": True, "data": result})


@supplier_account_inject
def cc_list_service_template(request, biz_cc_id, supplier_account):
    """
    获取服务模板
    url: /pipeline/cc_list_service_template/biz_cc_id/
    :param request:
    :param biz_cc_id:
    :param supplier_account:
    :return:
        - 请求成功 {"result": True, "data": service_templates, "message": "success"}
            - service_templates： [{"value" : 模板名_模板id, "text": 模板名}, ...]
        - 请求失败 {"result": False, "data": [], "message": message}
    """
    service_templates_untreated = get_service_template_list(request.user.username, biz_cc_id, supplier_account)
    service_templates = []
    for template_untreated in service_templates_untreated:
        template = {
            "value": template_untreated["name"],
            "text": template_untreated["name"],
        }
        service_templates.append(template)
    # 为服务模板列表添加一个all选项
    if request.GET.get('all'):
        service_templates.insert(0, {'value': 'all', 'text': _('所有模块(all)')})

    return JsonResponse({"result": True, "data": service_templates, "message": "success"})


urlpatterns = [
    # set module ip selector
    url(r"^cc_get_service_template_list/(?P<biz_cc_id>\d+)/$", cc_list_service_template),
    url(r"^cc_get_set_list/(?P<biz_cc_id>\d+)/$", cc_get_set)
]
urlpatterns += select.select_urlpatterns
