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

import os
import math
import karesansui

DEFAULT_LANGS = {
    "ja_JP": {'DATE_FORMAT' : ("%Y/%m/%d", "%Y/%m/%d %H:%M:%S", "yy-mm-dd")},
    "en_US": {'DATE_FORMAT' : ("%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "mm-dd-yy")},
#    "de_DE": {'DATE_FORMAT' : ("%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "mm-dd-yy")},
#    "es_ES": {'DATE_FORMAT' : ("%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "mm-dd-yy")},
#    "fr_FR": {'DATE_FORMAT' : ("%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "mm-dd-yy")},
#    "it_IT": {'DATE_FORMAT' : ("%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "mm-dd-yy")},
#    "ko_KR": {'DATE_FORMAT' : ("%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "mm-dd-yy")},
#    "pt_BR": {'DATE_FORMAT' : ("%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "mm-dd-yy")},
#    "ru_RU": {'DATE_FORMAT' : ("%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "mm-dd-yy")},
#    "zh_CN": {'DATE_FORMAT' : ("%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "mm-dd-yy")},
}

DEFAULT_DATE_FORMAT = ("%m/%d/%Y", "%m/%d/%Y %H:%M:%S", "mm/dd/yy", "%Y/%m/%d %H:%M")

# define karesansui paths & users
KARESANSUI_USER  = "kss"
KARESANSUI_GROUP = "kss"
KARESANSUI_PREFIX = "/var/lib/karesansui"
KARESANSUI_TMP_DIR     = KARESANSUI_PREFIX + "/tmp"
KARESANSUI_SYSCONF_DIR = "/etc/karesansui"
KARESANSUI_DATA_DIR    = "/var/lib/karesansui"

MACHINE_ATTRIBUTE = {'HOST':0,
                     'GUEST':1,
                     'URI':2,
                    }
MACHINE_HYPERVISOR = {'REAL':0,
                      'XEN':1,
                      'KVM':2,
                      'URI':3,
                     }

# define vendor paths
VENDOR_PREFIX      = "/usr"
VENDOR_BIN_DIR     = VENDOR_PREFIX + "/bin"
VENDOR_SBIN_DIR    = VENDOR_PREFIX + "/sbin"
VENDOR_SYSCONF_DIR = "/etc"
VENDOR_DATA_DIR    = "/var/lib"
VENDOR_DATA_ISCSI_DIR = "/var/lib/iscsi"
VENDOR_DATA_ISCSI_MOUNT_DIR = VENDOR_DATA_ISCSI_DIR + "/mount"
VENDOR_DATA_ISCSI_DOMAINS_DIR = VENDOR_DATA_ISCSI_DIR + "/domains"
VENDOR_DATA_BONDING_EVACUATION_DIR = "/var/lib/karesansui/ifcfg"
VENDOR_LIBVIRT_RUN_DIR = "/var/run/libvirt"
XEN_SYSCONF_DIR    = "/etc/xen"

#LOGOUT_FILE_PREFIX = "%s/logout." % karesansui.config['application.tmp.dir']
LOGOUT_FILE_PREFIX = KARESANSUI_TMP_DIR + "/logout."
ICON_DIR_TPL = "%s/static/icon/%s"
MSG_LIMIT = 5
TAG_CLIPPING_RANGE = 12
MACHINE_NAME_CLIPPING_RANGE = 20

DEFAULT_LIST_RANGE = 10
JOB_LIST_RANGE = DEFAULT_LIST_RANGE
USER_LIST_RANGE = DEFAULT_LIST_RANGE
TAG_LIST_RANGE = DEFAULT_LIST_RANGE
WATCH_LIST_RANGE = DEFAULT_LIST_RANGE
MAILTEMPLATE_LIST_RANGE = DEFAULT_LIST_RANGE

# use for virt library
VIRT_LIBVIRT_DATA_DIR    = "/var/lib/libvirt"
VIRT_XENDOMAINS_AUTO_DIR = XEN_SYSCONF_DIR + "/auto"

VIRT_LIBVIRT_SOCKET_RW = VENDOR_LIBVIRT_RUN_DIR + "/libvirt-sock";
VIRT_LIBVIRT_SOCKET_RO = VENDOR_LIBVIRT_RUN_DIR + "/libvirt-sock-ro";

# kvm
KVM_VIRTUAL_DISK_PREFIX = "hd"
KVM_VIRT_CONFIG_DIR  = "/etc/karesansui/virt/kvm"
#KVM_VIRT_URI_RW = "qemu+tls://127.0.0.1:16514/system?no_verify=1"
#KVM_VIRT_URI_RO = "qemu+tls://127.0.0.1:16514/system?no_verify=1"
KVM_VIRT_URI_RW = "qemu+tcp://127.0.0.1:16509/system"
KVM_VIRT_URI_RO = "qemu+tcp://127.0.0.1:16509/system"
KVM_KARESANSUI_TMP_DIR = KARESANSUI_TMP_DIR + "/kvm"
if os.path.exists('/usr/share/qemu-kvm/keymaps'):
    KVM_KEYMAP_DIR = '/usr/share/qemu-kvm/keymaps'
else:
    KVM_KEYMAP_DIR = '/usr/share/kvm/keymaps'
#KVM_BRIDGE_PREFIX = "(eth|bondbr)"
KVM_BRIDGE_PREFIX = "br"

# xen
XEN_VIRTUAL_DISK_PREFIX = "xvd"
XEN_VIRT_CONFIG_DIR  = "/etc/karesansui/virt/xen"
XEN_VIRT_URI_RW = "xen:///?socket=" + VIRT_LIBVIRT_SOCKET_RW
XEN_VIRT_URI_RO = "xen:///?socket=" + VIRT_LIBVIRT_SOCKET_RO
XEN_KARESANSUI_TMP_DIR = KARESANSUI_TMP_DIR + "/xen"
XEN_KEYMAP_DIR = '/usr/share/xen/qemu/keymaps'

VIRT_XML_CONFIG_DIR  = VENDOR_SYSCONF_DIR + "/libvirt/qemu"

VIRT_SYSCONF_DIR = VENDOR_SYSCONF_DIR + "/libvirt"
OLD_VIRT_DISK_DIR       = VIRT_LIBVIRT_DATA_DIR + "/disk"
OLD_VIRT_DISK_IMAGE_DIR = VIRT_LIBVIRT_DATA_DIR + "/images"
OLD_VIRT_BOOT_IMAGE_DIR = VIRT_LIBVIRT_DATA_DIR + "/boot"
OLD_VIRT_SNAPSHOT_DIR   = VIRT_LIBVIRT_DATA_DIR + "/snapshot"
VIRT_DOMAINS_DIR        = VIRT_LIBVIRT_DATA_DIR + "/domains"
VIRT_QEMU_DIR           = VIRT_LIBVIRT_DATA_DIR + "/qemu"
VIRT_SNAPSHOT_DIR       = VIRT_QEMU_DIR + "/snapshot"
VIRT_NETWORK_CONFIG_DIR = VIRT_SYSCONF_DIR + "/qemu/networks"
VIRT_AUTOSTART_CONFIG_DIR = VIRT_SYSCONF_DIR + "/qemu/autostart"
VIRT_LIBVIRTD_CONFIG_FILE = VIRT_SYSCONF_DIR + "/libvirtd.conf"
VIRT_STORAGE_CONFIG_DIR = VIRT_SYSCONF_DIR + "/storage"
VIRT_STORAGE_AUTOSTART_CONFIG_DIR = VIRT_SYSCONF_DIR + "/storage/autostart"

# virt command
VIRT_COMMAND_APPLY_SNAPSHOT = "apply_snapshot.py"
VIRT_COMMAND_CREATE_GUEST = "create_guest.py"
VIRT_COMMAND_DELETE_GUEST = "delete_guest.py"
VIRT_COMMAND_DELETE_SNAPSHOT = "delete_snapshot.py"
VIRT_COMMAND_GET_MEMORY_USAGE = "get_memory_usage.py"
VIRT_COMMAND_SET_MEMORY = "set_memory.py"
VIRT_COMMAND_START_GUEST = "start_guest.py"
VIRT_COMMAND_REBOOT_GUEST = "reboot_guest.py"
VIRT_COMMAND_DESTROY_GUEST = "destroy_guest.py"
VIRT_COMMAND_AUTOSTART_GUEST = "autostart_guest.py"
VIRT_COMMAND_CREATE_NETWORK = "create_network.py"
VIRT_COMMAND_DELETE_NETWORK = "delete_network.py"
VIRT_COMMAND_UPDATE_NETWORK = "update_network.py"
VIRT_COMMAND_REPLICATE_GUEST = "replicate_guest.py"
VIRT_COMMAND_EXPORT_GUEST = "export_guest.py"
VIRT_COMMAND_IMPORT_GUEST = "import_guest.py"
VIRT_COMMAND_DELETE_EXPORT_DATA = "delete_export_data.py"
VIRT_COMMAND_SET_VCPUS = "set_vcpus.py"
VIRT_COMMAND_SUSPEND_GUEST = "suspend_guest.py"
VIRT_COMMAND_ADD_DISK = "add_disk.py"
VIRT_COMMAND_APPEND_DISK = "append_disk.py"
VIRT_COMMAND_DELETE_DISK = "delete_disk.py"
VIRT_COMMAND_ADD_NIC = "add_nic.py"
VIRT_COMMAND_DELETE_NIC = "delete_nic.py"
VIRT_COMMAND_CPUTOP = "cputop.py"
VIRT_COMMAND_GET_CPU_USAGE = "get_cpu_usage.py"
VIRT_COMMAND_RESUME_GUEST = "resume_guest.py"
VIRT_COMMAND_SHUTDOWN_GUEST = "shutdown_guest.py"
VIRT_COMMAND_TAKE_SNAPSHOT = "take_snapshot.py"
VIRT_COMMAND_SET_MAC_ADDRESS = "set_mac_address.py"
VIRT_COMMAND_SET_GRAPHICS = "set_graphics.py"
FIREWALL_COMMAND_SAVE_FIREWALL = "save_firewall.py"
FIREWALL_COMMAND_RESTORE_FIREWALL = "restore_firewall.py"
UPDATE_COMMAND_SOFTWARE="update_software.py"
VIRT_COMMAND_CREATE_STORAGE_POOL = "create_storage_pool.py"
VIRT_COMMAND_DELETE_STORAGE_POOL = "delete_storage_pool.py"
VIRT_COMMAND_START_STORAGE_POOL = "start_storage_pool.py"
VIRT_COMMAND_DESTROY_STORAGE_POOL = "destroy_storage_pool.py"
VIRT_COMMAND_CREATE_STORAGE_VOLUME = "create_storage_volume.py"
VIRT_COMMAND_DELETE_STORAGE_VOLUME = "delete_storage_volume.py"
VIRT_COMMAND_REPLICATE_STORAGE_VOLUME = "replicate_storage_volume.py"
ISCSI_COMMAND_GET = "get_iscsi.py"
ISCSI_COMMAND_ADD = "add_iscsi.py"
ISCSI_COMMAND_DELETE = "delete_iscsi.py"
ISCSI_COMMAND_START = "start_iscsi.py"
ISCSI_COMMAND_STOP = "stop_iscsi.py"
ISCSI_COMMAND_UPDATE = "update_iscsi.py"
CONFIGURE_COMMAND_READ = "read_conf.py"
CONFIGURE_COMMAND_WRITE = "write_conf.py"
IPTABLES_COMMAND_CONTROL = "control_iptables.py"
SERVICE_COMMAND_START = "start_service.py"
SERVICE_COMMAND_STOP = "stop_service.py"
SERVICE_COMMAND_RESTART = "restart_service.py"
SERVICE_COMMAND_AUTOSTART = "autostart_service.py"
ISCSI_COMMAND_READY_MOUNT = "ready_mount.py"
BONDING_COMMAND_ADD = "add_bonding.py"
BONDING_COMMAND_DELETE = "delete_bonding.py"
NETWORK_COMMAND_RESTART = "restart_network_interface.py"

# use for firewall library
FIREWALL_XML_FILE  = KARESANSUI_SYSCONF_DIR + "/firewall.xml"
FIREWALL_USERCHAIN = "KARESANSUI-Firewall"
RH_USERCHAIN = "RH-Firewall-1-INPUT"

# Proxy Server use Status
PROXY_ENABLE = '1'
PROXY_DISABLE = '0'

# port number
PORT_MIN_NUMBER = 1
PORT_MAX_NUMBER = 65535
WELKNOWN_PORT_MIN_NUMBER = 1
WELKNOWN_PORT_MAX_NUMBER = 1024
UNKNOWN_PORT_MIN_NUMBER = 1025
UNKNOWN_PORT_MAX_NUMBER = 65535
GRAPHICS_PORT_MIN_NUMBER = 5900
GRAPHICS_PORT_MAX_NUMBER = PORT_MAX_NUMBER
ENABLE_GRAPHICS_TYPE = ['vnc','spice']

# input value length
ID_MIN_LENGTH = 1
ID_MAX_LENGTH = int(math.pow(2, 31)) - 1  # signed int max (2^31-1) SQLAlchemy SQLType.Integer
USER_MIN_LENGTH = 1
USER_MAX_LENGTH = 16
EMAIL_MIN_LENGTH = 1 + 1 + 4
EMAIL_MAX_LENGTH = 256
PASSWORD_MIN_LENGTH = 5
PASSWORD_MAX_LENGTH = 40
LANGUAGES_MIN_LENGTH = 1
LANGUAGES_MAX_LENGTH = 6
TAG_MIN_LENGTH = 1
TAG_MAX_LENGTH = 24
SEARCH_MIN_LENGTH = 0
SEARCH_MAX_LENGTH = 256
PAGE_MIN_SIZE = 0
PAGE_MAX_SIZE = int(math.pow(2, 31)) - 1  # signed int max (2^31-1)
MACHINE_NAME_MIN_LENGTH = 1
MACHINE_NAME_MAX_LENGTH = 256
HYPERVISOR_MIN_SIZE = 0
HYPERVISOR_MAX_SIZE = 2
MEMORY_MIN_SIZE = 64
DISK_MIN_SIZE = 1
CHECK_DISK_QUOTA = 0.95
DOMAIN_NAME_MIN_LENGTH = 1
DOMAIN_NAME_MAX_LENGTH = 256
NOTE_TITLE_MIN_LENGTH = 0
NOTE_TITLE_MAX_LENGTH = 64
IMAGE_EXT_LIST = ["gif", "png", "jpeg"]
VCPUS_MIN_SIZE = 1
FQDN_MIN_LENGTH = 0
FQDN_MAX_LENGTH = 256
CHAP_USER_MIN_LENGTH = 1
CHAP_USER_MAX_LENGTH = 256
CHAP_PASSWORD_MIN_LENGTH = 1
CHAP_PASSWORD_MAX_LENGTH = 256
STORAGE_VOLUME_SIZE_MIN_LENGTH = 0;
STORAGE_VOLUME_SIZE_MAX_LENGTH = 2147483647;
CONTINUATION_COUNT_MIN = 1;
CONTINUATION_COUNT_MAX = 2147483647;
PROHIBITION_PERIOD_MIN = 1;
PROHIBITION_PERIOD_MAX = 2147483647;
THRESHOLD_VAL_MIN = 0;

DEFAULT_KEYMAP = 'en-us'

# use for storagepool
STORAGE_POOL_TYPE = {"TYPE_DIR":"dir",
                     "TYPE_FS":"fs",
                     "TYPE_NETFS":"netfs",
                     "TYPE_LOGICAL":"logical",
                     "TYPE_DISK":"disk",
                     "TYPE_ISCSI":"iscsi",
                     "TYPE_SCSI":"scsi",
                     }

STORAGE_VOLUME_FORMAT = {"TYPE_RAW":"raw",
                  "TYPE_QCOW2":"qcow2",
                  #"TYPE_QCOW":"qcow",
                  #"TYPE_COW":"cow",
                  #"TYPE_VDI":"vdi",
                  #"TYPE_VMDK":"vmdk",
                  #"TYPE_VPC":"vpc",
                  #"TYPE_CLOOP":"cloop",
                  }

STORAGE_VOLUME_UNIT = {"B":1024**0,
                       "K":1024**1,
                       "M":1024**2,
                       "G":1024**3,
                       "T":1024**4,
                       "P":1024**5,
                       "E":1024**6,
                      }

# Disk format
DISK_QEMU_FORMAT = {"RAW" : "raw",
                    "QCOW2" : "qcow2",
                    #"QCOW" : "qcow",
                    #"COW" : "cow",
                    #"VMDK" : "vmdk",
                    }

DISK_NON_QEMU_FORMAT = {"RAW" : "raw",}

# use for iSCSI
ISCSI_DEVICE_DIR = "/dev/disk/by-path"
ISCSI_DEVICE_NAME_TPL = "ip-%s:%s-iscsi-%s"
ISCSI_DEFAULT_CONFIG_PATH = "/etc/iscsi/iscsid.conf"
ISCSI_DEFAULT_NODE_CONFIG_DIR = "/var/lib/iscsi/nodes"

ISCSI_CONFIG_KEY_AUTH_METHOD = "node.session.auth.authmethod"
ISCSI_CONFIG_KEY_AUTH_USER = "node.session.auth.username"
ISCSI_CONFIG_KEY_AUTH_PASSWORD = "node.session.auth.password"
ISCSI_CONFIG_KEY_SATRTUP = "node.startup"
ISCSI_CONFIG_VALUE_AUTH_METHOD_NONE = "None"
ISCSI_CONFIG_VALUE_AUTH_METHOD_CHAP = "CHAP"
ISCSI_CONFIG_VALUE_SATRTUP_ON = "automatic"
ISCSI_CONFIG_VALUE_SATRTUP_OFF = "manual"
ISCSI_DATA_DIR = VENDOR_DATA_DIR + "/iscsi"

ISCSI_CMD = "/sbin/iscsiadm"
ISCSI_CMD_OPTION_MODE = "--mode"
ISCSI_CMD_OPTION_MODE_NODE = "node"
ISCSI_CMD_OPTION_MODE_SESSION = "session"
ISCSI_CMD_OPTION_MODE_DISCOVERY = "discovery"
ISCSI_CMD_OPTION_TYPE = "--type"
ISCSI_CMD_OPTION_TYPE_SENDTARGETS = "sendtargets"
ISCSI_CMD_OPTION_OPERATOR = "--op"
ISCSI_CMD_OPTION_OPERATOR_DELETE = "delete"
ISCSI_CMD_OPTION_TARGETNAME = "--targetname"
ISCSI_CMD_OPTION_PORTAL = "--portal"
ISCSI_CMD_OPTION_LOGIN = "--login"
ISCSI_CMD_OPTION_LOGOUT = "--logout"
ISCSI_CMD_RES_NO_NODE = "no records found"
ISCSI_CMD_RES_NO_ACTIVE_SESSION = "No active sessions"

DEFAULT_KVM_DISK_FORMAT = "qcow2"
DEFAULT_XEN_DISK_FORMAT = "raw"

# use for log
LOG_EPOCH_REGEX = r"(^[0-9]+\.[0-9]+)"
LOG_SYSLOG_REGEX = r"(^[a-zA-Z]{3} [ 0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})"

# use for collectd
COLLECTD_LOG_DIR  = "/var/log/collectd"
COLLECTD_DATA_DIR = "%s/collectd" % VENDOR_DATA_DIR

COLLECTD_PLUGIN_CPU = "cpu"
COLLECTD_PLUGIN_DF = "df"
COLLECTD_PLUGIN_DISK = "disk"
COLLECTD_PLUGIN_EXEC = "exec"
COLLECTD_PLUGIN_INTERFACE = "interface"
COLLECTD_PLUGIN_IPTABLES = "iptables"
COLLECTD_PLUGIN_LIBVIRT = "libvirt"
COLLECTD_PLUGIN_LOAD = "load"
COLLECTD_PLUGIN_LOGFILE = "logfile"
COLLECTD_PLUGIN_MEMORY = "memory"
COLLECTD_PLUGIN_NETWORK = "network"
COLLECTD_PLUGIN_PYTHON = "python"
COLLECTD_PLUGIN_RRDCACHED = "rrdcached"
COLLECTD_PLUGIN_RRDTOOL = "rrdtool"
COLLECTD_PLUGIN_SENSORS = "sensors"
COLLECTD_PLUGIN_SNMP = "SNMP"
COLLECTD_PLUGIN_SYSLOG = "syslog"
COLLECTD_PLUGIN_TAIL = "tail"
COLLECTD_PLUGIN_UPTIME = "uptime"
COLLECTD_PLUGIN_USERS = "users"

WATCH_PLUGINS = {"cpu"       : COLLECTD_PLUGIN_CPU,
                 "df"        : COLLECTD_PLUGIN_DF,
                 "interface" : COLLECTD_PLUGIN_INTERFACE,
                 "libvirt"   : COLLECTD_PLUGIN_LIBVIRT,
                 "load"      : COLLECTD_PLUGIN_LOAD,
                 "memory"    : COLLECTD_PLUGIN_MEMORY,
                 }

COLLECTD_CPU_TYPE = "cpu"
COLLECTD_CPU_TYPE_INSTANCE = {"IDLE" : "idle",
                              "NICE" : "nice",
                              "USER" : "user",
                              "WAIT" : "wait",
                              "INTERRUPT" : "interrupt",
                              "SOFTIRQ" : "softirq",
                              "STEAL" : "steal",
                              "SYSTEM" : "system",
                              }
COLLECTD_CPU_DS = "value"
COLLECTD_MEMORY_TYPE = "memory"
COLLECTD_MEMORY_TYPE_INSTANCE = {"FREE" : "free",
                                 "CACHED" : "cached",
                                 "BUFFERED" : "buffered",
                                 "USED" : "used",
                                 }
COLLECTD_MEMORY_DS = "value"
COLLECTD_DF_TYPE = "df"
COLLECTD_DF_DS = {"USED" : "used",
                  "FREE" : "free",
                  }
COLLECTD_DISK_TYPE = {"MERGED" : "disk_merged",
                      "OCTETS" : "disk_octets",
                      "OPS" : "disk_ops",
                      "TIME" : "disk_time",
                      }
COLLECTD_DISK_DS = {"READ" : "read",
                    "WRITE" : "write",
                    }
COLLECTD_INTERFACE_TYPE = {"ERRORS" : "if_errors",
                           "PACKETS" : "if_packets",
                           "OCTETS" : "if_octets",
                           }
COLLECTD_INTERFACE_DS = {"RX" : "rx",
                         "TX" : "tx",
                         }
COLLECTD_UPTIME_TYPE ="uptime"
COLLECTD_UPTIME_DS = "value"

COLLECTD_LOAD_TYPE = "load"
COLLECTD_LOAD_DS = {"SHORTTERM": "shortterm",
                    "MIDTERM"  : "midterm",
                    "LONGTERM" : "longterm",
                   }

COLLECTD_USERS_TYPE ="users"
COLLECTD_USERS_DS = "users"

COLLECTD_LIBVIRT_TYPE = {"CPU_TOTAL" : "virt_cpu_total",
                         "VCPU" : "virt_vcpu",
                         "DISK_OPS" : "disk_ops",
                         "DISK_OCTETS" : "disk_octets",
                         "IF_OCTETS" : "if_octets",
                         "IF_PACKETS" : "if_packets",
                         "IF_ERRORS" : "if_errors",
                         "IF_DROPPED" : "if_dropped",
                         }

COLLECTD_DF_RRPORT_BY_DEVICE = True

COUNTUP_DATABASE_PATH = KARESANSUI_DATA_DIR + "/notify_count.db"
VALUE_BOUNDS_UPPER = "1"
VALUE_BOUNDS_LOWER = "0"

HDD_TYPES_REGEX = ('sd[a-z]+[0-9]*',
                   'hd[a-z]+[0-9]*',
                   )

STORAGE_POOL_PWD = {"OWNER":"root",
                    "GROUP":"kss",
                    "MODE":"0770",
                    }

STORAGE_VOLUME_PWD = {"OWNER":"root",
                      "GROUP":"kss",
                      "MODE":"0660",
                      }

DISK_USES = {"IMAGES":"images",
             "DISK":"disk",
             }

# use for mail template
TEMPLATE_DIR = KARESANSUI_SYSCONF_DIR + "/template"
MAIL_TEMPLATE_DIR_JA = TEMPLATE_DIR + "/ja"
MAIL_TEMPLATE_DIR_EN = TEMPLATE_DIR + "/en"
MAIL_TEMPLATE_COLLECTD_WARNING = {COLLECTD_PLUGIN_CPU:"collectd_warning_cpu.eml",
                                  COLLECTD_PLUGIN_DF:"collectd_warning_df.eml",
                                  COLLECTD_PLUGIN_DISK:"collectd_warning_disk.eml",
                                  COLLECTD_PLUGIN_INTERFACE:"collectd_warning_interface.eml",
                                  COLLECTD_PLUGIN_LIBVIRT:"collectd_warning_libvirt.eml",
                                  COLLECTD_PLUGIN_LOAD:"collectd_warning_load.eml",
                                  COLLECTD_PLUGIN_MEMORY:"collectd_warning_memory.eml",
                                  COLLECTD_PLUGIN_UPTIME:"collectd_warning_uptime.eml",
                                  COLLECTD_PLUGIN_USERS:"collectd_warning_users.eml",
                                  }
MAIL_TEMPLATE_COLLECTD_FAILURE = {COLLECTD_PLUGIN_CPU:"collectd_failure_cpu.eml",
                                  COLLECTD_PLUGIN_DF:"collectd_failure_df.eml",
                                  COLLECTD_PLUGIN_DISK:"collectd_failure_disk.eml",
                                  COLLECTD_PLUGIN_INTERFACE:"collectd_failure_interface.eml",
                                  COLLECTD_PLUGIN_LIBVIRT:"collectd_failure_libvirt.eml",
                                  COLLECTD_PLUGIN_LOAD:"collectd_failure_load.eml",
                                  COLLECTD_PLUGIN_MEMORY:"collectd_failure_memory.eml",
                                  COLLECTD_PLUGIN_UPTIME:"collectd_failure_uptime.eml",
                                  COLLECTD_PLUGIN_USERS:"collectd_failure_users.eml",
                                  }
MAIL_TEMPLATE_COLLECTD_OKAY = {COLLECTD_PLUGIN_CPU:"collectd_okay_cpu.eml",
                                  COLLECTD_PLUGIN_DF:"collectd_okay_df.eml",
                                  COLLECTD_PLUGIN_DISK:"collectd_okay_disk.eml",
                                  COLLECTD_PLUGIN_INTERFACE:"collectd_okay_interface.eml",
                                  COLLECTD_PLUGIN_LIBVIRT:"collectd_okay_libvirt.eml",
                                  COLLECTD_PLUGIN_LOAD:"collectd_okay_load.eml",
                                  COLLECTD_PLUGIN_MEMORY:"collectd_okay_memory.eml",
                                  COLLECTD_PLUGIN_UPTIME:"collectd_okay_uptime.eml",
                                  COLLECTD_PLUGIN_USERS:"collectd_okay_users.eml",
                                  }

# use for service
SERVICE_XML_FILE  = KARESANSUI_SYSCONF_DIR + "/service.xml"

# use for Report
GRAPH_COMMON_PARAM = [
    "--imgformat", "PNG",
    "--font", "TITLE:0:IPAexGothic",
    "--font", "LEGEND:0:IPAexGothic",
    "--pango-markup",
    "--width", "550",
    "--height", "350",
    "--full-size-mode",
    "--grid-dash", "1:0",
    "--color", "BACK#FFFFFF",
    "--color", "CANVAS#FFFFFF",
    "--color", "SHADEA#FFFFFF",
    "--color", "SHADEB#FFFFFF",
    "--color", "GRID#DDDDDD",
    "--color", "MGRID#CCCCCC",
    "--color", "FONT#555555",
    "--color", "FRAME#FFFFFF",
    "--color", "ARROW#FFFFFF",
    ]
# use for log viewer
LOG_VIEW_XML_FILE = KARESANSUI_SYSCONF_DIR + "/logview.xml"

GUEST_EXPORT_FILE = 'info.dat'

KVM_BUS_TYPES = ['ide',
                 #'scsi',
                 'virtio',
                 ]
XEN_BUS_TYPES = ['xen']

# use for mount check
MOUNT_CMD = "/bin/mount"
UMOUNT_CMD = "/bin/umount"
FORMAT_CMD = "/sbin/mkfs"
YES_CMD = ("echo", "y")

# interval of monitoring
# !! This interval value is dummy.
# !! Genuine value in collectd config file (/etc/collectd.conf).
WATCH_INTERVAL = 10

# use for network bonding
BONDING_MODE = {"0" : 0,
                "1" : 1,
                "2" : 2,
                "3" : 3,
                "4" : 4,
                "5" : 5,
                "6" : 6,
                }
BONDING_CONFIG_MII_DEFAULT = 100
NETWORK_IFCFG_DIR = "/etc/sysconfig/network-scripts"
NETWORK_COMMAND = "/etc/init.d/network"
SYSTEM_COMMAND_REMOVE_MODULE = "/sbin/rmmod"
NETWORK_IFDOWN_COMMAND = "/sbin/ifdown"
NETWORK_BRCTL_COMMAND = "/usr/sbin/brctl"
NETWORK_IFCONFIG_COMMAND = "/sbin/ifconfig"

DEFAULT_DECIMAL_POINT = 1

DEFAULT_ALERT_TRIGGER_COUNT = 3;
DEFAULT_SLIENT_PERIOD = 300;
