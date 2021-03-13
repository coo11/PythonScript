
# -*- coding: utf-8 -*-
# https://lancellc.gitbook.io/clash/clash-config-file

import re
import yaml
import requests
import base64
import argparse
from time import strftime
from os import path

Profiles_ConnersHua = """
rule-providers:

  AdBlockWhite:
    type: http
    behavior: classical
    path: ./RuleSet/AdBlockWhite.yaml
    url: https://cdn.jsdelivr.net/gh/blackmatrix7/ios_rule_script@release/rule/Clash/WhiteList/WhiteList.yaml
    interval: 86400
    
  AdBlock:
    type: http
    behavior: classical
    path: ./RuleSet/AdBlock.yaml
    url: https://cdn.jsdelivr.net/gh/blackmatrix7/ios_rule_script@release/rule/Clash/Advertising/Advertising.yaml
    interval: 86400

  FSMEDIA:
    type: http
    behavior: classical
    path: ./RuleSet/FSMEDIA.yaml
    url: https://cdn.jsdelivr.net/gh/blackmatrix7/ios_rule_script@release/rule/Clash/GlobalMedia/GlobalMedia.yaml
    interval: 86400

  Global:
    type: http
    behavior: classical
    path: ./RuleSet/Global.yaml
    url: https://cdn.jsdelivr.net/gh/blackmatrix7/ios_rule_script@release/rule/Clash/Global/Global.yaml
    interval: 86400
    
  GlobalDomain:
    type: http
    behavior: domain
    path: ./RuleSet/GlobalDomain.yaml
    url: https://cdn.jsdelivr.net/gh/blackmatrix7/ios_rule_script@release/rule/Clash/Proxy/Proxy_Domain.yaml
    interval: 86400
    
  China:
    type: http
    behavior: classical
    path: ./RuleSet/China.yaml
    url: https://cdn.jsdelivr.net/gh/blackmatrix7/ios_rule_script@release/rule/Clash/China/China.yaml
    interval: 86400

  Telegram:
    type: http
    behavior: classical
    path: ./RuleSet/Telegram.yaml
    url: https://cdn.jsdelivr.net/gh/lhie1/Rules@master/Clash/Provider/Telegram.yaml
    interval: 86400

  Blackhole:
    type: http
    behavior: ipcidr
    path: ./RuleSet/Blackhole.yaml
    url: https://cdn.jsdelivr.net/gh/DivineEngine/Profiles@master/Clash/RuleSet/Extra/IP-Blackhole.yaml
    interval: 86400

# ALL POLICY YOU CAN USE: DIRECT, PROXY, DENIED, FSMEDIA, MATCH
rules:
  - RULE-SET,AdBlockWhite,NATIVE
  - RULE-SET,AdBlock,DENIED
  - RULE-SET,Telegram,PROXY
  - RULE-SET,Blackhole,PROXY,no-resolve
  - RULE-SET,FSMEDIA,FSMEDIA
  
  # GeoIP
  - GEOIP,CN,DIRECT
  
  - RULE-SET,Global,PROXY
  - RULE-SET,GlobalDomain,PROXY

  - IP-CIDR,192.168.0.0/16,DIRECT
  - IP-CIDR,10.0.0.0/8,DIRECT
  - IP-CIDR,172.16.0.0/12,DIRECT
  - IP-CIDR,127.0.0.0/8,DIRECT
  - IP-CIDR,100.64.0.0/10,DIRECT
  - IP-CIDR,224.0.0.0/4,DIRECT

  - RULE-SET,China,DIRECT

  - MATCH,MATCH
"""

CPATH = path.dirname(path.abspath(__file__))


