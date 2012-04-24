Requirement
-----------

* python-docutils >= 0.9
* python-sphinx >= 1.1.0
* python-jinja2 >= 2.3
* python-pygments >= 1.2

Setting Up
----------

To enable l10n, you need to execute the following command and generate the gettext's pot files.

    # make gettext
    # mkdir -p locale/[lang]/LC_MESSAGES   # japanese=>ja, brazil=>br

Translating
-----------

If you want to translate the documents in your own language:

######1. Generate po file.

If you want to update exising po file, you can merge translations using following approach:

    # msgmerge --update locale/[lang]/LC_MESSAGES/index.po _build/locale/index.pot

Or, if you want to generate new po file:

    # msginit --locale=[lang] --input=_build/locale/index.pot --output=locale/[lang]/LC_MESSAGES/index.po

######2. Edit po file.

Open po file, translate messages.

    # vi locale/[lang]/LC_MESSAGES/index.po 

######3. Generate mo file.

    # msgfmt locale/[lang]/LC_MESSAGES/index.po -o locale/[lang]/LC_MESSAGES/index.mo

Generating HTML Document
------------------------

If you want to change locale, _language_ parameter must be set as you like.

    # vi conf.py

Generate documents.

    # make clean html

