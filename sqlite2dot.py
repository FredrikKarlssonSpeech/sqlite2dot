# -*- coding: utf-8 -*-

# Copyright (c) 2015, Françoise Conil
# Copyright (c) 2011, Fredrik Karlsson
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this 
#    list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice, 
#    this list of conditions and the following disclaimer in the documentation 
#    and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors 
#    may be used to endorse or promote products derived from this software without 
#    specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY 
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING 
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
This is a python version of Fredrik Karlsson sqlite2dot TCL script.

Those scripts aim at providing a visualization of a SQLite schema by creating a .dot file 
for use with the Graphwiz program.
"""

import sys
import os

import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def sqlite_db_tables(c=None):
    """
    List the tables of a sqlite database.
    How do I list all tables/indices contained in an SQLite database :
        https://www.sqlite.org/faq.html#q7
    """
    db_tables = []

    if c is not None:
        c.execute('select name from sqlite_master where type = "table" and name NOT LIKE "%sqlite_%"')

        rows = c.fetchall()

        for r in rows:
            db_tables.append(r['name'])

    return db_tables

def sqlite_table_columns(c=None, table=None):
    """
    The PRAGMA statement is an SQL extension specific to SQLite and used to modify the operation of the SQLite library or to query the SQLite library for internal (non-table) data.
    https://sqlite.org/pragma.html
    """
    db_columns = []

    if c is not None and table is not None:
        c.execute('PRAGMA table_info("{0}")'.format(table))

        rows = c.fetchall()

        for r in rows:
            db_columns.append(r)

    return db_columns

def sqlite_table_foreign_keys(c=None, table=None):
    """
    """
    db_fk = []

    if c is not None and table is not None:
        c.execute('PRAGMA foreign_key_list({0})'.format(table))

        rows = c.fetchall()

        for r in rows:
            db_fk.append(r)

    return db_fk

def sqlite_table_indexes(c=None, table=None):
    """
    """
    db_index = {}

    if c is not None and table is not None:
        c.execute('PRAGMA index_list({0})'.format(table))

        rows = c.fetchall()

        for r in rows:
            db_index[r['name']] = {}
            db_index[r['name']]['infos'] = r

        for idx in db_index.keys():
            c.execute('PRAGMA index_info({0})'.format(idx))

            rows = c.fetchall()

            db_index[idx]['composed_of'] = []
            for r in rows:
                db_index[idx]['composed_of'].append(r)

    return db_index

def write_graphiz_graph(db_struct=None, db_filename=None):
    """
    http://graphviz.org/Documentation.php

    Would it be interesting to use the python graphviz package ?
    https://pypi.python.org/pypi/graphviz/
    """
    gviz_filename = None

    if db_struct is not None and db_filename is not None:
        # Generates a .dot filename from the db filename
        gviz_filename = '{0}.dot'.format(os.path.splitext(db_filename)[0])

        with open(gviz_filename, 'w') as f:
            #f.write('digraph structs {\n')
            f.write('digraph {\n')
            f.write('\t\trankdir=LR;\n')
            f.write('\t\tlabel="{0}";\n'.format(os.path.split(db_filename)[1]))
            f.write('\t\tlabelloc="t";\n')

            for tname, tstruct in db_struct.items():
                #f.write('\tsubgraph cluster_{0} {1}\n'.format(tname, '{'))
                f.write('\t\tnode [shape=none];\n')
                #f.write('\t\tlabel=\"{0}\";\n'.format(tname))
                #f.write('\t\trank=same;\n')
                #f.write('\t\tclusterrank=local;\n')
                #f.write('\t\tlabeljust=l;\n')
                #f.write('\t\tstyle=dotted;\n')

                rows = []
                for cols in tstruct['columns']:
                    rows.append('<tr><td port="{0}" align="left" bgcolor="lavender">{0}</td><td align="left" port="{0}_type" bgcolor="lavender">{1}</td></tr>'.format(cols['name'], cols['type'].lower()))

                irows = []
                if len(tstruct['idx']) > 0:
                    for idx in tstruct['idx'].keys():
                        if tstruct['idx'][idx]['infos']['unique']:
                            rows.append('<tr><td port="{0}" align="left" colspan="2" bgcolor="gold">{0}</td></tr>'.format(idx))
                        else:
                            rows.append('<tr><td port="{0}" align="left" colspan="2" bgcolor="cornsilk">{0}</td></tr>'.format(idx))

                f.write('\t\t{0} [label=<<table port="{0}" border="1" cellspacing="0"><tr><td bgcolor="steelblue" colspan="2"><font color="cornsilk">{0}</font></td></tr>{1}{2}</table>>];\n'.format(tname, 
                                                                                                                                                         "".join(rows),
                                                                                                                                                         "".join(irows)))

                if len(tstruct['idx']) > 0:
                    for idx in tstruct['idx'].keys():
                        for idxinfo in tstruct['idx'][idx]['composed_of']:
                            f.write('\t\t{0}:{1} -> {0}:{2} [label="{3:d}" style=solid color=steelblue arrowhead=normal arrowtail=diamond dir=both arrowsize=0.6];\n'.format(tname, idx, idxinfo['name'], idxinfo['seqno']))

                for fk in tstruct['fk']:
                    f.write('\t\t{0}:{1} -> {2}:{3} [arrowtype=open style=solid color=red];\n'.format(tname, fk['from'], fk['table'], fk['to']))

                #f.write('\t}\n')

            f.write('}\n')
            f.close()

    return gviz_filename

def generate_png(dot_filename=None):
    """
    $ dot -T png -o netpredictions.png firefox_fc/netpredictions.dot
    """
    if dot_filename is not None:
        png_filename = '{0}.png'.format(os.path.splitext(dot_filename)[0])

        os.system('dot -Tpng -o {0} {1}'.format(png_filename, dot_filename))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: {0} fullpath-to-database-file-to-analyse'.format(sys.argv[0]))

    db_filename = sys.argv[1]

    if not os.path.isfile(db_filename):
        sys.exit('ERROR: database file {0} was not found !'.format(db_filename))

    # No error in sqlite3.connect() or conn.cursor() if the 
    # file is not an sqlite file
    # There is just a DatabaseError exception when a query is made :/
    valid_db = True
    conn = sqlite3.connect(db_filename)

    # To get a dictionary with column names when executing queries
    # https://docs.python.org/2/library/sqlite3.html#connection-objects
    conn.row_factory = dict_factory

    c = conn.cursor()

    try:
        c.execute('select name from sqlite_master')
    except sqlite3.DatabaseError:
        valid_db = False

    if valid_db:
        db_struct = {}
        tables = sqlite_db_tables(c)

        for t in tables:
            db_struct[t] = {}

            cols = sqlite_table_columns(c, t)
            db_struct[t]['columns'] = cols

            fk = sqlite_table_foreign_keys(c, t)
            db_struct[t]['fk'] = fk

            idx = sqlite_table_indexes(c, t)
            db_struct[t]['idx'] = idx

        dot_file = write_graphiz_graph(db_struct, db_filename)

        generate_png(dot_file)

    conn.close()

    print('End of analyze')