def set_basic_info(
    *, port=7890, m_port=6789, s5_port=5678, mode="rule", log_lv="info", ext_port=9877
):
    return rf"""##############
# Generated at {strftime("%Y-%m-%d %H:%M:%S")}
##############
# HTTP
port: {port}
# HTTP&SOCKS5
mixed-port: {m_port}
# SOCKS5
socks-port: {s5_port}
# Linux & macOS
# redir-port: 7892
allow-lan: false
# rule / global / direct
mode: {mode}
# silent / info / warning / error / debug
log-level: {log_lv}
# RESTful API
external-controller: '127.0.0.1:{ext_port}'
# `http://{{external-controller}}/ui`
external-ui: .\dashboard
experimental:
  ignore-resolve-fail: true
tun:
  enable: true
  stack: gvisor # only gvisor
  dns-hijack:
    - 198.18.0.2:53 # when `fake-ip-range` is 198.18.0.1/16, should hijack 198.18.0.2:53
  macOS-auto-route: true # auto set global route for Windows
  # It is recommended to use `interface-name`
  macOS-auto-detect-interface: true # auto detect interface, conflict with `interface-name`
dns:
  enable: true
  ipv6: false
  listen: '0.0.0.0:53'
  enhanced-mode: fake-ip
  # enhanced-mode: redir-host
  default-nameserver:
    - 119.29.29.29
    - 223.5.5.5
    - 8.8.8.8
  fake-ip-range: 198.18.0.1/16
  fake-ip-filter:
    # 以下域名列表参考自 vernesong/OpenClash 项目，并由 Hackl0us 整理补充
    # === LAN ===
    - '*.lan'
    # === Linksys Wireless Router ===
    - '*.linksys.com'
    - '*.linksyssmartwifi.com'
    # === Apple Software Update Service ===
    - 'swscan.apple.com'
    - 'mesu.apple.com'
    # === Windows 10 Connnect Detection ===
    - '*.msftconnecttest.com'
    - '*.msftncsi.com'
    # === NTP Service ===
    - 'time.*.com'
    - 'time.*.gov'
    - 'time.*.edu.cn'
    - 'time.*.apple.com'

    - 'time1.*.com'
    - 'time2.*.com'
    - 'time3.*.com'
    - 'time4.*.com'
    - 'time5.*.com'
    - 'time6.*.com'
    - 'time7.*.com'

    - 'ntp.*.com'
    - 'ntp.*.com'
    - 'ntp1.*.com'
    - 'ntp2.*.com'
    - 'ntp3.*.com'
    - 'ntp4.*.com'
    - 'ntp5.*.com'
    - 'ntp6.*.com'
    - 'ntp7.*.com'

    - '*.time.edu.cn'
    - '*.ntp.org.cn'
    - '+.pool.ntp.org'

    - 'time1.cloud.tencent.com'
    # === Music Service ===
    ## NetEase
    - '+.music.163.com'
    - '*.126.net'
    ## Baidu
    - 'musicapi.taihe.com'
    - 'music.taihe.com'
    ## Kugou
    - 'songsearch.kugou.com'
    - 'trackercdn.kugou.com'
    ## Kuwo
    - '*.kuwo.cn'
    ## JOOX
    - 'api-jooxtt.sanook.com'
    - 'api.joox.com'
    - 'joox.com'
    ## QQ
    - '+.y.qq.com'
    - '+.music.tc.qq.com'
    - 'aqqmusic.tc.qq.com'
    - '+.stream.qqmusic.qq.com'
    ## Xiami
    - '*.xiami.com'
    ## Migu
    - '+.music.migu.cn'
    # === Game Service ===
    ## Nintendo Switch
    - '+.srv.nintendo.net'
    ## Sony PlayStation
    - '+.stun.playstation.net'
    ## Microsoft Xbox
    - 'xbox.*.microsoft.com'
    - '+.xboxlive.com'
    # === Other ===
    ## QQ Quick Login
    - 'localhost.ptlogin2.qq.com'
    ## Golang
    - 'proxy.golang.org'
    ## STUN Server
    - 'stun.*.*'
    - 'stun.*.*.*'
  nameserver:
    - tls://dns.rubyfish.cn:853
    - https://doh.pub/dns-query
    - tls://dns.pub
  fallback:
    - https://dns.google/dns-query
    - tcp://1.1.1.1
    - https://1.1.1.1/dns-query
  fallback-filter:
    geoip: true
clash-for-android: 
  # append-system-dns: true # append system DNS to nameserver 
  ui-subtitle-pattern: "[\u4e00-\u9fa5]{2,4}"
"""


def deduplicate_list(*nodes):
    all_nodes = [node for each in nodes for node in each]
    all_names = {i['name'] for i in all_nodes}
    test = dict()
    for i, info in enumerate(all_nodes):
        n = info['name']
        if n not in test:
            test[n] = 1
        else:
            j = test[n]
            test[n] = j + 1
            while f'{n}_{str(j)}' in all_names:
                j += 1
            new_name = f'{n}_{str(j)}'
            test[new_name] = 1
            all_nodes[i]['name'] = new_name
            all_names.add(new_name)
    return all_nodes


def get_sub_list(*sub_url):
    subs = []
    for i in sub_url:
        r = requests.get(i)
        sub = ""
        try:
            sub = decode_b64(r.text)
        except:
            sub = parse_yaml(r.text)
        else:
            try:
                sub = parse_yaml(sub)
            except:
                sub = {'proxies': [i.strip()
                                   for i in sub.split('\n') if i.strip() != '']}
        if "proxies" in sub:
            subs.append(sub["proxies"])
        else:
            print(f'Subscription link\n{i}:\nNo support subscription yet.\n')
            # subs = parse_url(subs.strip().split("\n"))
    if len(subs):
        return deduplicate_list(*subs)
    else:
        return []


