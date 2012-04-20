Karesansui
==========

Karesansuiは、日本発のオープンソースの仮想化管理アプリケーションです。

 * 複雑な部分を抽象化した、シンプルで直観的なWebインターフェース。
 * MITライセンスで提供されるフリーソフトウェアであり、個人ユース、商用を問わず無料で利用することができます。
 * Kernel-based Virtual Machine(KVM)に対応しています。今後、他の仮想化技術／ハイパーバイザーにも対応する予定です。
 * 多言語対応しています。現在は日本語と英語をサポートしています。

必要なもの
----------

Karesansuiは、他のソフトウェアを必要とします。

インストールするために以下が必要です。

* [Python](http://www.python.org/) 2.6 (2.4 might work?)
* [RRDtool](http://oss.oetiker.ch/rrdtool/) 1.3 (or better)
* [Mako](http://www.makotemplates.org/) 0.3.2 (or better)
* [SQLAlchemy](http://www.sqlalchemy.org/) 0.5 (or better)
* [PyXML](http://sourceforge.net/projects/pyxml/) 0.8 (or better)
* [PySqlite](http://trac.edgewall.org/wiki/PySqlite) 2.3.5 (or better)
* [flup](http://trac.saddi.com/flup) 1.0.2 (or better)
* [collectd](http://collectd.org/) 4.10.3 (or better)
* [TightVNC Java Viewer](http://www.tightvnc.com/) 1.3.10 (or better)
* [IPAexfont](http://ossipedia.ipa.go.jp/ipafont/) 1.03 (or better)
* [web.py](http://webpy.org/) 0.36 (or better)

上記の依存ソフトウェアのインストール方法を含めた一連のインストール方法は、[INSTALL](http://github.com/karesansui/karesansui/blob/master/INSTALL.md)にも記載されています。

ソースコードをハックしたい場合は以下が必要です。

* [Git](http://git-scm.com/)
* [setuptools](http://pypi.python.org/pypi/setuptools)

インストール方法
----------------
[INSTALL](http://github.com/karesansui/karesansui/blob/master/INSTALL.ja.md) をご参照ください。

ライセンスについて
------------------
KaresansuiはMITライセンスです。ソースコードは利用制約の少ないMITライセンスを採用していますので、再利用時のライセンスによる問題を軽減します。すべてのソースコードにライセンスが明記されていますので、迷うことなく利用することができるはずです。
ただし、例外として画像等のいくつかのファイルには技術的な問題でライセンス表記をしていません。
私たちは私たちが配布しているファイルについてのみ言及することができますので、それ以外のファイルについては著作者に問い合わせてください。
Karesansuiのロゴと商標に関しては、ソースツリーに含まれるTRADEMARKS.TXTをご参照ください。

このソースツリーはKaresansui以外のオープンソースプロジェクトの成果物を含んでいます。それらはKaresansuiとは異なるライセンスポリシーで配布されていることがあるので、それぞれのライセンス表記をご確認ください。

### karesansui/static/js/lib以下のJavaScriptライブラリ ###

* [jquery](http://jquery.com/) - License MIT or GPL
* [jquery.form.js](http://malsup.com/jquery/form/) - License MIT or GPL
* [jquery-tablesort](http://tablesorter.com/docs/) - License  MIT or GPL
* [jquery-plugin-autocomplete](http://bassistance.de/jquery-plugins/jquery-plugin-autocomplete/) - License  MIT or GPL
* [jCarousel](http://sorgalla.com/jcarousel/) - License  MIT or GPL
* [ajax-upload](http://valums.com/ajax-upload/) - License  MIT

謝辞
----
これらのプロジェクトに猛烈に感謝いたします。: Python, libvirt, webpy, flup, psycopg2, tightvncviewer, jquery, jquery.form.js, jquery-tablesort, jquery-plugin-autocomplete, jCarousel, ajax-upload.


連絡先
------
http://karesansui-project.info

