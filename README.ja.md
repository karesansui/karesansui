Karesansui
==========

Karesansuiは、日本発のオープンソースの仮想化管理アプリケーションです。

 * 複雑な部分を抽象化した、シンプルで直観的なWebインターフェース。
 * GPL+LGPLライセンスで提供されるフリーソフトウェアであり、個人ユース、商用を問わず無料で利用することができます。
 * Kernel-based Virtual Machine(KVM)に対応しています。今後、他の仮想化技術／ハイパーバイザーにも対応する予定です。
 * 多言語対応しています。現在は日本語と英語をサポートしています。

インストール方法
----------------
INSTALL をご参照ください。

ライセンスについて
------------------
Karesansuiの一部はLGPLで、一部はGPLです。コア部分のソースコードは利用制約の少ないLGPLライセンスを採用していますので、再利用時のライセンスによる問題を軽減します。すべてのソースコードにライセンスが明記されていますので、迷うことなく利用することができるはずです。 

ただし、例外としていくつかのファイルには技術的な問題でライセンス表記をしていません。
このソースツリーに含まれるtemplate/default/include以下のファイルはLGPLです。その他のtemplate/default以下のファイルはGPLです。
これは、あなたがあなたの書いたオリジナルのファイルをtemplate/defaultにファイルを置く場合GPLを付さないといけないということは意味しません。また、template/default/includeにファイルを置く場合はLGPLを付さないといけないということは意味しません。
また、template/defaultやtemplate/default/includeに誰かがファイルを置き、それがライセンス表記されていなかったら、GPLやLGPLが付されたということにはなりません。私たちは私たちが配布しているファイルについてのみ言及することができますので、それ以外のファイルについては著作者に問い合わせてください。

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