def make_proxy_group(subs):
    # if not subs:
    #     raise Exception('No subscription data avaliable.')
    region = ["JP", "HK", "TW", "US", "EA", "XX"]
    regex = ["日本", "深港|香港", "台湾|彰化", "美国", "韩国|新加坡"]
    group = [{"name": i, "type": "select", "proxies": []} for i in region]
    regex = [re.compile(i, re.I | re.A) for i in regex]
    # WARNING: If not use re.A, some CJK unicodes may be lost.
    for i in subs:
        for j, k in enumerate(regex):
            if k.search(i['name']):
                group[j]["proxies"].append(i['name'])
                break
        else:
            group[5]["proxies"].append(i['name'])
    group[0]["type"] = "fallback"
    group[0]["interval"] = 300
    group[0]["url"] = "http://connectivitycheck.gstatic.com/generate_204"
    group += [
        {"name": 'HKA', "type": "url-test", "interval": 7200, "tolerance": 20,
            "url": "http://youtube.com/generate_204", "proxies": group[1]['proxies']},
        {"name": "PROXY", "type": "select",
            "proxies": ['HKA']+region + ["DIRECT"]},
        {
            "name": "NATIVE",
            "type": "select",
            "proxies": ["DIRECT", "HKA", "HK", "TW", "JP"],
        },
        # {"name": "CNMEDIA", "type": "select", "proxies": ["DIRECT", "HK", "TW"]},
        {
            "name": "FSMEDIA",
            "type": "select",
            "proxies": ["HKA", "HK", "TW", "JP", "US", "PROXY"],
        },
        {"name": "MATCH", "type": "select",
            "proxies": ["PROXY","DIRECT"]},
        {"name": "DENIED", "type": "select",
            "proxies": ["REJECT", "NATIVE"]},
    ]
    return dump_yaml('proxy-groups', group)


def add_custom_rules(rules):
    default = parse_yaml(Profiles_ConnersHua)
    return '\n\n'.join([
        yaml.dump({'rule-providers': default['rule-providers']}, indent=2),
        dump_yaml('rules', rules) + dump_yaml('rules',
                                              default['rules']).replace('rules:', '')
    ])


def dump_yaml(node_name, node_content):
    if not node_content:
        return f'{node_name}:\n\n'
    content = [
        "  - " + str(i).replace("'", '"').replace(" ", "") for i in node_content
    ]
    return f"{node_name}:\n" + "\n".join(content)


def parse_yaml(string):
    return yaml.load(string, Loader=yaml.SafeLoader)


def make_config(update_type, *sub_urls, **kw):
    body = [set_basic_info(), None, None, None]
    fp = path.join(CPATH, "config.yaml")
    if not path.exists(fp):
        update_type = 'all'
    elif update_type != 'all':
        with open(fp, 'r', encoding='utf-8') as f:
            config = parse_yaml(f.read())
            body[1] = dump_yaml('proxies', config.get('proxies'))
            body[2] = dump_yaml(
                'proxy-groups', config.get('proxy-groups'))
            body[3] = yaml.dump({'rule-providers': config.get('rule-providers')}, indent=2
                                ) + '\n\n' + dump_yaml('rules', config.get('rules'))
    if update_type != 'rules':
        subs = get_sub_list(*sub_urls)
        body[1] = dump_yaml('proxies', subs)
        body[2] = make_proxy_group(subs)
    if update_type != 'subs':
        body[3] = add_custom_rules(kw['rules'])
    with open(fp, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(body))
    print('Finished.')


def decode_b64(string):
    def p(s): return s + "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(p(string)).decode("utf-8")


def safe_get(dic, key, ret=[]):
    val = dic.get(key, ret)
    if not val and val != ret:
        return ret
    else:
        return val


def main():
    parser = argparse.ArgumentParser(
        prog='MyClashConfigParser',
        description='Update or generate clash config info.\nIf params not given but needed, info will be tried to find in custom.yaml.\nIf no parameters given, all is used by default.')
    parser.add_argument(
        'pos', nargs='*', help="Update all info, as same as param '--all'.", metavar='urls')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--all", nargs='*', default=[],
                       help="Update subscriptions and rules.", metavar=('url', 'urls'))
    group.add_argument("-s", "--subs", nargs='*', default=[],
                       help="Just update subscriptions.", metavar=('url', 'urls'))
    group.add_argument("-r", "--rules", action='store_true',
                       help="Just add custom rules.")
    args = parser.parse_args()
    urls_arg, rules_arg = [], []
    fp = path.join(CPATH, "custom.yaml")
    if path.exists(fp):
        with open(fp, 'r', encoding='utf-8') as f:
            custom = parse_yaml(f.read())
            urls_arg = safe_get(custom, 'subs')
            rules_arg = safe_get(custom, 'rules')
    urls = args.pos + args.subs + args.all
    if args.rules:
        if not urls:
            update_type = 'rules'
        else:
            print("Error: Other parameters confilct with '-r/--rules'.")
            exit(0)
    elif args.subs:
        update_type = 'subs'
    else:
        update_type = 'all'
    if not urls_arg:
        urls_arg = urls
    make_config(update_type, *urls_arg, rules=rules_arg)


if __name__ == '__main__':
    main()
