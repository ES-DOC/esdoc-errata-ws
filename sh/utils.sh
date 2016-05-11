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

# Outputs a line to split up logging.
log_banner()
{
	echo "-------------------------------------------------------------------------------"
}

# Resets temporary folder.
reset_tmp()
{
	rm -rf $ERRATA_DIR_TMP/*
	mkdir -p $ERRATA_DIR_TMP
}

# Assigns the current working directory.
set_working_dir()
{
	if [ "$1" ]; then
		cd $1
	else
		cd $ERRATA_HOME
	fi
}

# Removes all files of passed type in current working directory.
remove_files()
{
	find . -name $1 -exec rm -rf {} \;
}

# ###############################################################
# SECTION: INITIALIZE PATHS
# ###############################################################

# Define core directories.
declare ERRATA_DIR_BASH=$ERRATA_HOME/sh
declare ERRATA_DIR_WS_JOBS=$ERRATA_HOME/jobs
declare ERRATA_DIR_TEST_DATA=$ERRATA_HOME/test-data

