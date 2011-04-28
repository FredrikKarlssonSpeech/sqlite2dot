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

#puts "TABLES: $tables"

append out  "digraph structs \{\n"
#append out  "\trankdir=LR\n"
append out  "\tnode \[shape=record,width=4\];\n"

foreach currtab $tables {

	set isFirst 1
	set keyLst [list ]
	#$currtab Field]
	set valLst [list ]
	#{} Value]
	
	db eval [format {PRAGMA table_info(%s);} $currtab] vals {
		lappend keyLst $vals(name) 
		lappend valLst $vals(type)
		
#		if {$isFirst} {
#			append out [format {		%s [label="{<%s> %s | %s} } $currtab $vals(name) $vals(name) $vals(type)] 
#		} else {
#			append out [format {|{<%s> %s | %s} } $vals(name) $vals(name) $vals(type)]
#		}
#		set isFirst 0
	}
	#parray valsArr
	set keyOut ""
	foreach currkey $keyLst {
		append keyOut [format {<%s> %s |} $currkey $currkey]
	}
	set keyOut [string trimright $keyOut "|"]
	#puts $keyOut
	set valOut [join $valLst " | "]
	#puts $valOut
	#append out {"];}

	append out [format {	%s [label="{\N | %s } | { | %s }"];} $currtab $keyOut $valOut]
	append out "\n"
	
	db eval [format {PRAGMA foreign_key_list(%s);} $currtab] vals {
		append out [format {			%s:%s -> %s:%s;} $currtab $vals(from) $vals(table) $vals(to) ]
		append out "\n"
	}
}

append out "\}"
puts $out

