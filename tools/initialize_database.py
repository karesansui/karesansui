#!/usr/bin/env python

import sys, os
import socket
import re
import string
from optparse import OptionParser
import traceback

try:
    from distutils.sysconfig import get_python_lib
    sys.real_prefix = '/usr';
    sys.path.append(get_python_lib(0,0))
except:
    pass

try:
    import sqlalchemy
    import karesansui
    from karesansui import __version__
    from karesansui.lib.utils import is_uuid, is_int
    from karesansui.lib.utils import generate_phrase, generate_uuid, string_from_uuid
    from karesansui.lib.file.k2v import K2V
    from karesansui.lib.crypt import sha1encrypt
    from karesansui.lib.const import MACHINE_ATTRIBUTE, MACHINE_HYPERVISOR
    from karesansui.db import get_engine, get_metadata, get_session
    from karesansui.db.model.user import User
    from karesansui.db.model.notebook import Notebook
    from karesansui.db.model.tag import Tag
    from karesansui.db.model.machine import Machine

except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    # basic
    optp.add_option('-m', '--email',    dest='email',    help=_("E-mail Address"), default="root@localhost")
    optp.add_option('-p', '--password', dest='password', help=_("Password"),       default="")
    optp.add_option('-l', '--lang',     dest='lang',     help=_("Language"),       default="")
    optp.add_option('-f', '--host',     dest='fqdn',     help=_("FQDN"),           default="")
    optp.add_option('-u', '--uuid',     dest='uuid',     help=_("UUID"),           default="")

    return optp.parse_args()

def chkopts(opts):
    from karesansui.lib.utils import generate_phrase, generate_uuid, string_from_uuid, is_uuid
    from karesansui.lib.const import DEFAULT_LANGS

    reg_email = re.compile("^[a-zA-Z0-9\./_-]{1,}@[a-zA-Z0-9\./-]{4,}$")
    if opts.email:
        if reg_email.search(opts.email) is None:
            raise Exception('ERROR: Illigal option value. option=%s value=%s' % ('-m or --email', opts.email))
    else:
        raise Exception('ERROR: %s option is required.' % '-m or --email')

    reg_passwd = re.compile("^.{5,}")
    if opts.password:
        if reg_passwd.search(opts.password) is None:
            raise Exception('ERROR: Illigal option value. option=%s value=%s' % ('-p or --password', opts.password))
    else:
        pass

    if opts.password == "":
        opts.password = generate_phrase(8)

    if opts.uuid:
        if is_uuid(opts.uuid) is False:
            raise Exception('ERROR: Illigal option value. option=%s value=%s' % ('-u or --uuid', opts.uuid))
    else:
        pass

    if opts.uuid == "":
        opts.uuid = string_from_uuid(generate_uuid())

    reg_fqdn = re.compile("^[a-z0-9][a-z0-9\.\-]{2,}$")
    if opts.fqdn:
        if reg_fqdn.search(opts.fqdn) is None:
            raise Exception('ERROR: Illigal option value. option=%s value=%s' % ('-f or --fqdn', opts.fqdn))
    else:
        pass

    if opts.fqdn == "":
        opts.fqdn = socket.gethostname() 

    reg_lang = re.compile("^[a-z]{2}_[A-Z]{2}$")
    if opts.lang:
        if reg_lang.search(opts.lang) is None:
            raise Exception('ERROR: Illigal option value. option=%s value=%s' % ('-l or --lang', opts.lang))
    else:
        pass

    if opts.lang == "":
        try:
            DEFAULT_LANGS[os.environ["LANG"][0:5]]
            opts.lang = os.environ["LANG"][0:5]
        except:
            opts.lang = "en_US"


karesansui.config = K2V("/etc/karesansui/application.conf").read()

(opts, args) = getopts()
#print opts
chkopts(opts)

for k in dir(opts):
    v = getattr(opts,k)
    if type(v) == str and k[0:2] != "__":
        exec("%s = '%s'" % (k, v,))

#print opts
#sys.exit()

engine = get_engine()
metadata = get_metadata()

try:
    metadata.drop_all()   
    metadata.tables['machine2jobgroup'].create()
    metadata.create_all()   
except Exception, e:
    traceback.format_exc()
    raise Exception('Initializing/Updating a database error - %s' % ''.join(e.args))

session = get_session()
try:
    (password, salt) = sha1encrypt(u"%s" % password)
    user = session.query(User).filter(User.email == email).first()

    if user is None:
        # User Table set.
        new_user  = User(u"%s" % email,
                              unicode(password),
                              unicode(salt),
                              u"Administrator",
                              u"%s" % lang,
                              )

        if string.atof(sqlalchemy.__version__[0:3]) >= 0.6:
            session.add(new_user)
        else:
            session.save(new_user)
        session.commit()
    else:
        user.password  = password
        user.salt      = salt
        user.languages = lang
        if string.atof(sqlalchemy.__version__[0:3]) >= 0.6:
            session.add(user)
        else:
            session.update(user)
        session.commit()

    # Tag Table set.
    tag = Tag(u"default")
    if string.atof(sqlalchemy.__version__[0:3]) >= 0.6:
        session.add(tag)
    else:
        session.save(tag)
    session.commit()
        
    # Machine Table set.
    user     = session.query(User).filter(User.email == email).first()
    notebook = Notebook(u"", u"")
    machine  = Machine(user,
                       user,
                       u"%s" % uuid,
                       u"%s" % fqdn,
                       MACHINE_ATTRIBUTE['HOST'],
                       MACHINE_HYPERVISOR['REAL'],
                       notebook,
                       [tag],
                       u"%s" % fqdn,
                       u'icon-guest1.png',
                       False,
                       None,
                      )

    if string.atof(sqlalchemy.__version__[0:3]) >= 0.6:
        session.add(machine)
    else:
        session.save(machine)
    session.commit()

    session.close()
except Exception, e:
    traceback.format_exc()
    raise Exception('Initializing/Updating a database error - %s' % ''.join(e.args))

