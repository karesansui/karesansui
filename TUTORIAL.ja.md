# チュートリアル

このドキュメントは下記のユーザー向けに記述されています。

* ゲストOSを作成したいユーザー
* 基本的な操作を知りたいユーザー

## ゲストOSのインストール

#### インストール準備

ここでは、ゲストにCentOS 6(x86_64)をインストールする場合を例に、３通りのインストール方法を説明します。

######ケース1: 既にインターネットに接続できる環境の場合 (ネットワークインストール)

ホストOSが既にインターネットに繋がっている場合は、外部サーバーにあるカーネルイメージとOSイメージを使用してゲストOSをインストールすることができます。
プロキシサーバー経由でのインストールはできませんので、その場合はFTPサーバーを利用してください。
ホストOSから CentOS 6 のOSイメージのURLに接続できるか確認してください。

URLの例

* http://[Web-site-name]/centos/6/os/x86_64/
* ftp://[FTP-site-name]/Linux/centos/6/os/x86_64/


######ケース2: インターネットに接続できない環境の場合 (ローカルインストール - ISOイメージ)

KVMハイパーバイザーなど完全仮想化環境では、ISO-9660 CD-ROM イメージファイルを使ってインストールすることができます。
イメージファイルがなくDVD-ROMのみお持ちの場合は、 _dd_ コマンドを使ってイメージファイルを生成できます。

    # dd if=/dev/cdrom of=/iso/centos6-x86_64.iso
    dd: reading `/dev/cdrom': Input/output error
    269860+0 records in
    269860+0 records out

######ケース3: インターネットに接続できない環境の場合 (ローカルインストール - DVD-ROM)

CentOS 6(x86_64)のDVDを利用してインストールすることができます。
この場合、一時的にホストOS上にFTPサーバーを稼働させる必要がありますので、vsftpd等のFTPサーバーソフトウェアをあらかじめインストールしておきます。
CentOS 6(x86_64)のDVDをドライブに挿入し、下記の方法でOSイメージをホストOSのAnonymousFTPの領域へマウントします。

    # rpm -q vsftpd 2>/dev/null || yum -y install vsftpd
    # /etc/init.d/vsftpd restart
    # mount /dev/cdrom /var/ftp/pub

localhostにAnonymousFTPでログインが可能か確認します。

    # ftp localhost
    Connected to localhost (127.0.0.1).
    220 (vsFTPd 2.2.2)
    Name (localhost:root): ftp
    331 Please specify the password.
    Password:
    230 Login successful.
    Remote system type is UNIX.
    Using binary mode to transfer files.
    ftp> quit

ログインができない場合は、SELinuxが有効になっている可能性がありますので、下記の方法で一時的に無効にしてください。

    # /usr/sbin/setenforce 0


#### ゲストOSのインストール

まず、Karesansuiのトップ画面のホストアイコンをクリックします。
その後、表示される「ゲスト一覧」タブ内の「作成」ボタンをクリックすると「ゲスト作成」画面が表示されます。

入力方法を、前述のインストールのケースごとに示します。

######ケース1: 既にインターネットに接続できる環境の場合 (ネットワークインストール)

下記に示した項目を入力します。
 
<table class='item_table'>
 <tr>
  <th>項目名</th>
  <th>説明</th>
  <th>例</th>
 </tr>
 <tr>
  <td nowrap>カーネルイメージ</td>
  <td nowrap>カーネルイメージのURL</td>
  <td nowrap>ftp://ftp.iij.ad.jp/pub/linux/centos/6/os/x86_64/isolinux/vmlinuz</td>
 </tr>
 <tr>
  <td nowrap>Initrdイメージ</td>
  <td nowrap>InitrdイメージのURL</td>
  <td nowrap>ftp://ftp.iij.ad.jp/pub/linux/centos/6/os/x86_64/isolinux/initrd.img</td>
 </tr>
</table>

その他、各項目の入力方法に関しては、項目名の右に表示される「？」をクリックして確認してください。

######ケース2: インターネットに接続できない環境の場合 (ローカルインストール - ISOイメージ)

下記に示した項目を入力します。

<table class='item_table'>
 <tr>
  <th>項目名</th>
  <th>説明</th>
  <th>例</th>
 </tr>
 <tr>
  <td nowrap>ISOイメージ</td>
  <td nowrap>ISOイメージの絶対パス</td>
  <td nowrap>/iso/centos6-x86_64.img</td>
 </tr>
</table>

その他、各項目の入力方法に関しては、項目名の右に表示される「？」をクリックして確認してください。

######ケース3: インターネットに接続できない環境の場合 (ローカルインストール - DVD-ROM)

下記に示した項目を入力します。

<table class='item_table'>
 <tr>
  <th>項目名</th>
  <th>説明</th>
  <th>例</th>
 </tr>
 <tr>
  <td nowrap>カーネルイメージ</td>
  <td nowrap>カーネルイメージの絶対パス</td>
  <td nowrap>/var/ftp/pub/isolinux/vmlinuz</td>
 </tr>
 <tr>
  <td nowrap>Initrdイメージ</td>
  <td nowrap>Initrdイメージの絶対パス</td>
  <td nowrap>/var/ftp/pub/isolinux/initrd.img</td>
 </tr>
</table>

その他、各項目の入力方法に関しては、項目名の右に表示される「？」をクリックして確認してください。

-----

全ての入力が完了したら、「ゲスト作成」画面の最下部にある「作成」ボタンをクリックしてください。
クリック後、ゲスト作成のジョブを受理した旨のメッセージが表示されますので、「閉じる」ボタンで「ゲスト作成」画面を閉じます。

その後表示されるゲスト一覧画面に、今作成したゲストのアイコンが追加されます。

作成されたゲストのアイコンをクリックし、その後表示されるゲスト画面の「コンソール」タブをクリックします。
ゲストのコンソール画面が表示され、コンソール画面において通常の CentOS 6 のOSインストールと同じようにゲスト上にOSをインストールすることができます。

######ケース1: 既にインターネットに接続できる環境の場合 (ネットワークインストール)

ゲストOS(CentOS 6)のインストールにおいて

######1. 「Installation Method」の選択

前述のカーネルイメージで指定したプロトコル（「HTTP」または「FTP」）を選択し、「HTTP」の場合は「HTTP Setup」、「FTP」の場合は「FTP Setup」で接続先を設定してください。

######2 - 1. HTTP経由でのインストール

下記に示した項目を入力します。

<table class='item_table'>
 <tr>
  <th>項目名</th>
  <th>説明</th>
  <th>例</th>
 </tr>
 <tr>
  <td nowrap>Web site name</td>
  <td nowrap>OSイメージを提供するWebサイトのFQDN</td>
  <td nowrap>mirror.centos.org</td>
 </tr>
 <tr>
  <td nowrap>CentOS directory</td>
  <td nowrap>Webサイト上の各CentOSディレクトリ</td>
  <td nowrap>/centos/6/os/x86_64/</td>
 </tr>
</table>

######2 - 2. FTP経由でのインストール

下記に示した項目を入力します。

<table class='item_table'>
 <tr>
  <th>項目名</th>
  <th>説明</th>
  <th>例</th>
 </tr>
 <tr>
  <td nowrap>FTP site name</td>
  <td nowrap>OSイメージを提供するFTPサイトのFQDN</td>
  <td nowrap>ftp.iij.ad.jp</td>
 </tr>
 <tr>
  <td nowrap>CentOS directory</td>
  <td nowrap>FTPサイト上の各CentOSディレクトリ</td>
  <td nowrap>/pub/linux/centos/6/os/x86_64/</td>
 </tr>
</table>

######ケース2: インターネットに接続できない環境の場合 (ローカルインストール - ISOイメージ)

通常のインストールディスクからのインストールと同様にインストールできます。

######ケース3: インターネットに接続できない環境の場合 (ローカルインストール - DVD-ROM)

ゲストOS(CentOS 6)のインストールにおいて

######1. 「Installation Method」の選択

OSインストール時の「Installation Method」の選択では「FTP」を選択します。

######2. FTP経由でのインストール

「FTP Setup」で下記に示した項目を入力します。

<table class='item_table'>
 <tr>
  <th>項目名</th>
  <th>説明</th>
  <th>例</th>
 </tr>
 <tr>
  <td nowrap>FTP site name</td>
  <td nowrap>OSイメージを提供するFTPサイトのFQDN</td>
  <td nowrap>ホスト自身のIPアドレス(ループバックアドレスはだめ)</td>
 </tr>
 <tr>
  <td nowrap>CentOS directory</td>
  <td nowrap>FTPサイト上の各CentOSディレクトリ</td>
  <td nowrap>/pub/</td>
 </tr>
</table>


## 最後に

以上で、チュートリアルは終了です。これで仮想化の基本操作はできるようになるでしょう。

## ヒント

Karesansuiからゲストのシャットダウンを行う場合、あらかじめゲストのOSにおいて電源管理サービス（ACPI イベントデーモン）を有効にしておく必要があります。
CentOS や Red Hat Enterprise Linux の場合は、_acpid_ パッケージをインストールし、ゲスト起動時に _acpid_ が自動起動されるように設定してください。

    # rpm -q acpid 2>/dev/null || yum -y install acpid
    # /sbin/service haldaemon stop
    # /sbin/service acpid restart
    # /sbin/chkconfig acpid on
    # /sbin/service haldaemon start


