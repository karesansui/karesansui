Karesansuiのインストール
=======================

## このドキュメントについて ##
<a name='about_document'/>

このドキュメントは、インラインHTMLを含むMarkdown形式で記載されています。
最新の情報は、[https://github.com/karesansui/karesansui/blob/master/INSTALL.ja.md][install]から入手することができます。

このドキュメントは、CentOS 6.x (x86_64) にインストールすることを前提に記載していますが、他のLinuxディストリビューションでも同等の作業をすることでインストールが可能です。

  [install]:https://github.com/karesansui/karesansui/blob/master/INSTALL.ja.md


## OSのインストール ##
<a name='installing_operating_system'/>

Karesansuiは、仮想化システムがインストールされた環境でのみ動作します。

KVM (Kernel-based Virtual Machine)を有効にするために、あらかじめ、CentOS 6.x のインストール時の「インストール・ソフトウェアの選択」において「仮想化ホスト(Virtual Host)」を選択し、ソフトウェア選択のカスタマイズで「今すぐカスタマイズ」を選択し、「仮想化」を有効にしてください。

OSインストール後にKVMを有効にする場合は、下記コマンドを実行してください。
以降、ハッシュ(#)プロンプトはrootユーザーによる実行を示し、ドル($)プロンプトは特定の一般ユーザーによる実行を示します。

###`CentOS 6` の場合:

    # yum groupinstall "Virtualization" "Virtualization Client" "Virtualization Platform" "Virtualization Tools"
    # /sbin/modprobe -b kvm-intel (or /sbin/modprobe -b kvm-amd)
    # /sbin/modprobe -b vhost_net

以下のコマンドで、KVM用カーネル・モジュールがロードされているか確認します。

    # /sbin/lsmod | grep kvm
    kvm_intel              50380  0 
    kvm                   305081  1 kvm_intel

 *AMDのCPUでは、"kvm_intel"のかわりに"kvm_amd"がロードされます。*


## ネットワークの設定 ##
<a name='configuring_the_network'/>

Linuxをインストールすると、そのネットワークインターフェースは通常 _eth0_ として認識され、KVMゲストから外向けの通信のみ許可されます。
このインターフェースをゲストと共有して使用できるように、ブリッジモードの仮想インターフェースを作成します。

### ブリッジインターフェースを作成 ###

注意: ローカルのコンソールではなく、SSHやTelnetを通してサーバーにアクセスしている場合、ネットワーク設定変更後のネットワーク再起動時に接続が切れる恐れがあります。ネットワーク設定は、できる限りローカルのコンソールで行ってください。

###`CentOS 6` の場合:

####1. ネットワークインターフェースに紐付けるブリッジを定義するためのネットワークスクリプトを作成します。

スクリプトファイルのパスは、 _/etc/sysconfig/network-scripts/ifcfg-br0_ になります。この _br0_ は、ブリッジ名です。

    # cp /etc/sysconfig/network-scripts/ifcfg-{eth0,br0}

####2. _br0_ のスクリプトファイルを編集します。 (/etc/sysconfig/network-scripts/ifcfg-br0)

ネットワークカードが固定IPアドレスに設定されている場合は、以下のようになっているはずです。

    DEVICE=eth0
    HWADDR=<このデバイスのMACアドレス>
    ONBOOT=yes
    IPADDR=<IPアドレス>
    BOOTPROTO=static
    NETMASK=<ネットマスク>
    TYPE=Ethernet

  スクリプトファイルを以下の例のように編集します。

    DEVICE=br0    # <- 変更
    #HWADDR=<このデバイスのMACアドレス>  # <- コメントまたは削除
    ONBOOT=yes
    IPADDR=<IPアドレス>
    BOOTPROTO=static
    NETMASK=<ネットマスク>
    TYPE=Bridge   # <- 変更

####3. _eth0_ のスクリプトファイルを編集します。 (/etc/sysconfig/network-scripts/ifcfg-eth0)

次に、 _eth0_ のスクリプトファイルを編集し、下記のように _BRIDGE=br0_ を追記します。また、 _IPADDR_ や _NETMASK_ 等の行も削除します。

    DEVICE=eth0
    HWADDR=<このデバイスのMACアドレス>
    ONBOOT=yes
    #IPADDR=<IPアドレス>    # <- コメントまたは削除
    #BOOTPROTO=none         # <- コメントまたは削除
    #NETMASK=<ネットマスク> # <- コメントまたは削除
    TYPE=Ethernet
    BRIDGE=br0              # <- 追加

####4. ネットワークを再起動します。

ネットワークスクリプトの変更を有効にするため、ネットワークを再起動します。

    # /etc/init.d/network restart

####5. ネットワークインターフェースの状態を確認します。

    # /sbin/ifconfig -a

###別の手順:

####1. _eth0_ を プロミスキャスモードにします。

    # /sbin/ifconfig eth0 0.0.0.0 promisc up

####2. ブリッジを作成します。

    # /usr/sbin/brctl addbr br0

####3. _eth0_ を _br0_ ブリッジのポートにします。

    # /usr/sbin/brctl addif br0 eth0

####4. ブリッジを起動します。

    # ifconfig br0 up

####5. ブリッジをネットワークに接続します。

    # ifconfig br0 172.23.233.1 netmask 255.255.255.0
    # route add default gw 172.23.233.254


## 必要なソフトウェアのインストール ##
<a name='installing_dependent_software_libs'/>

Karesansuiをセットアップするには、依存するソフトウェアをインストールしておく必要があります。
各ディストリビューションの提供するアップデートプログラム等を利用し、依存パッケージの大半はインストールできますが、一部のソフトウェアはビルドが必要です。

###`CentOS 6` の場合:

#####CentOSの基本リポジトリからインストール

    # yum install PyXML python-mako python-sqlalchemy python-simplejson rrdtool rrdtool-python

#####[EPEL(Extra Packages for Enterprise Linux)](http://fedoraproject.org/wiki/EPEL)リポジトリからインストール

    # wget ftp://ftp.iij.ad.jp/pub/linux/fedora/epel/6/x86_64/epel-release-6-7.noarch.rpm
    # rpm -Uvh epel-release-6-7.noarch.rpm 
    # yum install python-flup python-sqlite2
    # yum install collectd collectd-ping collectd-rrdtool collectd-virt

#####ディストリビューションやEPEL等のサードパーティで提供していないソフトウェアは自ホストでビルドしインストール

以下の手順で追加パッケージをビルド・作成することができます。

######1. ビルド環境の構築

RPMパッケージを作成する環境を構築します。パッケージ作成ユーザーとしてrpmbuildアカウントを作成します。

    # yum install rpm-build
    # useradd rpmbuild
    # su - rpmbuild
    $ mkdir -p ~/pkgs/{BUILD,RPMS/{i{3,4,5,6}86,x86_64,noarch},SOURCES,SPECS,SRPMS}
    $ echo '%_topdir %(echo $HOME)/pkgs' > ~/.rpmmacros

######2. Karesansuiのソースコードの取得

    # yum install git python-setuptools
    # su - rpmbuild
    $ git clone git://github.com/karesansui/karesansui.git

######3. python-webpyパッケージの作成

    # su - rpmbuild
    $ cd ~/pkgs/SOURCES/
    $ wget http://webpy.org/static/web.py-0.36.tar.gz
    $ rpmbuild -ba ~/karesansui/sample/specs/python-webpy/python-webpy.spec

######4. tightvnc-javaパッケージの作成

    # su - rpmbuild
    $ cd ~/pkgs/SOURCES/
    $ wget http://downloads.sourceforge.net/sourceforge/vnc-tight/tightvnc-1.3.10_javabin.tar.gz
    $ wget http://downloads.sourceforge.net/sourceforge/vnc-tight/tightvnc-1.3.10_javasrc.tar.gz
    $ rpmbuild -ba ~/karesansui/sample/specs/tightvnc-java/tightvnc-java.spec 

######5. IPAexfontパッケージの作成

    # su - rpmbuild
    $ cd ~/pkgs/SOURCES/
    $ wget http://iij.dl.sourceforge.jp/ipafonts/49986/IPAexfont00103.zip
    $ cp ~rpmbuild/karesansui/sample/specs/IPAexfont/09-ipaexfont.conf .
    $ rpmbuild -ba ~/karesansui/sample/specs/IPAexfont/IPAexfont.spec 

######6. ビルドしたパッケージのインストール

    $ cd ~/pkgs/RPMS/noarch
    # rpm -Uvh python-webpy-*.el6.noarch.rpm IPAexfont-*.el6.noarch.rpm tightvnc-java-*.el6.noarch.rpm 


## pysilhouetteのインストール ##
<a name='installing_pysilhouette'/>

### pysilhouette って何？ ###

pysilhouetteは、pythonで記述されたバックグラウンドジョブマネージャーで、Karesansuiの管理画面でのゲスト作成など各タスクを実行するために利用されます。
Karesansuiと同じく、Karesansui Project Teamによって開発されたソフトウェアです。

###`CentOS 6` の場合:

####1. pysilhouetteのソースコードの取得

    # su - rpmbuild
    $ git clone git://github.com/karesansui/pysilhouette.git

####2a. (方法１) RPMパッケージを作成してインストール

    $ cd ~/pysilhouette
    $ python setup.py sdist
    $ rpmbuild -ta dist/pysilhouette-*.tar.gz
    # rpm -Uvh ~rpmbuild/pkgs/RPMS/noarch/pysilhouette-*.noarch.rpm

####2b. (方法２) Pythonのdistutilsを使ってインストール

    $ cd ~/pysilhouette
    $ python setup.py build
    # python setup.py install --root=/ --record=INSTALLED_FILES

    #### Create pysilhouette account ####
    # /usr/sbin/useradd -c "Pysilhouette" -s /bin/false -r pysilhouette

    #### Create the application's system directories ####
    # mkdir /etc/pysilhouette
    # mkdir /var/log/pysilhouette
    # mkdir /var/lib/pysilhouette

    #### Copy several programs, configuration files and SysV init script ####
    # cp -f ~rpmbuild/pysilhouette/sample/rc.d/init.d/* /etc/rc.d/init.d/
    # cp -f ~rpmbuild/pysilhouette/sample/sysconfig/silhouetted /etc/sysconfig/silhouetted
    # cp -f ~rpmbuild/pysilhouette/sample/log.conf.example /etc/pysilhouette/log.conf
    # cp -f ~rpmbuild/pysilhouette/sample/silhouette.conf.example /etc/pysilhouette/silhouette.conf
    # cp -f ~rpmbuild/pysilhouette/sample/whitelist.conf.example /etc/pysilhouette/whitelist.conf
    # ln -s `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`/pysilhouette/silhouette.py /usr/bin
    # cp -f ~rpmbuild/pysilhouette/tools/psil-cleandb /usr/sbin
    # cp -f ~rpmbuild/pysilhouette/tools/psil-set /usr/sbin
    # chmod 0744 /usr/sbin/psil-*


## karesansuiのインストール ##
<a name='installing_karesansui'/>

###`CentOS 6` の場合:

####1. karesansuiのソースコードの取得

    # su - rpmbuild
    $ git clone git://github.com/karesansui/karesansui.git # 既にダウンロード済みの場合は、必要ありません。

####2a. (方法１) RPMパッケージを作成してインストール

    $ cd ~/karesansui
    $ python setup.py sdist
    $ rpmbuild -ta dist/karesansui-*.tar.gz
    # rpm -Uvh ~rpmbuild/pkgs/RPMS/noarch/karesansui-{,{bin,data,gadget,lib,plus}-}3.*.noarch.rpm

####2b. (方法２) Pythonのdistutilsを使ってインストール

    $ cd ~/karesansui
    $ python setup.py build
    # python setup.py install --record=INSTALLED_FILES --install-scripts=/usr/share/karesansui/bin

    #### Create kss account ####
    # /usr/sbin/useradd -c "Karesansui Project" -s /bin/false -r -m -d /var/lib/karesansui kss
    # gpasswd -a qemu kss

    #### Create the application's system directories ####
    # mkdir /etc/karesansui/virt
    # mkdir /var/log/karesansui
    # mkdir -p /var/lib/karesansui/{tmp,cache}

    #### Change attributes of the application's directories/files ####
    # chgrp -R kss   /etc/karesansui
    # chmod g+rwx    /etc/karesansui/virt
    # chmod o-rwx    /etc/karesansui/virt
    # chmod -R g+rw  /etc/karesansui
    # chmod -R o-rwx /etc/karesansui
    # chgrp -R kss   /var/log/karesansui
    # chmod -R 0700  /var/log/karesansui
    # chgrp -R kss   /var/lib/karesansui
    # chmod -R 0770  /var/lib/karesansui
    # chgrp -R kss `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`/karesansui
    # find `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`/karesansui -type d -exec chmod g+rwx \{\} \;
    # find /usr/share/karesansui/ -type d -exec chgrp -R kss \{\} \;
    # find /usr/share/karesansui/ -type d -exec chmod g+rwx \{\} \;

    #### Copy several programs, configuration files and SysV init script ####
    # cp -f  ~rpmbuild/karesansui/sample/application.conf.example /etc/karesansui/application.conf
    # cp -f  ~rpmbuild/karesansui/sample/log.conf.example /etc/karesansui/log.conf
    # cp -f  ~rpmbuild/karesansui/sample/service.xml.example /etc/karesansui/service.xml
    # cp -f  ~rpmbuild/karesansui/sample/logview.xml.example /etc/karesansui/logview.xml
    # cp -f  ~rpmbuild/karesansui/sample/cron_cleantmp.example /etc/cron.d/karesansui_cleantmp
    # cp -f  ~rpmbuild/karesansui/sample/whitelist.conf.example /etc/pysilhouette/whitelist.conf


## pysilhouetteの設定 ##
<a name='configuring_pysilhouette'/>

必要に応じて下記ファイルの内容を変更してください。

<table style='border: solid 1px #000000; border-collapse: collapse;'>
 <tr><th>ファイル</th><th>説明</th></tr>
 <tr>
  <td nowrap>/etc/pysilhouette/silhouette.conf</td>
  <td>pysilhouetteの基本動作に関する設定ファイル</td>
 </tr>
 <tr>
  <td nowrap>/etc/pysilhouette/log.conf</td>
  <td>pysilhouetteのログ出力に関する設定ファイル</td>
 </tr>
 <tr>
  <td nowrap>/etc/pysilhouette/whitelist.conf</td>
  <td>pysilhouetteで実行可能なコマンドのホワイトリスト</td>
 </tr>
 <tr>
  <td nowrap>/etc/sysconfig/silhouetted</td>
  <td>pysilhouetteサービスの起動オプション</td>
 </tr>
</table>

マシン起動時にpysilhouetteサービスが有効になるように設定します。

    # /sbin/chkconfig --add silhouetted
    # /sbin/chkconfig silhouetted on


## karesansuiの設定 ##
<a name='configuring_karesansui'/>

必要に応じて下記ファイルの内容を変更してください。

<table style='border: solid 1px #000000; border-collapse: collapse;'>
 <tr><th>ファイル</th><th>説明</th></tr>
 <tr>
  <td nowrap>/etc/karesansui/application.conf</td>
  <td>karesansuiの基本動作に関する設定ファイル(<b>*application.uniqkeyの設定が必要。設定値は uuidgen コマンドで生成できます。</b>)</td>
 </tr>
 <tr>
  <td nowrap>/etc/karesansui/log.conf</td>
  <td>karesansuiのログ出力に関する設定ファイル</td>
 </tr>
 <tr>
  <td nowrap>/etc/karesansui/service.xml</td>
  <td>karesansuiに関連するサービスの定義</td>
 </tr>
 <tr>
  <td nowrap>/etc/karesansui/service.xml</td>
  <td>karesansuiに関連するログファイルの定義</td>
 </tr>
 <tr>
  <td nowrap>/etc/cron.d/karesansui_cleantmp</td>
  <td>cronによる定期実行の設定</td>
 </tr>
</table>


## karesansui用データベースの作成 ##
<a name='creating_database_for_karesansui'/>

karesansuiのソースコードに付属するスクリプトを利用してデータベース作成とKaresansuiの管理者情報のデータベースへの挿入を行います。

    # python ~rpmbuild/karesansui/tools/initialize_database.py -m <管理者メールアドレス> -p <管理者パスワード> -l ja_JP

データベースにSQLiteを利用している場合は、以下のコマンドでデータベースファイルの属性変更を行ってください。

    # chgrp -R kss /var/lib/karesansui/karesansui.db
    # chmod -R g+w /var/lib/karesansui/karesansui.db
    # chmod -R o-rwx /var/lib/karesansui/karesansui.db


## pysilhouette用データベースの作成 ##
<a name='creating_database_for_pysilhouette'/>

以下のコマンドを実行してデータベースを作成します。

    # python -c "import karesansui; from pysilhouette.prep import readconf; karesansui.sheconf = readconf('/etc/pysilhouette/silhouette.conf'); import karesansui.db._2pysilhouette; karesansui.db._2pysilhouette.get_metadata().create_all()"

データベースにSQLiteを利用している場合は、以下のコマンドでデータベースファイルの属性変更を行ってください。

    # chgrp -R kss /var/lib/pysilhouette/
    # chmod -R g+rw /var/lib/pysilhouette/
    # chmod -R o-rwx /var/lib/pysilhouette/


## pysilhouette サービスの起動 ##
<a name='starting_pysilhouette_service'/>

    # /etc/init.d/silhouetted start


## libvirtの設定 ##
<a name='configuring_libvirt'/>

####1. libvirtd 設定ファイルの編集

以下の設定ファイルを編集します。

__/etc/libvirt/libvirtd.conf__

 * listen_tcp = 1
 * tcp_port = "16509"
 * unix_sock_group = "kss"
 * auth_tcp = "none"

__/etc/sysconfig/libvirtd__

 * LIBVIRTD_ARGS="--listen"

####2. libvirtが使用するディレクトリの作成

    # mkdir -p /var/lib/libvirt/{disk,domains,snapshot}
    # chgrp -R kss  /var/lib/libvirt
    # chmod -R 0770 /var/lib/libvirt

    # chgrp -R kss /etc/libvirt
    # find /etc/libvirt -type d -exec chmod g+rwx \{\} \;

####3. TLS証明書の作成

まず、自己認証局(CA)を作成します。

    $ certtool --generate-privkey > cakey.pem
    $ vi ca.info
    cn = Name of your organization
    ca
    cert_signing_key
    $ certtool --generate-self-signed --load-privkey cakey.pem --template ca.info --outfile cacert.pem

サーバー証明書を発行します。

    $ certtool --generate-privkey > serverkey.pem
    $ vi server.info
    organization = Name of your organization
    cn = Your FQDN
    tls_www_server
    encryption_key
    signing_key
    $ certtool --generate-certificate --load-privkey serverkey.pem   --load-ca-certificate cacert.pem --load-ca-privkey cakey.pem   --template server.info --outfile servercert.pem

証明書および鍵をインストールします。

    # mkdir -p /etc/pki/libvirt/private/
    # cp -i cacert.pem /etc/pki/CA/
    # cp -i servercert.pem /etc/pki/libvirt/
    # cp -i serverkey.pem /etc/pki/libvirt/private/

####4. libvirtサービスの有効化

サービスを再起動し、マシン起動時に自動で有効になるように設定します。

    # /sbin/chkconfig libvirtd on
    # /etc/init.d/libvirtd restart

####5. libvirtサービスとの接続チェック

libvirtのqemuモニターと接続が可能かどうか確認してください。

    # virsh -c qemu+tcp://localhost:16509/system list

接続が成功した場合は、以下のように出力されます。

    Id 名前               状態
    ----------------------------------

####6. libvirtストレージプールの作成

    # KARESANSUI_CONF=/etc/karesansui/application.conf python -c "from karesansui.prep import built_in; built_in()"
    # /usr/share/karesansui/bin/create_storage_pool.py --name=default --target_path=/var/lib/libvirt/domains --mode=0770 --owner=0 --group=`id -g kss` --type=dir
    # virsh pool-refresh default
    # rm -fr /usr/share/karesansui/bin/__cmd__.py /var/log/karesansui/*


## Karesansuiの管理コンソールへの接続確認
<a name='checking_for_connectivity_to_karesansui_management_console'/>

以上で、Karesansui自身の構築は完了です。

python-webpyの内蔵Webサーバーを利用して、WebブラウザからKaresansuiにアクセスできるかどうかを確認します。

まず、Karesansuiをwebpyの内蔵サーバーで立ち上げます。

    # su -s /bin/bash kss -c "KARESANSUI_CONF=/etc/karesansui/application.conf SEARCH_PATH= /usr/share/karesansui/bin/karesansui.fcgi"

構築が正しく行われている場合は、以下のように出力されます。

<pre>
http://0.0.0.0:8080/
</pre>

正常に起動しましたら、Webブラウザから下記のURLにアクセスしてください。ベーシック認証のユーザー名とパスワードは、「karesansui用データベースの作成」で指定した値になります。

<pre>
http://[インストールしたサーバー]:8080/karesansui/v3/
</pre>

管理画面が正常に表示されれば、Karesansuiのインストールは成功です。


他のHTTPサーバーを利用する
========================

## Lighttpdとの連携 ##
<a name='with_lighttpd'/>

###`CentOS 6` の場合:

####1. パッケージのインストール

[EPEL(Extra Packages for Enterprise Linux)](http://fedoraproject.org/wiki/EPEL)リポジトリから _lighttpd_ パッケージをインストールします。

    # wget ftp://ftp.iij.ad.jp/pub/linux/fedora/epel/6/x86_64/epel-release-6-7.noarch.rpm
    # rpm -Uvh epel-release-6-7.noarch.rpm 
    # yum install lighttpd lighttpd-fastcgi spawn-fcgi

####2. グループメンバーの調整

_lighttpd_ ユーザーを _kss_ グループに、 _kss_ ユーザーを _lighttpd_ グループに追加します。

    # gpasswd -a lighttpd kss
    # gpasswd -a kss lighttpd

####3. 設定ファイルの作成と編集

_/etc/lighttpd/lighttpd.conf_ に以下の行を追記します。

    include "conf.d/karesansui.conf"

_/etc/lighttpd/modules.conf_ で以下のモジュールを有効にします。

    mod_alias
    mod_rewrite
    mod_fastcgi

ソースコードに付属する設定ファイルのサンプルをコピーし、必要であれば設定内容を変更します。

    # cp ~rpmbuild/karesansui/sample/lighttpd/karesansui.conf /etc/lighttpd/conf.d/


####4. lighttpdのSSLの設定

    # mkdir -p /etc/lighttpd/ssl
    # openssl req -new -x509 -keyout /etc/lighttpd/ssl/server.pem -out /etc/lighttpd/ssl/server.pem -days 3650 -nodes
    # chmod 400 /etc/lighttpd/ssl/server.pem


####5. Webサーバーの起動

既に他のWebサーバーでKaresansuiを試している場合は、下記コマンドで既存ファイルのいくつかを削除する必要があります。

    # rm -fr /usr/share/karesansui/bin/__cmd__.py /var/log/karesansui/*log

サービスを再起動し、マシン起動時に自動で有効になるように設定します。

    # /sbin/chkconfig lighttpd on
    # /etc/init.d/lighttpd restart

SELinuxが有効な状態ですと、lighttpdが正常に起動しない場合があります。無効にしてから再度サービスを起動してみてください。

    # /usr/sbin/setenforce 0
    # /etc/init.d/lighttpd restart

次回マシン起動時にSELinuxをPermissiveモードにする必要があるなら、/etc/selinux/configに以下のように設定してくだい。

    SELINUX=permissive

####6. Karesansuiの管理コンソールへの接続確認

Webブラウザから下記のURLにアクセスしてください。ベーシック認証のユーザー名とパスワードは、「karesansui用データベースの作成」で指定した値になります。

<pre>
https://[インストールしたサーバー]/karesansui/v3/
</pre>


## Apacheとの連携 ##
<a name='with_apache'/>

###`CentOS 6` の場合:

####1. パッケージのインストール

[RepoForge](http://repoforge.org/)リポジトリから _mod_fastcgi_ パッケージをインストールします。

    # wget http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.2-2.el6.rf.x86_64.rpm
    # rpm -Uvh rpmforge-release-0.5.2-2.el6.rf.x86_64.rpm 
    # yum install httpd mod_fastcgi

####2. グループメンバーの調整

_apache_ ユーザーを _kss_ グループに、 _kss_ ユーザーを _apache_ グループに追加します。

    # gpasswd -a apache kss
    # gpasswd -a kss apache

####3. 設定ファイルの作成と編集

ソースコードに付属する設定ファイルのサンプルをコピーし、必要であれば設定内容を変更します。

    # cp ~rpmbuild/karesansui/sample/apache/fastcgi.conf /etc/httpd/conf.d/

####4. Webサーバーの起動

既に他のWebサーバーでKaresansuiを試している場合は、下記コマンドで既存ファイルのいくつかを削除する必要があります。

    # rm -fr /usr/share/karesansui/bin/__cmd__.py /var/log/karesansui/*log

サービスを再起動し、マシン起動時に自動で有効になるように設定します。

    # /sbin/chkconfig httpd on
    # /etc/init.d/httpd restart

    # chmod 777 /tmp/dynamic
    # chown apache:apache /tmp/dynamic
    # /etc/init.d/httpd restart

SELinuxが有効な状態ですと、apacheが正常に起動しない場合があります。無効にしてから再度サービスを起動してみてください。

    # /usr/sbin/setenforce 0
    # /etc/init.d/httpd restart

次回マシン起動時にSELinuxをPermissiveモードにする必要があるなら、/etc/selinux/configに以下のように設定してくだい。

    SELINUX=permissive

####6. Karesansuiの管理コンソールへの接続確認

Webブラウザから下記のURLにアクセスしてください。ベーシック認証のユーザー名とパスワードは、「karesansui用データベースの作成」で指定した値になります。

<pre>
https://[インストールしたサーバー]/karesansui/v3/
</pre>


## Nginxとの連携 ##
<a name='with_nginx'/>

###`CentOS 6` の場合:

####1. パッケージのインストール

[EPEL(Extra Packages for Enterprise Linux)](http://fedoraproject.org/wiki/EPEL)リポジトリから _nginx_ パッケージをインストールします。

    # wget ftp://ftp.iij.ad.jp/pub/linux/fedora/epel/6/x86_64/epel-release-6-7.noarch.rpm
    # rpm -Uvh epel-release-6-7.noarch.rpm 
    # yum install nginx spawn-fcgi

####2. グループメンバーの調整

_nginx_ ユーザーを _kss_ グループに、 _kss_ ユーザーを _nginx_ グループに追加します。

    # gpasswd -a nginx kss
    # gpasswd -a kss nginx

####3. 設定ファイルの作成と編集

ソースコードに付属する設定ファイルのサンプルをコピーし、必要であれば設定内容を変更します。

    # cp ~rpmbuild/karesansui/sample/nginx/karesansui.conf /etc/nginx/conf.d/

####4. Webサーバーの起動

既に他のWebサーバーでKaresansuiを試している場合は、下記コマンドで既存ファイルのいくつかを削除する必要があります。

    # rm -fr /usr/share/karesansui/bin/__cmd__.py /var/log/karesansui/*log

Karesansuiをwebpyの内蔵サーバーで立ち上げます。

    # su -s /bin/bash kss -c "KARESANSUI_CONF=/etc/karesansui/application.conf SEARCH_PATH= /usr/share/karesansui/bin/karesansui.fcgi 127.0.0.1:8080"

サービスを再起動し、マシン起動時に自動で有効になるように設定します。

    # /sbin/chkconfig nginx on
    # /etc/init.d/nginx restart

####6. Karesansuiの管理コンソールへの接続確認

Webブラウザから下記のURLにアクセスしてください。ベーシック認証のユーザー名とパスワードは、「karesansui用データベースの作成」で指定した値になります。

<pre>
http://[インストールしたサーバー]/karesansui/v3/
</pre>


その他の設定
============

## collectdの設定 ##
<a name='configuring_collectd'/>

### collectd って何？ ###

[collectd](http://collectd.org/) は、システムの各種情報を定期的に収集し、それらのデータを蓄積する手段を提供するデーモンプログラムです。
Karesansuiでは、統計グラフを表示するためにcollectdを利用しています。

###`CentOS 6` の場合:

まず、collectdの各種プラグインの設定を変更する必要があります。
下記に示す手順に従ってください。

####1. collectdの設定ファイルを編集します。 (/etc/collectd.conf)

__Global settings__

    Hostname    your.host.name
    FQDNLookup   true
    BaseDir     "/var/lib/collectd"
    PIDFile     "/var/run/collectd.pid"
    PluginDir   "/usr/lib64/collectd/"
    TypesDB     "/usr/share/collectd/types.db"
    Interval     10
    Timeout      2
    ReadThreads  5

__LoadPlugin section__

    LoadPlugin cpu
    LoadPlugin df
    LoadPlugin disk
    LoadPlugin interface
    LoadPlugin libvirt
    LoadPlugin load
    LoadPlugin memory
    LoadPlugin network
    LoadPlugin rrdtool
    LoadPlugin uptime
    LoadPlugin users

__Plugin configuration__

    <Plugin df>
        ReportReserved     false
        ReportByDevice     true
        ReportInodes       false
        IgnoreSelected     false
    </Plugin>

    <Plugin disk>
        Disk "/^[hs]d[a-f][0-9]?$/"
        IgnoreSelected false
    </Plugin>

    <Plugin interface>
       IgnoreSelected false
    </Plugin>

    <Plugin libvirt>
        HostnameFormat     name
        Connection         "qemu+tcp://127.0.0.1:16509/system?no_verify=1"
        IgnoreSelected     false
        RefreshInterval    60
    </Plugin>

    <Plugin rrdtool>
        DataDir "/var/lib/collectd"
        CacheTimeout 120
        CacheFlush   900
    </Plugin>

####2. collectdサービスを再起動します。

全ての変更を有効にするため、collectdを再起動します。

    # /sbin/chkconfig collectd on
    # /etc/init.d/collectd restart


フィードバック
==============
このドキュメントに誤りや不明瞭な点、情報が古いなどありましたら、改善いたしますので連絡願います。ご協力に感謝いたします。

