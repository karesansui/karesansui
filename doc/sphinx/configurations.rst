==============
Configurations
==============

Overview
========

ここでは各種設定ファイルに関して説明します。

Karesansuiの設定(application.conf)の説明
========================================

application.search.path

    Pythonの追加サーチパスを設定します。
    ※複数指定する場合はカンマ(,)で区切ります

例) application.search.path=/usr/lib/python,/usr/lib/python2.6,/usr/lib/python2.6/site-packages


application.log.config

    ログ出力設定ファイルパスを設定します。
    ログ出力設定ファイルついてはこちらを参照してください。

例) application.log.config=/etc/karesansui/log.conf

application.url.prefix

    URIのプレフィックスを設定します。
    以下の{}内を設定します。
    http://example.com{/karesansui/v3}/
    ※v1はKaresansuiのメジャーバージョンを指定しておくことを推奨します。
    ※Karesansui 2.0.0で"karesansui/v3/"に変更になりました。(Since 3.0.0)

例) application.url.prefix=/karesansui/v3

application.default.locale

    Karesansuiが使用するデフォルトのロケールを設定します。
    ※現在、ja_JPとen_USに対応しています。
    ※ログインしている場合は、ログインユーザのロケールが優先されます。

例) application.default.locale=ja_JP

application.template.theme

    Karesansuiのテーマを設定します。
    ※初期インストール時はdefaultに設定されています。

例) application.template.theme=default

application.tmp.dir

    Karesansuiが一時的に作成するファイル等々をおくディレクトリパスを設定します。

例) application.tmp.dir=/tmp

application.bin.dir

    Karesansuiが使用するジョブコマンドのディレクトリパスを設定します。
    ※Karesansuiの実行ユーザ権限で書き込みができる必要があります。

例) application.bin.dir=/usr/share/karesansui/bin

application.generate.dir

    各種設定ファイルのテンプレートディレクトリを設定します。

例) application.generate.dir=/usr/lib/python2.6/site-packages/karesansui/templates/default/_generate

application.mail.email

    Karesansuiで利用するメールアドレスを設定します。

例) application.mail.email=karesansui@example.com

application.mail.port

    Karesansuiで利用するメールサーバのポート番号を設定します。

例) application.mail.port=25

application.mail.server

    Karesansuiで利用するメールサーバ名を設定します。

例) application.mail.server=localhost

application.proxy.status

    Karesansuiでプロキシサーバを利用するかを設定します。
    1=有効
    0=無効

例)application.proxy.status=0

application.proxy.server

    Karesansuiで利用するプロキシサーバ名を設定します。

例) application.proxy.server=localhost

application.proxy.port

    Karesansuiで利用するプロキシサーバのポート番号を設定します。

例) application.proxy.port=9080

application.proxy.user

    Karesansuiで利用するプロキシサーバにログインするユーザ名を設定します。

例) application.proxy.user=bar

application.proxy.password

    Karesansuiで利用するプロキシサーバにログインするパスワードを設定します。

例)application.proxy.password=foo

database.bind

    Karesansuiで利用するデータベースのバインドを設定します。
    RFC-1738で定義されているスタイルで設定してください。
    さらに詳しい設定についてはSQLAlchemyのサポートデータベース を参照してください。

MySQL
mysql://localhost/<データベース名>
mysql://<ユーザ名>:<パスワード>@<ホスト名>/<データベース名>
mysql://<ユーザ名>:<パスワード>@<ホスト名>:<ポート番号>/<データベース名>
PostgreSQL
postgres://<ユーザ名>:<パスワード>@<ホスト名>:<ポート番号>/<データベース名>
SQLite※Karesansuiの実行権限で読み取り・書き込み可能である必要があります。
sqlite:////<絶対パス>/<ファイル名>-絶対パスで定義
sqlite:///<相対パス>/<ファイル名>-相対パスで定義
例) database.bind=sqlite:////var/opt/karesansui/karesansui.db

database.pool.status

    コネクションプールの利用可否を設定します。
    0=利用しない
    1=利用する

例)database.pool.status=0

database.pool.size

    通常時のコネクションプール数を設定します。
    ※SQLiteでは利用できません。設定は無視されます。

例)database.pool.size=1

database.pool.max.overflow

    コネクションプールの最大数を設定します。

例)database.pool.max.overflow=10

pysilhouette.conf.path

    Karesansuiで使用するPysilhouetteソフトウェアの設定ファイルパスを設定します。
    ※Karesansuiの実行ユーザ権限で読み取り可能である必要があります。(書き込み・実行権限は必要ありません。)

例)pysilhouette.conf.path=/etc/pysilhouette/silhouette.conf

Configurations allow you to create multiple variations of a part or assembly model within a single document.
