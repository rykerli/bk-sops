# -*- coding: utf-8 -*-
import logging

from django.http import JsonResponse

from gcloud.conf import settings
from gcloud.utils.cmdb import batch_request
from gcloud.utils.handlers import handle_api_error

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
logger = logging.getLogger("root")


def get_set_list(username, bk_biz_id, bk_supplier_account, kwargs=None):
    """
    @summary: 批量获取业务下所有集群
    @param username:
    @param bk_biz_id:
    @param bk_supplier_account:
    @return: [{'bk_set_id':'', 'bk_set_name':''}, {'bk_set_id':'', 'bk_set_name':''}]
    """
    client = get_client_by_user(username)
    params = {
        "bk_biz_id": bk_biz_id,
        "bk_supplier_account": bk_supplier_account,
        "fields": ["bk_set_name", "bk_set_id"],
    }
    if kwargs:
        params.update(kwargs)
    return batch_request(client.cc.search_set, params)


def get_service_template_list(username, bk_biz_id, bk_supplier_account):
    """
    @summary: 批量获取服务模板列表
    @param username:
    @param bk_biz_id:
    @param bk_supplier_account:
    @return: [{'id':'', 'name':''}, {'id':'', 'name':''}]
    """
    client = get_client_by_user(username)
    kwargs = {"bk_biz_id": int(bk_biz_id), "bk_supplier_account": bk_supplier_account}
    list_service_template_return = client.cc.list_service_template(kwargs)
    if not list_service_template_return["result"]:
        message = handle_api_error("cc", "cc.list_service_template", kwargs, list_service_template_return)
        logger.error(message)
        return JsonResponse({"result": False, "data": [], "message": message})
    return list_service_template_return["data"]["info"]


def search_topo_tree(username, bk_biz_id):
    """
    @summary: 获取业务下集群模块topo
    @param username:
    @param bk_biz_id:
    @return: [{'bk_biz_id':'', 'bk_biz_name':'', "bk_topo_tree": [
        {
          "bk_obj_id": "set",
          "bk_inst_name": "PaaS平台",
          "bk_inst_id": 4,
          "children": [{
              "bk_obj_id": "module",
              "bk_inst_name": "nginx",
              "bk_inst_id": 15,
              "children": null}]
        }]}]
    """
    client = get_client_by_user(username)
    params = {"bk_biz_id": bk_biz_id, "bk_biz_name": ""}
    topo_tree_result = client.cc.search_topo_tree(params)
    if not topo_tree_result["result"]:
        message = handle_api_error("cc", "cc.search_topo_tree", params, topo_tree_result)
        logger.error(message)
        return JsonResponse({"result": False, "data": [], "message": message})
    return topo_tree_result["data"]


def list_biz_hosts(username, bk_biz_id, bk_supplier_account, kwargs=None):
    """
    @summary: 批量获取业务下主机
    @param kwargs:
    @param username:
    @param bk_biz_id:
    @param bk_supplier_account:
    @return: [{'bk_set_id':'', 'bk_set_name':''}, {'bk_set_id':'', 'bk_set_name':''}]
    """
    client = get_client_by_user(username)
    params = {"bk_biz_id": bk_biz_id, "bk_supplier_account": bk_supplier_account}
    if kwargs:
        params.update(kwargs)
    return batch_request(client.cc.list_biz_hosts, params)
