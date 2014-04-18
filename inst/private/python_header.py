import sys
sys.ps1 = ""; sys.ps2 = ""
import sympy as sp
from sympy import *
#import dill as pickle


def dbout(l):
    sys.stderr.write("pydebug: " + str(l) + "\n")


def objectfilter(x):
    """Perform final fixes before passing objects back to Octave"""
    if isinstance(x, sp.Matrix) and x.shape == (1,1):
        #dbout("Note: replaced 1x1 mat with scalar")
        y = x[0,0]
    else:
        y = x
    return y


# Single quotes must be replaced with two copies, escape not enough
# Please no extra blank lines within functions (breaks interpret from stdin)
# FIXME: unicode probably do not have enough escaping, but cannot string_escape
def octcmd(x):
    x = objectfilter(x)
    if isinstance(x, (sp.Basic,sp.Matrix)):
        # could escape, but does single quotes too
        #_srepr = sp.srepr(x).encode("string_escape").replace("'", "''")
        _srepr = sp.srepr(x).replace("'", "''")
        _str = str(x).encode("string_escape").replace("'", "''")
        _pretty_ascii = \
        sp.pretty(x,use_unicode=False).encode("string_escape").replace("'", "''")
        _pretty_unicode = \
        sp.pretty(x,use_unicode=True).encode("utf-8").replace("\n","\\n").replace("'", "''")
        if isinstance(x, sp.Matrix):
            _d = x.shape
            s = "sym('" +  _srepr  + "'" + \
                ", [" +  str(_d[0]) + ' ' + str(_d[1])  + ']' + \
                ", '" +  _str  + "'" + \
                ", sprintf('" +  _pretty_ascii  + "')" + \
                ")"
        else:
            if not isinstance(x, sp.Expr):
                dbout("Treating unknown sympy as scalar: " + str(type(x)))
            s = "sym('" +  _srepr  + "'" + \
                ", [1 1]" + \
                ", '" +  _str  + "'" + \
                ", sprintf('" +  _pretty_ascii  + "')" + \
                ")"
    elif isinstance(x, bool) and x:
        s = "true"
    elif isinstance(x, bool) and not x:
        s = "false"
    elif isinstance(x, (list,tuple)):
        s = "{"
        for y in x:
            s = s + octcmd(y) + ",  "
        s = s + "}"
    elif isinstance(x, int):
        s = str(x)
    elif isinstance(x, float):
        # FIXME: see Bug #11
        s = "%.20g" % x
    elif isinstance(x, str):
        s = "sprintf('" + x.encode("string_escape").replace("'", "''") + "')"
    elif isinstance(x, unicode):
        # not .encode("string_escape")
        s = "sprintf('" + \
          x.encode("utf-8").replace("\n","\\n").replace("'", "''") + "')"
    elif isinstance(x, dict):
        # Note: the dict cannot be too complex: the keys need to be convertable
        # to strings with str().  E.g., cannot be integers or (complicated) sym.
        s = "struct("
        for key,val in x.iteritems():
            s = s + "'" + str(key) + "', " + octcmd(val) + ", "
        if len(x) >= 1:
            s = s[:-2]
        s = s + ")"
    else:
        s = "error('python does not know how to export type " + str(type(x)).replace("'", "''") + "')"
    return s

