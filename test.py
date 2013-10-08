#!/usr/bin/python2

import sys
import hashlib
import base64

salt = "c5d22d1f16b8"

def authenticate_from_file(uname, passwd):
    f = open('users.txt', 'r')
    for l in f:
        t = l.split(' ')
        sha = hashlib.sha1()
        sha.update(passwd)
        sha.update(salt)
        print "comparing " + base64.b64encode(sha.digest()) + " with " + t[1]
        if uname == t[0] and sha.digest() == base64.b64decode(t[1]):
            return True
    return False

if authenticate_from_file(sys.argv[1], sys.argv[2]):
    print "OK"
else:
    print "NO"