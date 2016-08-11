#!/bin/bash

# ###############################################################
# SECTION: HELPER FUNCTIONS
# ###############################################################

# Wraps standard echo by adding ESDOC prefix.
log()
{
	declare now=`date +%Y-%m-%dT%H:%M:%S`
	declare tabs=''
	if [ "$1" ]; then
		if [ "$2" ]; then
			for ((i=0; i<$2; i++))
			do
				declare tabs+='\t'
			done
	    	echo -e $now" [INFO] :: ERRATA > "$tabs$1
	    else
	    	echo -e $now" [INFO] :: ERRATA > "$1
	    fi
	else
	    echo -e $now" [INFO] :: ERRATA > "
	fi
}

# ###############################################################
# SECTION: INITIALIZE VARS
# ###############################################################

# Set of ops sub-directories.
declare -a ERRATA_OPS_DIRS=(
	$ERRATA_HOME/ops
)

# ###############################################################
# SECTION: Initialise file system
# ###############################################################

# Ensure ops paths exist.
for ops_dir in "${ERRATA_OPS_DIRS[@]}"
do
	mkdir -p $ops_dir
done
