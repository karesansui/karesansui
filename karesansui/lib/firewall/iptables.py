#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2009-2012 HDE, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""<description>
<comment-ja>
ファイアウォールの設定や稼働状況を制御するクラスを定義する
</comment-ja>
<comment-en>
Define the class to control packet filtering.
</comment-en>

@file:  iptables.py
@author: Taizo ITO <taizo@karesansui-project.info>
@copyright:     
"""

import time
import os, stat
import re
import errno
import pprint
from StringIO import StringIO
from xml.dom.minidom import DOMImplementation
implementation = DOMImplementation()

import karesansui
from karesansui.lib.const import FIREWALL_XML_FILE, \
     FIREWALL_USERCHAIN, RH_USERCHAIN, KARESANSUI_GROUP
from karesansui.lib.utils import get_xml_xpath as XMLXpath, \
     get_xml_parse as XMLParse, get_nums_xml_xpath as XMLXpathNum, \
     execute_command, r_chgrp, is_readable
    
from karesansui.lib.networkaddress import NetworkAddress
from karesansui.lib.file.configfile import ConfigFile
from karesansui.lib.virt.virt import KaresansuiVirtException, \
     KaresansuiVirtConnection

class KaresansuiIpTablesException(karesansui.KaresansuiLibException):
    pass

class IptablesXMLGenerator:

    def _create_text_node(self, tag, txt):
        node = self.document.createElement(tag)
        self._add_text(node, txt)
        return node

    def _add_text(self, node, txt):
        txt_n = self.document.createTextNode(txt)
        node.appendChild(txt_n)

    def generate(self,config):
        tree = self.generate_xml_tree(config)
        out = StringIO()
        out.write(tree.toxml('UTF-8'))
        return out.getvalue()

class KaresansuiIpTables(IptablesXMLGenerator):

    def __init__(self):
        self.iptables_conf_file = "/etc/sysconfig/iptables"
        self.firewall_xml_file = FIREWALL_XML_FILE

        self._lsmod = "/sbin/lsmod"
        self._iptables = "/sbin/iptables"
        self._iptables_save = "/sbin/iptables-save"
        self._iptables_init = "/etc/init.d/iptables"

        self.basic_targets = {
               'filter':['ACCEPT','DROP','REJECT'],
               'nat':['ACCEPT','DROP','REJECT','MASQUERADE','REDIRECT','DNAT'],
               'mangle':['ACCEPT','DROP','REJECT'],
              }

        self.basic_chains = {
               'filter':['INPUT','OUTPUT','FORWARD'],
               'nat':['PREROUTING','OUTPUT','POSTROUTING'],
               'mangle':['PREROUTING','INPUT','OUTPUT','FORWARD','POSTROUTING'],
              }

        self.chain_protos = ['tcp','udp','icmp','esp','ah','sctp']

        self.ipt_original_opts = {
                   "append|A": 1,
                   "delete|D": 1,
                   "insert|I": 1,
                   "replace|R": 1,
                   "list|L":0,
                   "flush|F":0,
                   "zero|Z":0,
                   "new-chain|N":1,
                   "delete-chain|X":1,
                   "rename-chain|E":1,
                   "policy|P":1,
                   "source|src|s":1,
                   "destination|dst|d":1,
                   "protocol|p":1,
                   "in-interface|i":1,
                   "jump|j":1,
                   "table|t":1,
                   "match|m":1,
                   "numeric|n":0,
                   "out-interface|o":1,
                   "verbose|v":0,
                   "exact|x":0,
                   "fragments|f":0,
                   "version|V":0,
                   "help|h":0,
                   "line-numbers|0":0,
                   "modprobe|M":0,
                   "set-counters|c":1,
                   "goto|g":1,
              }

        self.ipt_udp_opts = {
             "source-port":1,
             "sport":1,
             "destination-port":1,
             "dport":1,
        }

        self.ipt_tcp_opts = {
             "source-port":1,
             "sport":1,
             "destination-port":1,
             "dport":1,
             "syn":0,
             "tcp-flags":1,
             "tcp-option":1,
        }


        self.ipt_ext_opts = {
             "state":1, # --state [INVALID|ESTABLISHED|NEW|RELATED|UNTRACKED]
             "reject-with":1,
             "mss":1,   # --mss value[:value]
        }

        self.params = {
           "target"     :"target",
           "protocol"   :"protocol",
           "source"     :"source",
           "destination":"destination",
           "sport"      :"source-port",
           "dport"      :"destination-port",
           "inif"       :"in-interface",
           "outif"      :"out-interface",
           "option"     :"option",
        }
        return None

    def firewall_xml__to__iptables_config(self):
        self.firewall_xml = self.read_firewall_xml()
        self.set_default()
        self.write_iptables_config()

    def firewall_xml__from__iptables_config(self):
        self.firewall_xml = self.read_iptables_config()
        self.set_default()
        self.write_firewall_xml()

    def read_iptables_config(self):
        config = {}

        res = []
        if is_readable(self.iptables_conf_file):
            res = ConfigFile(self.iptables_conf_file).read()
            ret = 0
        if len(res) == 0:
            cmd = []
            cmd.append(self._iptables_save)
            (ret,res) = execute_command(cmd)

        table_regex = re.compile(r"""^\*(?P<table>[a-z]+)""")
        policy_regex = re.compile(r"""^:(?P<chain>\S+) (?P<target>\S+)""")
        rule_regex = re.compile(r"""^\-A (?P<rule>\S+)""")
        end_regex = re.compile(r"""^COMMIT$""")

        if ret == 0 and len(res) > 0:
            for aline in res:
                aline = aline.rstrip()
                aline = aline.replace(RH_USERCHAIN,FIREWALL_USERCHAIN)

                m = end_regex.match(aline)
                if m is not None:

                    for chain, policy in policies.iteritems():
                        rule = self._make_rule_arr(rules[chain])
                        info = {"policy": policies[chain], "rule": rule}
                        table_info[chain] = info

                    config[table] = table_info
                    continue

                m = table_regex.match(aline)
                if m is not None:
                    table = m.group("table")
                    table_info = {}
                    policies = {}
                    rules = {}
                else:
                    m = policy_regex.match(aline)
                    if m is not None:
                        chain = m.group("chain")
                        target = m.group("target")
                        policies[chain] = target
                        rules[chain] = []
                    else:
                        m = rule_regex.match(aline)
                        if m is not None:
                            rule_chain = m.group("rule")
                            rules[rule_chain].append(aline)

        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(config)
        return config

    def write_iptables_config(self):
        try:
            self.set_libvirt_rules()
            self.write_firewall_xml()
            ConfigFile(self.iptables_conf_file).write("\n".join(self.make_save_lines()) + "\n")
        except:
            raise KaresansuiIpTablesException("Error: Cannot write iptables configuration file.")

    def _make_rule_arr(self,rules):
        arr = []
        for aline in rules:
            arr.append(self._rule_str_to_arr(aline))
        return arr

    def _rule_str_to_arr(self,string,rule_id=None):
        #print string
        m_re = re.compile(r"""(^| )-{1,2}(?P<opt>\S+) ?(?P<value>(\! )?\S+)?""", flags=0)
        for k,v in self.params.iteritems():
            exec("%s = ''" % (k,))

        for itr in m_re.finditer(string):
            opt = itr.group('opt')
            value = itr.group('value')
            if opt == 'A' or opt == 'append':
                continue
            elif opt == 'j' or opt == 'jump':
                target = value
            elif opt == 'p' or opt == 'protocol':
                protocol = value
            elif opt == 's' or opt == 'src' or opt == 'source':
                source = value
            elif opt == 'd' or opt == 'dst' or opt == 'destination':
                destination = value
            elif opt == 'sport' or opt == 'source-port':
                sport = value
            elif opt == 'dport' or opt == 'destination-port':
                dport = value
            elif opt == 'i' or opt == 'in-interface':
                inif = value
            elif opt == 'o' or opt == 'out-interface':
                outif = value
            else:
                if len(opt) == 1:
                    opt = "-%s" % opt
                else:
                    opt = "--%s" % opt
                if option is None:
                    option = ""
                option = "%s %s %s" % (option, opt, value,)

        rule_info = {"id": rule_id,
                     "target": target,
                     "protocol": protocol,
                     "source": source,
                     "destination": destination,
                     "source-port": sport,
                     "destination-port": dport,
                     "in-interface": inif,
                     "out-interface": outif,
                     "option": option,
                    }

        return rule_info


    def read_firewall_xml(self,path=None):

        config = {}

        if path is None:
            path = self.firewall_xml_file

        if not os.path.exists(path) or os.path.getsize(path) == 0:
            raise KaresansuiIpTablesException("no such file: %s" % path)

        document = XMLParse(path)
        
        table_num = XMLXpathNum(document,'/firewall/table')
        for tbl in range(1, table_num + 1):
            table_name = XMLXpath(document,'/firewall/table[%i]/@name' % (tbl,))
            if table_name is None:
                table_name = 'filter'

            chain = {}
            chain_num = XMLXpathNum(document,'/firewall/table[%i]/chain' % (tbl,))
            for chn in range(1, chain_num + 1):
                chain_name = XMLXpath(document,'/firewall/table[%i]/chain[%i]/@name' % (tbl,chn,))
                chain_policy = XMLXpath(document,'/firewall/table[%i]/chain[%i]/@policy' % (tbl,chn,))

                rule = []
                rule_num = XMLXpathNum(document,'/firewall/table[%i]/chain[%i]/rule' % (tbl,chn,))
                for rl in range(1, rule_num + 1):
                    rule_id = XMLXpath(document,'/firewall/table[%i]/chain[%i]/rule[%i]/@id' % (tbl,chn,rl,))

                    target = XMLXpath(document,'/firewall/table[%i]/chain[%i]/rule[%i]/target/text()' % (tbl,chn,rl,))
                    if target is None:
                        target = ''
                    else:
                        target = target.strip()

                    protocol = XMLXpath(document,'/firewall/table[%i]/chain[%i]/rule[%i]/protocol/text()' % (tbl,chn,rl,))
                    if protocol is None:
                        protocol = ''
                    else:
                        protocol = protocol.strip()
                        if protocol == "50":
                            protocol = "esp"
                        if protocol == "51":
                            protocol = "ah"

                    source = XMLXpath(document,'/firewall/table[%i]/chain[%i]/rule[%i]/source/text()' % (tbl,chn,rl,))
                    if source is None:
                        source = ''
                    else:
                        source = source.strip()

                    destination = XMLXpath(document,'/firewall/table[%i]/chain[%i]/rule[%i]/destination/text()' % (tbl,chn,rl,))
                    if destination is None:
                        destination = ''
                    else:
                        destination = destination.strip()

                    sport = XMLXpath(document,'/firewall/table[%i]/chain[%i]/rule[%i]/source-port/text()' % (tbl,chn,rl,))
                    if sport is None:
                        sport = ''
                    else:
                        sport = sport.strip()

                    dport = XMLXpath(document,'/firewall/table[%i]/chain[%i]/rule[%i]/destination-port/text()' % (tbl,chn,rl,))
                    if dport is None:
                        dport = ''
                    else:
                        dport = dport.strip()

                    inif = XMLXpath(document,'/firewall/table[%i]/chain[%i]/rule[%i]/in-interface/text()' % (tbl,chn,rl,))
                    if inif is None:
                        inif = ''
                    else:
                        inif = inif.strip()

                    outif = XMLXpath(document,'/firewall/table[%i]/chain[%i]/rule[%i]/out-interface/text()' % (tbl,chn,rl,))
                    if outif is None:
                        outif = ''
                    else:
                        outif = outif.strip()

                    option = XMLXpath(document,'/firewall/table[%i]/chain[%i]/rule[%i]/option/text()' % (tbl,chn,rl,))
                    if option is None:
                        option = ''
                    else:
                        option = option.strip()

                    rule_info = {"id": rule_id,
                        "target": target,
                        "protocol": protocol,
                        "source": source,
                        "destination": destination,
                        "source-port": sport,
                        "destination-port": dport,
                        "in-interface": inif,
                        "out-interface": outif,
                        "option": option,
                       }

                    rule.append(rule_info)

                chain_info = {"policy": chain_policy,
                        "rule": rule,
                       }
                chain[chain_name] = chain_info

            config[table_name] = chain

        return config

    def generate_xml_tree(self, config):
        self.firewall_xml = config

        self.begin_build()
        for tbl,val in self.firewall_xml.iteritems():
            self.build_table(tbl)
        self.end_build()

        return self.document

    def begin_build(self):
        self.document = implementation.createDocument(None,None,None)
        self.firewall = self.document.createElement("firewall")

        self.firewall.setAttribute("type", "iptables")
        self.firewall.appendChild(self._create_text_node("last_modified", "%s" % time.ctime()))
        self.document.appendChild(self.firewall)

    def build_table(self,name):
        doc = self.document
        table = doc.createElement("table")
        table.setAttribute("name", name)

        chains = self.firewall_xml[name]
        for chain_name,val in chains.iteritems():
            chain_n = doc.createElement("chain")
            chain_n.setAttribute("name", chain_name)
            try:
                if val['policy'] is not None:
                    chain_n.setAttribute("policy", val['policy'])
            except:
                pass

            cnt = 1
            for rule in val["rule"]:
                rule_n = doc.createElement("rule")
                rule_n.setAttribute("id", str(cnt))

                if rule["target"] is not None:
                    target = self._create_text_node("target", rule["target"])
                    rule_n.appendChild(target)

                try:
                    if rule["protocol"] is not None and rule["protocol"] != "":
                        protocol = self._create_text_node("protocol", rule["protocol"])
                        rule_n.appendChild(protocol)
                except:
                    pass

                try:
                    if rule["source"] is not None and rule["source"] != "" :
                        source = self._create_text_node("source", rule["source"])
                        rule_n.appendChild(source)
                except:
                    pass

                try:
                    if rule["destination"] is not None and rule["destination"] != "":
                        destination = self._create_text_node("destination", rule["destination"])
                        rule_n.appendChild(destination)
                except:
                    pass

                try:
                    if rule["source-port"] is not None and rule["source-port"] != "":
                        sport = self._create_text_node("source-port", rule["source-port"])
                        rule_n.appendChild(sport)
                except:
                    pass

                try:
                    if rule["destination-port"] is not None and rule["destination-port"] != "":
                        dport = self._create_text_node("destination-port", rule["destination-port"])
                        rule_n.appendChild(dport)
                except:
                    pass

                try:
                    if rule["in-interface"] is not None and rule["in-interface"] != "":
                        inif = self._create_text_node("in-interface", rule["in-interface"])
                        rule_n.appendChild(inif)
                except:
                    pass

                try:
                    if rule["out-interface"] is not None and rule["out-interface"] != "":
                        outif = self._create_text_node("out-interface", rule["out-interface"])
                        rule_n.appendChild(outif)
                except:
                    pass

                try:
                    if rule["option"] is not None and rule["option"] != "":
                        option = self._create_text_node("option", rule["option"])
                        rule_n.appendChild(option)
                except:
                    pass

                chain_n.appendChild(rule_n)
                cnt = cnt + 1
 
            table.appendChild(chain_n)

        self.firewall.appendChild(table)


    def end_build(self):
        pass

    def write_firewall_xml(self,path=None):
        if path is None:
            path = self.firewall_xml_file
        try:
            pathdir = os.path.dirname(path)
            os.makedirs(pathdir)
        except OSError, (err, msg):
            if err != errno.EEXIST:
                raise OSError(err,msg)

        #print self.generate(self.firewall_xml)
        ConfigFile(path).write(self.generate(self.firewall_xml))
        if os.getuid() == 0 and os.path.exists(path):
            r_chgrp(path,KARESANSUI_GROUP)
            os.chmod(path,0664)

    def make_save_lines(self):
        lines = []
        lines.append("# Generated by karesansui on %s" % (time.ctime(),))
        for tbl,tbl_val in self.firewall_xml.iteritems():
            lines.append("*%s" % (tbl,))

            # policy
            for chn,chn_val in tbl_val.iteritems():
                try:
                    policy = chn_val['policy']
                except:
                    policy = '-'
                if policy is None:
                    policy = '-'
                lines.append(":%s %s" % (chn,policy,))

            # rule
            for chn,chn_val in tbl_val.iteritems():
                try:
                    rules = chn_val['rule']
                except:
                    continue

                for rule in rules:
                    rule_s = []
                    try:
                        target = rule["target"]
                    except:
                        target = 'ACCEPT'

                    try:
                        protocol = rule["protocol"]
                    except:
                        protocol = None
                    if protocol is not None and protocol.strip() != "":
                        rule_s.append("--protocol %s" % protocol)

                    try:
                        option = rule["option"]
                    except:
                        option = None

                    loption = ""
                    if option is not None:
                        extopt_regex = re.compile(r"((--reject-with) *(\S+))")
                        for m in extopt_regex.finditer(option):
                            loption = "%s %s" % (loption, m.group(1),)

                        option = extopt_regex.sub('',option,0)
                        rule_s.append(option)

                    try:
                        source = rule["source"]
                    except:
                        source = None
                    if source is not None and source.strip() != "":
                        rule_s.append("--source %s" % source)

                    try:
                        destination = rule["destination"]
                    except:
                        destination = None
                    if destination is not None and destination.strip() != "":
                        rule_s.append("--destination %s" % destination)

                    try:
                        sport = rule["source-port"]
                    except:
                        sport = None
                    if sport is not None and sport.strip() != "":
                        rule_s.append("--source-port %s" % sport)

                    try:
                        dport = rule["destination-port"]
                    except:
                        dport = None
                    if dport is not None and dport.strip() != "":
                        rule_s.append("--destination-port %s" % dport)

                    try:
                        inif = rule["in-interface"]
                    except:
                        inif = None
                    if inif is not None and inif.strip() != "":
                        rule_s.append("--in-interface %s" % inif)

                    try:
                        outif = rule["out-interface"]
                    except:
                        outif = None
                    if outif is not None and outif.strip() != "":
                        rule_s.append("--out-interface %s" % outif)

                    rule_s.append("--jump %s" % target)

                    if loption is not "":
                        rule_s.append(loption)

                    lines.append("-A %s %s" % (chn, " ".join(rule_s)))

            lines.append("COMMIT")
        lines.append("# Completed on %s" % (time.ctime(),))
        return lines

    def set_default(self):

        try:
            self.firewall_xml['filter']
        except:
            self.firewall_xml['filter'] = {}

        try:
            self.firewall_xml['filter'][FIREWALL_USERCHAIN]
        except:
            self.firewall_xml['filter'][FIREWALL_USERCHAIN] = {}

        try:
            self.firewall_xml['filter'][FIREWALL_USERCHAIN]['rule']
        except:
            self.firewall_xml['filter'][FIREWALL_USERCHAIN] = {}
            rules = []

            rules.append({
                          'target':'ACCEPT',
                          'in-interface':'lo',
                        })
            """
            rules.append({
                          'target':'ACCEPT',
                          'protocol':'icmp',
                          'option':'-m icmp --icmp-type any',
                        })
            rules.append({
                          'target':'ACCEPT',
                          'protocol':'esp',
                        })
            rules.append({
                          'target':'ACCEPT',
                          'protocol':'ah',
                        })
            rules.append({
                          'target':'ACCEPT',
                          'option':'-m state --state RELATED,ESTABLISHED',
                        })
            rules.append({
                          'target':'REJECT',
                          'option':'--reject-with icmp-host-prohibited',
                        })
            """
            chain_info = {'rule':rules}
            self.firewall_xml['filter'][FIREWALL_USERCHAIN] = chain_info

        try:
            self.firewall_xml['filter']['INPUT']['rule']
        except:
            try:
                policy = self.firewall_xml['filter']['INPUT']['policy']
            except:
                policy = 'ACCEPT'
            self.firewall_xml['filter']['INPUT'] = {}
            rules = []
            rules.append({'target':FIREWALL_USERCHAIN,
                        })
            chain_info = {'policy':policy,'rule':rules}
            self.firewall_xml['filter']['INPUT'] = chain_info

        try:
            self.firewall_xml['filter']['FORWARD']['rule']
        except:
            try:
                policy = self.firewall_xml['filter']['FORWARD']['policy']
            except:
                policy = 'ACCEPT'
            self.firewall_xml['filter']['FORWARD'] = {}
            rules = []
            rules.append({'target':FIREWALL_USERCHAIN,
                        })
            chain_info = {'policy':policy,'rule':rules}
            self.firewall_xml['filter']['FORWARD'] = chain_info

        try:
            self.firewall_xml['filter']['OUTPUT']['rule']
        except:
            try:
                policy = self.firewall_xml['filter']['OUTPUT']['policy']
            except:
                policy = 'ACCEPT'
            self.firewall_xml['filter']['OUTPUT'] = {}
            rules = []
            chain_info = {'policy':policy,'rule':rules}
            self.firewall_xml['filter']['OUTPUT'] = chain_info

    def _modify_policy(self,table,chain,policy):
        if policy is None:
            self.firewall_xml[table][chain]['policy'] = None 
        elif policy != "":
            self.firewall_xml[table][chain]['policy'] = policy

    def _get_rules(self,table,chain):
        try:
            new_rules = []
            cnt = 1
            for rule in self.firewall_xml[table][chain]['rule']:

                for k,v in self.params.iteritems():
                    try: 
                        exec("%s = rule['%s']" % (k,v,))
                    except KeyError:
                        exec("%s = ''" % (k,))

                rule_info = {"id": cnt,
                        "target": target,
                        "protocol": protocol,
                        "source": source,
                        "destination": destination,
                        "source-port": sport,
                        "destination-port": dport,
                        "in-interface": inif,
                        "out-interface": outif,
                        "option": option,
                       }
                cnt = cnt + 1
                new_rules.append(rule_info)
            return new_rules
        except:
            return []

    def _search_rule(self,table,chain,conditions):

        ret = []
        try:
            rules = self.firewall_xml[table][chain]['rule']
            cnt = 1
            for rule in rules:

                match=True
                for k,v in conditions.iteritems():
                    try:
                        if rule[k] != v:
                            match=False
                    except:
                        match=False

                if match is True:
                    ret.append(cnt)
                cnt = cnt + 1
        except KeyError:
            return ret

        return ret

    def _add_rule(self,table,chain,rule_info):

        try:
            self.firewall_xml[table][chain]['rule']
        except KeyError:
            try:
                self.firewall_xml[table][chain]
            except KeyError:
                try:
                    self.firewall_xml[table]
                except KeyError:
                    self.firewall_xml[table] = {}
                self.firewall_xml[table][chain] = {}
            self.firewall_xml[table][chain]['rule'] = []

        rules = self.firewall_xml[table][chain]['rule']

        for k,v in self.params.iteritems():
            try: 
                exec("%s = rule_info['%s']" % (k,v,))
            except KeyError:
                exec("%s = ''" % (k,))

        if not target in self.basic_targets[table]:
            raise KaresansuiIpTablesException("no such target: %s" % target)

        n_rule_info = {"target": target,
                       "protocol": protocol,
                       "source": source,
                       "destination": destination,
                       "source-port": sport,
                       "destination-port": dport,
                       "in-interface": inif,
                       "out-interface": outif,
                       "option": option,
                      }

        rules.append(n_rule_info)
        self.firewall_xml[table][chain]['rule'] = rules
        return len(rules)

    def _delete_rule(self,table,chain,id):
        ret = []
        rules = self.firewall_xml[table][chain]['rule']
        new_rules = []
        cnt = 1
        for rule in rules:
            if id == cnt:
                ret = rule
            else:
                new_rules.append(rule)
            cnt = cnt + 1

        self.firewall_xml[table][chain]['rule'] = new_rules
        return ret

    def _modify_rule(self,table,chain,id,rule_info):
        rules = self.firewall_xml[table][chain]['rule']

        for k,v in self.params.iteritems():
            try: 
                exec("%s = rule_info['%s']" % (k,v,))
            except KeyError:
                exec("%s = ''" % (k,))

        if not target in self.basic_targets[table]:
            raise KaresansuiIpTablesException("no such target: %s" % target)

        n_rule_info = {"target": target,
                       "protocol": protocol,
                       "source": source,
                       "destination": destination,
                       "source-port": sport,
                       "destination-port": dport,
                       "in-interface": inif,
                       "out-interface": outif,
                       "option": option,
                      }

        new_rules = []
        cnt = 1
        for rule in rules:
            if id == cnt:
                rule = n_rule_info
            new_rules.append(rule)
            cnt = cnt + 1

        self.firewall_xml[table][chain]['rule'] = new_rules
        return id

    def _insert_rule(self,table,chain,id,rule_info):

        try:
            self.firewall_xml[table][chain]['rule']
        except KeyError:
            try:
                self.firewall_xml[table][chain]
            except KeyError:
                try:
                    self.firewall_xml[table]
                except KeyError:
                    self.firewall_xml[table] = {}
                self.firewall_xml[table][chain] = {}
            self.firewall_xml[table][chain]['rule'] = []

        rules = self.firewall_xml[table][chain]['rule']

        for k,v in self.params.iteritems():
            try: 
                exec("%s = rule_info['%s']" % (k,v,))
            except KeyError:
                exec("%s = ''" % (k,))

        if not target in self.basic_targets[table]:
            raise KaresansuiIpTablesException("no such target: %s" % target)

        n_rule_info = {"target": target,
                       "protocol": protocol,
                       "source": source,
                       "destination": destination,
                       "source-port": sport,
                       "destination-port": dport,
                       "in-interface": inif,
                       "out-interface": outif,
                       "option": option,
                      }

        new_rules = []
        cnt = 1
        for rule in rules:
            if id == cnt:
                new_rules.append(n_rule_info)
            new_rules.append(rule)
            cnt = cnt + 1
        if len(rules) == 0:
            new_rules.append(n_rule_info)

        if len(rules) == len(new_rules):
            new_rules.append(n_rule_info)
            id = len(new_rules)

        self.firewall_xml[table][chain]['rule'] = new_rules
        return id

    def modify_policy(self,chain,policy=None):
        self._modify_policy('filter',chain,policy)

    def get_rules(self):
        return self._get_rules('filter',FIREWALL_USERCHAIN)

    def add_rule(self,rule_info):
        return self._add_rule('filter',FIREWALL_USERCHAIN,rule_info)

    def delete_rule(self,id):
        return self._delete_rule('filter',FIREWALL_USERCHAIN,id)

    def modify_rule(self,id,rule_info):
        return self._modify_rule('filter',FIREWALL_USERCHAIN,id,rule_info)

    def insert_rule(self,id,rule_info):
        return self._insert_rule('filter',FIREWALL_USERCHAIN,id,rule_info)

    def is_configured(self):
        if os.path.exists(self.firewall_xml_file):
            ctime2 = time.ctime(os.stat(self.firewall_xml_file).st_mtime)
        else:
            return True

        if os.path.exists(self.iptables_conf_file):
            ctime1 = time.ctime(os.stat(self.iptables_conf_file).st_mtime)
            if ctime1 < ctime2:
                return False
            else:
                return True
        else:
            return False

    def set_libvirt_rules(self):

        kvc = KaresansuiVirtConnection()
        try:
            for name in kvc.list_active_network():
                try:
                    network = kvc.search_kvn_networks(name)[0]

                    info = network.get_info()
                    bridge = info['bridge']['name']
                    ipaddr = info['ip']['address']
                    netmask = info['ip']['netmask']
                    netaddr = NetworkAddress("%s/%s" % (ipaddr,netmask)).get('network')

                    # nat mode
                    if info['forward']['mode'] == 'nat':

                        # rule 1
                        # -A POSTROUTING -s 192.168.122.0/255.255.255.0 -d ! 192.168.122.0/255.255.255.0 -j MASQUERADE 
                        conditions = {'target':'MASQUERADE',
                                      'source':"%s/%s" % (netaddr,netmask),
                                      'destination':"! %s/%s" % (netaddr,netmask),
                                     }
                        ids = self._search_rule('nat','POSTROUTING',conditions)
                        if len(ids) == 0:
                            id = self._insert_rule('nat','POSTROUTING',1,conditions)

                        # rule 2
                        # -A FORWARD -d 192.168.122.0/255.255.255.0 -o virbr0 -m state --state RELATED,ESTABLISHED -j ACCEPT 
                        conditions = {'target':'ACCEPT',
                                      'destination':"%s/%s" % (netaddr,netmask),
                                      'out-interface':bridge,
                                     }
                        ids = self._search_rule('filter','FORWARD',conditions)
                        if len(ids) == 0:
                            conditions['option'] = '-m state --state RELATED,ESTABLISHED'
                            id = self._insert_rule('filter','FORWARD',1,conditions)

                        # rule 3
                        # -A FORWARD -s 192.168.122.0/255.255.255.0 -i virbr0 -j ACCEPT 
                        conditions = {'target':'ACCEPT',
                                      'source':"%s/%s" % (netaddr,netmask),
                                      'in-interface':bridge,
                                     }
                        ids = self._search_rule('filter','FORWARD',conditions)
                        if len(ids) == 0:
                            id = self._insert_rule('filter','FORWARD',1,conditions)

                    # rule 4
                    # -A INPUT -i virbr0 -p udp -m udp --dport 53 -j ACCEPT 
                    # -A INPUT -i virbr0 -p tcp -m tcp --dport 53 -j ACCEPT 
                    # -A INPUT -i virbr0 -p udp -m udp --dport 67 -j ACCEPT 
                    # -A INPUT -i virbr0 -p tcp -m tcp --dport 67 -j ACCEPT 
                    default_port = {'53':['udp','tcp'],
                                    '67':['udp','tcp'],
                                    }
                    for port,v in default_port.iteritems():
                        for protocol in v:

                            conditions = {'target':'ACCEPT',
                                          'protocol':protocol,
                                          'destination-port':port,
                                          'in-interface':bridge,
                                         }
                            ids = self._search_rule('filter','INPUT',conditions)
                            if len(ids) == 0:
                                conditions['option'] = "-m %s" % protocol
                                id = self._insert_rule('filter','INPUT',1,conditions)

                except KaresansuiVirtException, e:
                    pass
        finally:
            kvc.close()

        return True

    def is_running(self):
        return self.status()

    def start(self):
        cmd = []
        cmd.append(self._iptables_init)
        cmd.append('start')
        (ret,res) = execute_command(cmd)
        return ret

    def stop(self):
        cmd = []
        cmd.append(self._iptables_init)
        cmd.append('stop')
        (ret,res) = execute_command(cmd)
        return ret

    def restart(self):
        cmd = []
        cmd.append(self._iptables_init)
        cmd.append('restart')
        (ret,res) = execute_command(cmd)
        return ret

    def condrestart(self):
        ret = 0
        if self.status() is True:
            cmd = []
            cmd.append(self._iptables_init)
            cmd.append('restart')
            (ret,res) = execute_command(cmd)
        return ret

    def status(self):

        kmod_regex = re.compile(r"""^(ip_tables|iptable_filter|iptable_nat)[ \t]""")
        cmd = []
        cmd.append(self._lsmod)
        (ret,res) = execute_command(cmd)
        if len(res) > 0:
            for aline in res:
                m = kmod_regex.match(aline)
                if m:
                    return True
        return False

"""
pp = pprint.PrettyPrinter(indent=4)
kit = KaresansuiIpTables()
pp.pprint(kit.firewall_xml)
#pp.pprint(kit.firewall_xml)
#pp.pprint(kit.read_iptables_config())
config = kit.firewall_xml
#print kit.generate(config)
#pp.pprint(kit.make_save_lines())
print "\n".join(kit.make_save_lines())

pp = pprint.PrettyPrinter(indent=4)
kit = KaresansuiIpTables()
kit.set_libvirt_rules()
"""
