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

