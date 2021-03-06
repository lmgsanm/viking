# -*- coding: utf-8 -*-

import hashlib
import json
from django.shortcuts import render, HttpResponseRedirect
from .models import *
from cmdb.models import Iaas, Region, Zone, Instance
import manage.helpers.aliyun_open_api as AliAPI
import subprocess


def _load_aliyun_config():
    with open('config/_aliyun_config.json') as fp:
        config = json.loads(fp.read())
    return config


def _hash_password(password=''):
    '''md5加密
    :param password:
    :return: 加密后的字符串
    '''
    password = password.encode('utf-8')
    md5 = hashlib.md5()
    md5.update(password)
    return md5.hexdigest()


def _is_user_exist(username):
    '''用户是否存在
    :param username:
    :return: bool
    '''
    if Userinfo.objects.filter(name=username):
        return True
    else:
        return False


def _login_check(func):
    '''是否登陆
    '''

    def check(req, *a, **k):
        # TODO: 加密验证
        name = req.COOKIES.get("name")
        if not name:
            return HttpResponseRedirect('/manage/login')
        return func(req, *a, **k)

    return check


@_login_check
def index(req):
    '''首页
    '''
    username = req.COOKIES.get('name', '')
    return render(req, 'manage/index.html', locals())


def register(req):
    '''注册页面
    '''
    if req.method == 'POST' and req.POST:
        username = req.POST['username']
        if _is_user_exist(username):
            warning = '用户名已存在，请重新选一个独特的用户名'
            return render(req, 'manage/register.html', locals())
        user = Userinfo()
        user.name = username
        user.password = _hash_password(req.POST['password'])
        user.email = req.POST['email']
        user.save()
        return HttpResponseRedirect('/manage/login')
    else:
        return render(req, 'manage/register.html')


def login(req):
    if req.method == 'POST' and req.POST:
        username = req.POST['username']
        password = req.POST['password']
        password = _hash_password(password)

        if (_is_user_exist(username)):
            dbpassword = Userinfo.objects.get(name=username).password
            if dbpassword == password:
                response = HttpResponseRedirect('/manage/index')
                response.set_cookie('name', username, max_age=3600)
                req.session['name'] = username
                return response
            else:
                error = '用户名或密码错误，请重新输入'
                return render(req, 'manage/login.html', locals())
        else:
            error = '用户名或密码错误，请重新输入'
            return render(req, 'manage/login.html', locals())
    else:
        return render(req, 'manage/login.html', locals())


@_login_check
def iaaslist(req):  # 平台管理的iaas账户列表
    username = req.COOKIES.get('name', '')
    indexname = 'Iaas 账户信息'
    iaas_list = Iaas.objects.all()
    return render(req, 'manage/cmdb/iaas.html', locals())


def _is_aliyun(sp):
    return sp == 'aliyun'


@_login_check
def regionlist(req):  # 分区列表信息
    # username = req.COOKIES.get('name', '')
    iaas = req.GET.get('iaas', '')
    sp = req.GET.get('sp', '')  # ['sp']
    index = req.GET.get('index', '')  # ['index']
    indexname = index + u' / 地区列表'
    # print("iaas is %s" % iaas)
    if _is_aliyun(sp):
        print("aliyun sp")
        regions = AliAPI.ecs_region_list_request()
        region_list = json.loads(regions)['Regions']['Region']
        return render(req, 'manage/cmdb/ali_region.html', locals())
    else:
        region_list = Region.objects.values('id', 'name', 'iaas__id', 'iaas__name', 'iaas__sp').filter(iaas__id=iaas)[
                      :50]
        # print("region list %s" % region_list.query)
        return render(req, 'manage/cmdb/region.html', locals())


@_login_check
def zonelist(req):  # 分组列表信息
    username = req.COOKIES.get('name', '')
    region = req.GET.get('region', '')
    sp = req.GET.get('sp', '')
    index = req.GET.get('index', '')
    indexname = index + u' / 分组列表'
    print(("region is %s" % region))
    if _is_aliyun(sp):
        print("aliyun sp")
        zones = AliAPI.ecs_zone_list_request(region)
        zone_list = json.loads(zones)['Zones']['Zone']
        for zone in zone_list:
            zone['regionId'] = region
        return render(req, 'manage/cmdb/ali_zone.html', locals())
    else:
        zone_list = Zone.objects.values('id', 'name', 'region__id', 'region__name').filter(region__id=region)[:50]
        return render(req, 'manage/cmdb/zone.html', locals())


@_login_check
def instancelist(req):  # 主机列表信息
    # username = req.COOKIES.get('name', '')
    region = req.GET.get('regionId', '')
    zone = req.GET.get('zone', '')  # ['zone']
    local_name = req.GET.get('LocalName', '')  # ['LocalName']
    sp = req.GET.get('sp', '')
    # index = req.GET.get('index', '') # ['index']
    indexname = local_name + u' / 主机列表'
    if _is_aliyun(sp):
        instances = AliAPI.ecs_instance_list_request(region, zone)
        instance_list = json.loads(instances)['Instances']['Instance']
        for ins in instance_list:
            ins['LocalName'] = local_name;
            print(instance_list);
        return render(req, 'manage/cmdb/ali_hosts.html', locals())
    else:
        asset_list = Instance.objects.all()[:50]
        return render(req, 'manage/cmdb/instance.html', locals())


@_login_check
def auto_deploy_index(req):  # auto deploy index page
    current_user = req.COOKIES.get('name', '')
    indexname = 'AutoM 自动化部署'
    # TODO: find auto deploy tasks
    # iaas_list = Iaas.objects.all()
    return render(req, 'manage/autodeploy/index.html', locals())


@_login_check
def auto_deploy_repo(req):
    repo = req.GET.get('repo', '')
    topl = req.GET.get('topl', '')
    cmd = '/home/devops/apps/viking-ansible/bin/run_prod.sh '
    if (repo == 'storm' and topl == 'searchindex'):
        cmd += 'storm submit searchindex'
    elif (repo == 'storm' and topl == 'hdf_searchindex'):
        cmd += 'storm submit hdf_searchindex'
    elif (repo == 'cmsweb'):
        cmd += 'cmsweb'
    elif (repo == 'cmsapi'):
        cmd += 'cmsapi'
    else:
        err_info = "Error: unknown repo : " + repo
        return render(req, 'manage/autodeploy/index.html', locals())
    # if (repo == 'storm'):
    #     cmd += 'storm submit '
    #     if (topl == 'searchindex'):
    #         cmd += 'searchindex'
    #     elif (topl == 'hdf_searchindex'):
    #         cmd += 'hdf_searchindex'
    #     else:
    #         err_info = "Error: repo-storm submit unknown topl : " + topl
    #         return render(req, 'manage/autodeploy/index.html', locals())
    # elif (repo == 'cms'):
    #     err_info = "Error: repo-cms submit unknown topl : " + topl
    #     return render(req, 'manage/autodeploy/index.html', locals())
    # else:
    #     err_info = "Error: unknown repo : " + repo
    #     return render(req, 'manage/autodeploy/index.html', locals())

    # info = subprocess.call([cmd],shell=True)
    stdinfo = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if (stdinfo.stdout):
        deploy_info = "Deploy Info :"
        for line in stdinfo.stdout.readlines():
            deploy_info += str(line)
    if (stdinfo.stderr):
        err_info = "Error Info :"
        for line in stdinfo.stderr.readlines():
            err_info += str(line)
    return render(req, 'manage/autodeploy/index.html', locals())
