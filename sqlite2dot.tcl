#  Copyright (c) 2011, Fredrik Karlsson
#  All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#  3. All advertising materials mentioning features or use of this software
#     must display the following acknowledgement:
#  4. Neither the name of the main author nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY FREDRIK KARLSSON ''AS IS'' AND ANY
#  EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL FREDRIK KARLSSON BE LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


package require sqlite3

if {[llength $argv] != 1} {
	
	puts stderr "Wrong number of arguments"
	puts stderr "Should be: \n\nsqlite2dot.tcl <database file>"
	exit
}

sqlite3 db [lindex $argv 0]

db eval {select name from sqlite_master where type = "table" and name NOT LIKE "%sqlite_%"} {
	lappend tables $name

}



append out  "digraph structs \{\n"
append out  "\tnode \[width=4,shape=plaintext\];\n"

foreach currtab $tables {

	set isFirst 1
	set rows ""
	db eval [format {PRAGMA table_info(%s);} $currtab] vals {
		append rows [format {<TR><TD PORT="%s" ALIGN="LEFT">%s</TD><TD ALIGN="LEFT">%s</TD></TR>} $vals(name) $vals(name)  $vals(type)]
		append rows "\n"
	}


	append out [format {			%s [label=<<TABLE PORT="%s" BORDER="0"><TR><TD BGCOLOR="grey" COLSPAN="2">%s</TD></TR>%s</TABLE>>];} $currtab $currtab $currtab $rows]
	append out "\n"
	
	db eval [format {PRAGMA foreign_key_list(%s);} $currtab] vals {
		append out [format {			%s:%s -> %s:%s [arrowhead=vee,style=dotted];} $currtab $vals(from) $vals(table) $vals(to) ]
		append out "\n"
	}
}

append out "\}"
puts $out

