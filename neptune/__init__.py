#!/usr/bin/env python

import os
from md5 import md5
import clang.cindex

class CProjectException(Exception):

    def __init__(self, diagnostics):
        self.diagnostics = diagnostics

    def __str__(self):
        return '\n'.join(i.spelling for i in self.diagnostics)
    

class CProject:

    def __init__(self, db_path, load=True)
        """Initialize a CProject. Constructs a DB
        
        """
        self.db_path = db_path)
        self.tus = []
        if os.path.exists(self.db_path):
            self.load_tus()
        elif load:
            os.path.mkdir(self.db_path)
        self.index = clang.cindex.Index.create()

    @property
    def files(self):
        return (tu.spelling for tu in tus)

    def create_tu_from_file(self, path=None, args=None, max_error_severity=4):
        self.max_error_severity = max_error_severity
        self.path = path
        tu = self.index.parse(path, args)
        if self.errors:
            raise CProjectException(tu.diagnostics)
        self.tus.append(tu)

    def create_tu_from_ast(self, path):
        tu = self.index.read(path)
        self.tus.append(tu)

    def load_tus(self):
        for f in os.listdir(self.path):
            path = os.path.join(self.path, f)
            self.create_tu_from_ast(path)

    def save_tus(self):
        for tu in tus:
            filename = md5(tu.spelling).hexdigest()
            tu.save(os.path.join(self.path, filename))
        
    @property
    def errors(self):
        return any(i for i in self.tu.diagnostics
                   if i.severity >= self.max_error_severity)

    def get_xrefs_for(self, name):
        pass
        # for i in self.tu.get_includes():
        #     pass
        #get_tokens
        #c.walk_preorder

    #can't use emcas column numbers, they are wrong
    def get_coderef_from(self, line, column, path=None):
        cfile = clang.cindex.File.from_name(self.tu, path or self.path)
        clocn = clang.cindex.SourceLocation.from_position(self.tu,
                                                          cfile,
                                                          line,
                                                          column)
        cursor = clang.cindex.Cursor().from_location(self.tu,
                                                     clocn)

        return CodeReferece(cursor, self)


class CodeReferece:

    def __init__(self, cursor, parent):
        self.parent = parent
        self.cursor = cursor
        self.tu = parent.tu
        self.clocn = cursor.location

    def __repr__(self):
        return '<{} "{}" at {}:{},{}>'.format(self.__class__.__name__,
                                              self,
                                              self.clocn.file.name,
                                              self.clocn.line,
                                              self.clocn.column)

    def __str__(self):
        return self.cursor.displayname

    def get_location_tuple(self):
        return (self.clocn.file.name,
                self.clocn.line,
                self.clocn.column)

    @property
    def literal(self):
        e = self.cursor.extent
        filename = e.start.file.name
        start = e.start.offset
        end = e.end.offset
        with open(filename) as sfd:
            sfd.seek(start)
            data = sfd.read(end-start)
        return data

    @property
    def line(self):
        filename = self.clocn.file.name
        with open(filename) as sfd:
            offset = self.clocn.offset
            sfd.seek(offset - 1)
            while sfd.read(1) != '\n':
                offset-=2
                sfd.seek(offset)
            sfd.read(1)
            data = sfd.readline()
        return data

    @property
    def refdef(self):
        try:
            return CodeReferece(self.cursor.get_definition(), self)
        except: #fix this 
            return None

    @property
    def name(self):
        return self.cursor.spelling #is this always right?

    def get_xrefs_for(self, name):
        self.parent.get_xrefs_for(name)
    
    @property
    def xrefs(self):
        self.get_xrefs_for(self.name)


def init_db():
    from sys import argv
    path = os.path.expanduser(os.path.expandvars(sys.argv.pop()))
    c = CProject(os.env.get('NEPTUNE_DB_PATH'))
    c.create_tu_from_file(path, argv)
    c.save_tus()

    
# p = CProject(os.path.expanduser('~/src/stegdetect/src/stegdetect-0.6/stegdetect.c'), ' -DHAVE_CONFIG_H -I. -I. -I. -I./jpeg-6b -I./file -I./compat  -I/usr/include/gtk-1.2 -I/usr/include/glib-1.2 -I/usr/lib/glib/include -I/usr/lib/clang/3.5.0/include/ -O2 -Wall -g'.split())
# c = p.get_coderef_from(1451, 36)
