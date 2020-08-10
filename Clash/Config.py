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

  Unbreak:
    type: http
    behavior: classical
    path: ./RuleSet/Unbreak.yaml
    url: https://raw.githubusercontent.com/DivineEngine/Profiles/master/Clash/RuleSet/Unbreak.yaml
    interval: 86400

  AdBlock:
    type: http
    behavior: classical
    path: ./RuleSet/AdBlock.yaml
    url: https://raw.githubusercontent.com/DivineEngine/Profiles/master/Clash/RuleSet/Guard/Advertising.yaml
    interval: 86400

  Hijacking:
    type: http
    behavior: classical
    path: ./RuleSet/Hijacking.yaml
    url: https://raw.githubusercontent.com/DivineEngine/Profiles/master/Clash/RuleSet/Guard/Hijacking.yaml
    interval: 86400

  Streaming:
    type: http
    behavior: classical
    path: ./RuleSet/Hijacking.yaml
    url: https://raw.githubusercontent.com/DivineEngine/Profiles/master/Clash/RuleSet/StreamingMedia/Streaming.yaml
    interval: 86400

  Global:
    type: http
    behavior: classical
    path: ./RuleSet/Global.yaml
    url: https://raw.githubusercontent.com/DivineEngine/Profiles/master/Clash/RuleSet/Global.yaml
    interval: 86400

  China:
    type: http
    behavior: classical
    path: ./RuleSet/China.yaml
    url: https://raw.githubusercontent.com/DivineEngine/Profiles/master/Clash/RuleSet/China.yaml
    interval: 86400

# ALL POLICY YOU CAN USE: DIRECT, PROXY, DENIED, OSMEDIA, MATCH
rules:
  - RULE-SET,Unbreak,DIRECT
  - RULE-SET,AdBlock,DENIED
  - RULE-SET,Hijacking,DENIED
  - RULE-SET,Streaming,OSMEDIA
  - RULE-SET,Global,PROXY

  - IP-CIDR,192.168.0.0/16,DIRECT
  - IP-CIDR,10.0.0.0/8,DIRECT
  - IP-CIDR,172.16.0.0/12,DIRECT
  - IP-CIDR,127.0.0.0/8,DIRECT
  - IP-CIDR,100.64.0.0/10,DIRECT
  - IP-CIDR,224.0.0.0/4,DIRECT

  - RULE-SET,China,DIRECT
  # Tencent
  - IP-CIDR,119.28.28.28/32,DIRECT
  - IP-CIDR,182.254.116.0/24,DIRECT

  # GeoIP
  - GEOIP,CN,DIRECT
  - GEOIP,TW,PROXY

  - MATCH,MATCH
"""

CPATH = path.dirname(path.abspath(__file__))


def set_basic_info(
    *, port=7890, s5_port=7891, mode="rule", log_lv="info", ext_port=9877
):
    return rf"""##############
# Generated at {strftime("%Y-%m-%d %H:%M:%S")}
##############
# HTTP
port: {port}
# SOCKS5
socks-port: {s5_port}
# Linux & macOS
# redir-port: 7892
allow-lan: true
# rule / global / direct
mode: {mode}
# silent / info / warning / error / debug
log-level: {log_lv}
# RESTful API
external-controller: '127.0.0.1:{ext_port}'
# `http://{{external-controller}}/ui`
external-ui: .\dashboard
dns:
  enable: true
  ipv6: false
  listen: 127.0.0.1:53
  enhanced-mode: fake-ip
  default-nameserver:
    - 119.29.29.29
    - 119.28.28.28
    - 1.2.4.8
  fake-ip-filter:
    - '*.lan'
    - localhost.ptlogin2.qq.com
  nameserver:
    - https://dns.alidns.com/dns-query
    - https://1.1.1.1/dns-query
    - tls://dns.adguard.com:853
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
    region = ["HK", "TW", "JP", "US", "EA", "XX"]
    regex = ["深港|香港", "台湾|彰化", "日本", "美国", "韩国|新加坡"]
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
    group[0]["type"] = "url-test"
    group[0]["interval"] = 86400
    group[0]["url"] = "http://www.gstatic.com/generate_204"
    group += [
        {"name": "PROXY", "type": "select",
            "proxies": region + ["DIRECT"]},
        {
            "name": "NATIVE",
            "type": "select",
            "proxies": ["DIRECT", "HK", "TW", "JP"],
        },
        # {"name": "CNMEDIA", "type": "select", "proxies": ["DIRECT", "HK", "TW"]},
        {
            "name": "OSMEDIA",
            "type": "select",
            "proxies": ["HK", "TW", "JP", "US", "PROXY"],
        },
        {"name": "MATCH", "type": "select",
            "proxies": ["DIRECT", "PROXY"]},
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

# def parse_url(list):
#     new_list = []
#     for i in list:
#         if i.startswith("ssr://"):
#             pass
#         elif i.startswith("ss://"):
#             pass
#         elif i.startswith("vemss://"):
#             pass
#         elif i.startswith("trojan://"):
#             pass
#         else:
#             continue
#     if len(new_list):
#         return new_list
#     else:
#         raise Exception("No Source Found")

# def parse_ss(string):
#     ss = {"type": "ss"}
#     info = decode_b64(string)
#     pos = info.rfind("#")
#     if pos > 0:
#         info = info[:pos]
#         ss["name"] = info[pos + 1:]
#     info["cipher"], info["password"], info["post"], info["server"] = info.split(
#         ":")


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
