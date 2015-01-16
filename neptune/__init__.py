#!/usr/bin/env python

import clang.cindex

class CProjectException(Exception):

    def __init__(self, diagnostics):
        self.diagnostics = diagnostics

    def __str__(self):
        return '\n'.join(i.spelling for i in self.diagnostics)
    

class CProject:

    def __init__(self, path, args=None, max_error_severity=4):
        """Initialize a CProject

        Takes in path to entrypoint and optional args for compiling.
        """
        self.max_error_severity = max_error_severity
        self.index = clang.cindex.Index.create()
        self.path = path
        self.tu = self.index.parse(path, args)
        if self.errors:
            raise CProjectException(self.tu.diagnostics)
        
    @property
    def errors(self):
        return any(i for i in self.tu.diagnostics
                   if i.severity >= self.max_error_severity)

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
            return CodeReferece(self.cursor.referenced, self)
        except: #fix this 
            return None


# p = CProject(os.path.expanduser('~/src/stegdetect/src/stegdetect-0.6/stegdetect.c'), ' -DHAVE_CONFIG_H -I. -I. -I. -I./jpeg-6b -I./file -I./compat  -I/usr/include/gtk-1.2 -I/usr/include/glib-1.2 -I/usr/lib/glib/include -I/usr/lib/clang/3.5.0/include/ -O2 -Wall -g'.split())
# c = p.get_coderef_from(1451, 36)
