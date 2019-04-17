#!/bin/bash
####################################################################
#### Author: SAS Institute Inc.                                 ####
####################################################################
#
# Used to start/stop/check SAS Viya Services
#

do_usage()
{
	echo "Usage: This script is used internally by SAS Viya-ARK MMSU playbooks."
}

do_stopms()
{
	LIST=$(cd /etc/init.d;ls sas-viya-* 2>/dev/null|grep -v cascontroller)
	do_stop
}

do_stopmt()
{
	LIST=$(cd /etc/init.d;ls sas-*-all-services 2>/dev/null)
	do_stop
}

do_stopcas()
{
	LIST=$(cd /etc/init.d;ls sas-*-cascontroller-default 2>/dev/null)
	do_stop
}
do_stop()
{
	NLIST=
	for p in $LIST
	do
		if [[ $p =~ -viya-all-services|-consul-|-vault-|-httpproxy-|-rabbitmq-|-sasdatasvrc- ]]; then
			continue
		fi
		NLIST="$p $NLIST"
	done

	LIST=$NLIST
	do_ps_common stop
}

do_startmt()
{
	LIST=$(cd /etc/init.d;ls sas-*-all-services 2>/dev/null| grep -v '\-viya\-')
	do_start_common
}

do_startcas()
{
	LIST=$(cd /etc/init.d;ls sas-*-cascontroller-default 2>/dev/null)
	do_start_common
}

do_start_common()
{
	do_ps_common start
}

do_ps_common()
{
	ACTION=$1
	for p in $LIST
	do
		if [[ "${SYSTYPE}" == "systemd" ]]; then
			systemctl $ACTION $p &
		else
			service $p $ACTION &
		fi
	done

	for job in $(jobs -p)
	do
		if [[ -e /proc/$job ]]; then
			wait $job || let "FAIL+=1"
		fi
	done
}

do_svastatus()
{
	CMD=/etc/init.d/sas-viya-consul-default
	if [[ ! -x $CMD ]]; then
		echo "ERROR: Could not find the service $CMD"
		exit 2
	fi

	info=$($CMD status 2>&1)
	rc=$?
	if [[ $rc != 0 ]]; then
		echo $info|grep 'is stopped' > /dev/null
		if [[ $? == 0 ]]; then
			echo "Consul is down - unable to obtain status"
			return
		else
			echo $info
			exit $rc
		fi
	fi

	LIST=$(cd /etc/init.d;ls sas-*-all-services 2>/dev/null)

	for f in $LIST
	do
		/etc/init.d/$f status|sed "s|sas-services completed|$f completed|"
	done
}

checkdb()
{
	CMD=/etc/init.d/sas-viya-sasdatasvrc-postgres
	if [[ ! -x $CMD ]]; then
		echo "ERROR: Could not find the service $CMD"
		exit 2
	fi

	info=$($CMD status 2>&1)
	rc=$?
	echo $info
	if [[ $rc != 0 ]]; then
		exit $rc
	fi
}

checkspace()
{
	if [[ ! -d "$DIR" ]]; then
		return
	fi
	FREE=$(($(stat -f --format="%a*%S" "$DIR")))
	
	if [[ "$FREE" -lt "$SIZE" ]]; then
		echo "ERROR: log directory does not have enough free space: $DIR"
		echo "ERROR: free space: $FREE, minimum requirement: $SIZE"
		exit 1	
	fi
}

dolist_start()
{
	echo "start"
	do_start_common
}

dolist_stop()
{
	echo "stop"
}
######
# main
######
SYSTYPE=$(ps -p 1 | grep -v PID | awk '{ print $4 }')

OPT=$1
case "$OPT" in
	stopms|stopmt|startmt|startcas|stopcas|svastatus)
		FAIL=0; do_$OPT; exit $FAIL ;;
	checkdb)
		$OPT; exit $? ;;
	start|stop)
		shift 1
		LIST=$*
		do_ps_common $OPT
		;;
	checkspace)
		DIR=$2; SIZE=$3
		$OPT; exit $? ;;
	*)
		do_usage; exit 1 ;;
esac
