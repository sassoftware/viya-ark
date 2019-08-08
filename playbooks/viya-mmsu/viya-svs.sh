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

        if ! [[ $LIST = *[!\ ]* ]]; then
                return 0
        fi

	for p in $LIST
	do
		if [[ $p =~ -all-services ]]; then
			/etc/init.d/$p $ACTION &
		else
			do_service $p
		fi
	done

	for job in $(jobs -p)
	do
		if [[ -e /proc/$job ]]; then
			wait $job || let "FAIL+=1"
		fi
	done

	if [[ $FAIL -gt 0 ]]; then
		echo "ERROR: service $ACTION failed"
		return $FAIL
	fi
}

do_service()
{
	service=$*

	if [[ "${SYSTYPE}" == "systemd" ]]; then
		systemctl $ACTION $service &
	else
		service $service $ACTION &
	fi
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
			echo "$info"
			exit $rc
		fi
	fi

	LIST=$(cd /etc/init.d;ls sas-*-all-services 2>/dev/null)

	for f in $LIST
	do
		/etc/init.d/$f status|sed "s|sas-services completed|$f completed|"
	done
}

do_checkdb()
{
	CMD=/etc/init.d/sas-viya-sasdatasvrc-${dbname}
	if [[ ! -x $CMD ]]; then
		#echo "ERROR: Could not find the service $CMD"
		#exit 2
		continue
	fi

	info=$($CMD status 2>&1)
	rc=$?
	echo "$info"
	if [[ $rc != 0 ]]; then
		exit $rc
	fi
}

do_startdb()
{
	cd /etc/init.d
	if [[ -f "sas-viya-sasdatasvrc-${dbname}" ]]; then
		LIST="
		sas-viya-sasdatasvrc-${dbname}-pgpool0-ct-pcp
		sas-viya-sasdatasvrc-${dbname}-pgpool0-ct-pgpool
		sas-viya-sasdatasvrc-${dbname}-pgpool0-ct-pool_hba
		sas-viya-sasdatasvrc-${dbname}
		"
	fi

	do_ps_common start
}

do_stopdb()
{
	cd /etc/init.d
	if [[ -f "sas-viya-sasdatasvrc-${dbname}" ]]; then
		LIST="
		sas-viya-sasdatasvrc-${dbname}
		sas-viya-sasdatasvrc-${dbname}-pgpool0-ct-pool_hba
		sas-viya-sasdatasvrc-${dbname}-pgpool0-ct-pgpool
		sas-viya-sasdatasvrc-${dbname}-pgpool0-ct-pcp
		"
	fi

	do_ps_common stop
}

do_startdbct()
{
	cd /etc/init.d
	LIST=$(find . -name "sas-viya-sasdatasvrc-${dbname}-node*-ct-*"| cut -c3-)

	do_ps_common start
}

do_stopdbct()
{
	cd /etc/init.d
	LIST=$(find . -name "sas-viya-sasdatasvrc-${dbname}-node*-ct-*"| cut -c 3-)

	do_ps_common stop
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

do_cleancomp()
{
	LIST=$(ps -o "user pid ppid cmd" |grep -E '/opt/sas/spre/|/opt/sas/viya/'|grep compsrv)
	echo "$LIST"
	NLIST=$(echo "$LIST"|awk '{print $2}')

	for p in $NLIST
	do
		echo "kill -KILL $p 2>/dev/null"
		kill -KILL $p 2>/dev/null
	done
	return 0
}

do_geturls()
{
	FILE=
	host=$(hostname -f)
	if [[ -f /etc/httpd/conf.d/proxy.conf ]]; then
		FILE=/etc/httpd/conf.d/proxy.conf
	elif [[ -f /etc/apache2/conf.d/proxy.conf ]]; then
		FILE=/etc/apache2/conf.d/proxy.conf
	fi
	if [[ "$FILE" == "" ]]; then
		echo "No SAS Viya URLs found"
	else
		cat $FILE|grep ProxyPass|grep -e "/SAS"|awk "{print \$2}"|sort|uniq|sed "s/^/http:\/\/"$host"/"
	fi
	return 0
}

######
# main
######
SYSTYPE=$(ps -p 1 | grep -v PID | awk '{ print $4 }')

OPT=$1
case "$OPT" in
	stopms|stopmt|startmt|startcas|stopcas|svastatus)
		FAIL=0; do_$OPT; exit $FAIL ;;
	startdbct|startdb|stopdb|stopdbct)
		shift 1
		dbname=$1
		FAIL=0; do_$OPT; exit $FAIL ;;
	checkdb)
		shift 1
		dbname=$1
		do_$OPT; exit $? ;;
	start|stop)
		shift 1
		TLIST=$*
		LIST=
		for l in $TLIST
		do
			if [[ -x "/etc/init.d/$l" ]]; then
				LIST="$l $LIST"
			fi
		done

		do_ps_common $OPT
		;;
	cleancomp)
		do_$OPT
		;;
	checkspace)
		DIR=$2; SIZE=$3
		$OPT; exit $? ;;
	geturls)
		do_$OPT
		;;
	checkps)
		shift 1
		CNT=$*
		if [[ "$CNT" != "" ]]; then
			ps -ef|grep -E '/opt/sas/spre/|/opt/sas/viya/|pgpool'|grep -v grep|tail $CNT
		else
			ps -ef|grep -E '/opt/sas/spre/|/opt/sas/viya/|pgpool'|grep -v grep|awk '{print}'
		fi
		exit 0
		;;
	*)
		do_usage; exit 1 ;;
esac
