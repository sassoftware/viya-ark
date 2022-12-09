#!/bin/bash
####################################################################
#### Author: SAS Institute Inc.                                 ####
####################################################################
#
# Copyright (c) 2019-2022, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
#
# Used to start/stop/check SAS Viya Services
#

do_usage()
{
	echo "Usage: This script is used internally by SAS Viya-ARK MMSU playbooks."
}

do_stopms()
{
	local LIST=$(ls sas-viya-* 2>/dev/null|grep -v cascontroller)
	do_stop "$LIST"
}

do_stopmt()
{
	local LIST=$(ls sas-*-all-services 2>/dev/null)
	do_stop "$LIST"
}

do_stopcas()
{
	local LIST=$(ls sas-*-cascontroller-* 2>/dev/null)
	do_stop "$LIST"
}
do_stop()
{
	local LIST=$*
	local NLIST=
	for p in $LIST
	do
		if [[ $p =~ -viya-all-services|-consul-|-vault-|-httpproxy-|-rabbitmq-|-sasdatasvrc- ]]; then
			continue
		fi
		NLIST="$p $NLIST"
	done

	LIST=$NLIST
	do_ps_common stop "$LIST"
}

do_startmt()
{
	local LIST=$(ls sas-*-all-services 2>/dev/null| grep -v '\-viya\-')
	if [[ -x "sas-viya-runlauncher-default" ]]; then
		LIST="sas-viya-runlauncher-default $LIST"
	fi
	if [[ -x "sas-viya-spawner-default" ]]; then
		LIST="sas-viya-spawner-default $LIST"
	fi
	
	do_start_common "$LIST"
}

do_startcas()
{
	local LIST=$(ls sas-*-cascontroller-* 2>/dev/null)
	do_start_common "$LIST"
}

do_start_common()
{
	local LIST=$*
	do_ps_common start "$LIST"
}

do_ps_common()
{
	local ACTION=$1
	shift
	local LIST=$*
	LIST=$(echo $LIST)

        if [[ "$LIST" == "" ]]; then
                return 0
        fi

	if [[ "$DEBUG" != "" ]]; then
		echo "viyasvs: LIST=($LIST)"
		return 0
	fi

	for p in $LIST
	do
		if [[ $p =~ -all-services ]]; then
			/etc/init.d/$p $ACTION &
		else
			check_svcignore $p
			if [[ $? == 0 ]]; then
				do_service $ACTION $p
			fi
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
	mode=$1
	shift 1
	service=$*

	if [[ "$DEBUG" != "" ]]; then
		echo "viyasvs: systemctl $mode $service"
		return 0
	fi

	if [[ "${SYSTYPE}" == "systemd" ]]; then
		systemctl $mode $service &
	else
		service $service $mode &
	fi
	return $!
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
		echo $info|grep -q 'is stopped'
		if [[ $? == 0 ]]; then
			echo "Consul is down - unable to obtain status"
			return
		else
			echo "$info"
			exit $rc
		fi
	fi

	LIST=$(ls sas-*-all-services 2>/dev/null)

	for f in $LIST
	do
		/etc/init.d/$f status| sed "s|sas-viya-all-services completed|$f completed|;\
			s|sas-services completed|$f completed|"
	done
	return 0
}

do_checkdb()
{
	if [[ "$viya35" == "1" ]]; then
		CMD=/etc/init.d/sas-viya-sasdatasvrc-${dbname}-pgpool${dbnum}
	else
		CMD=/etc/init.d/sas-viya-sasdatasvrc-${dbname}
	fi
	if [[ ! -x $CMD ]]; then
		echo "Warning: Could not find the service $CMD"
		#exit 2
		return
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
	if [[ "$viya35" == "1" ]]; then
		dbnum=$dbarg2
		get_dbnuminfo pgpool
		if [[ -x "$DBDIR/pgpool${dbnuminfo}/startall" ]]; then
			if [[ "$DEBUG" == "" ]]; then
				check_consul
				if [[ $? == 0 ]]; then
				    check_vault
				    if [[ $? == 0 ]]; then
					#status: is running not sufficient
					dbstatus=$(/etc/init.d/sas-viya-sasdatasvrc-${dbname}-pgpool${dbnuminfo} status)
					if [[ $? == 0 ]]; then
						dbstatus=$(echo "$dbstatus"|grep 'node_id')
						if [[ "$dbstatus" == "" ]]; then
							su - sas -c "$DBDIR/pgpool${dbnuminfo}/startall"
							FAIL=$?
						fi
					else
						echo "ERROR: command error: sas-viya-sasdatasvrc-${dbname}-pgpool${dbnuminfo} status"
						exit 1
					fi
				    else
					echo "ERROR: vault service is not running or not ready"
				    fi
				else
					echo "ERROR: consul has issue, need to be fixed before starting pgpool"
					exit 1
				fi
			fi
		else
			echo "ERROR: postgres install issue, file not found: $DBDIR/pgpool${dbnuminfo}/startall"
			exit 1
		fi
	else
		if [[ -f "sas-viya-sasdatasvrc-${dbname}" ]]; then
			LIST="
			sas-viya-sasdatasvrc-${dbname}-pgpool0-ct-pcp
			sas-viya-sasdatasvrc-${dbname}-pgpool0-ct-pgpool
			sas-viya-sasdatasvrc-${dbname}-pgpool0-ct-pool_hba
			sas-viya-sasdatasvrc-${dbname}
			"
			do_ps_common start "$LIST"
		fi
	fi
}

do_stopdb()
{
	local LIST
	if [[ "$viya35" == "1" ]]; then
		check_vault
		if [[ $? != 0 ]]; then
			echo "Warning: vault service is not running"
			return
		fi
		
		dbnum=$dbarg2
		dbtype=$dbarg3
		if [[ "$dbtype" == "node" || "$dbtype" == "pgpool" ]]; then
			get_dbnuminfo "$dbtype"
			if [[ -x "$DBDIR/${dbtype}${dbnuminfo}/shutdownall" ]]; then
				if [[ "$DEBUG" == "" ]]; then
					check_consul
					if [[ $? == 0 ]]; then
					    check_vault
					    if [[ $? == 0 ]]; then
						dbstatus=$(/etc/init.d/sas-viya-sasdatasvrc-${dbname}-${dbtype}${dbnuminfo} status)
						if [[ $? == 0 ]]; then
							dbstatus=$(echo "$dbstatus" | grep 'is running')
							if [[ "$dbstatus" != "" ]]; then
								su - sas -c "$DBDIR/${dbtype}${dbnuminfo}/shutdownall"
								if [[ $? != 0 ]]; then
									let "FAIL+=1"
									return
								fi
							fi
						else
							echo "ERROR: command error: sas-viya-sasdatasvrc-${dbname}-${dbtype}${dbnuminfo} status"
							exit 1
						fi
					    else
						echo "ERROR: vault service is not running or not ready"
					    fi
					else
						echo "Warning: consul is not up, skip shutdown database $dbtype"
						exit 0
					fi	
				fi
			fi
		else
			echo "ERROR: unsupported dbtype in stopdb: ($dbtype)"
			exit 1
		fi
	else
		if [[ -f "sas-viya-sasdatasvrc-${dbname}" ]]; then
			LIST="
			sas-viya-sasdatasvrc-${dbname}
			sas-viya-sasdatasvrc-${dbname}-pgpool0-ct-pool_hba
			sas-viya-sasdatasvrc-${dbname}-pgpool0-ct-pgpool
			sas-viya-sasdatasvrc-${dbname}-pgpool0-ct-pcp
			"
		fi
	fi

	do_ps_common stop "$LIST"
}

check_dbps()
{
	LIST=$*
	local skip
	for f in "$LIST"
	do
		skip=0
		if [[ -f "$PIDROOT/$f.pid" ]]; then
			p=$(cat $PIDROOT/$f.pid)
			ps -p $p > /dev/null 2>&1
			if [[ $? == 0 ]]; then
				skip=1
			fi
		fi
		if [[ "$skip" != "1" ]]; then
			rc=$(do_service stop $f)
			if [[ "$rc" != "0" ]]; then
				wait $rc
			fi
		fi
	done
}

do_startdbct()
{
	local LIST
	if [[ "$viya35" == "1" ]]; then
		dbtype=$dbarg2
		LIST1=$(find . -name "sas-viya-sasdatasvrc-${dbname}-${dbtype}*-consul-template-operation_node"| cut -c3-|sort)
		LIST2=$(find . -name "sas-viya-sasdatasvrc-${dbname}-${dbtype}*-consul-template-*_hba"| cut -c3-|sort)
		LIST="$LIST1 $LIST2"
		check_dbps "$LIST"
		do_ps_common start "$LIST"
		if [[ "$dbtype" == "node" ]]; then
		    get_dbnuminfo node
		    if [[ -x "$DBDIR/node${dbnuminfo}/startall" ]]; then
			if [[ "$DEBUG" == "" ]]; then
				check_consul
				if [[ $? == 0 ]]; then
					dbstatus=$(/etc/init.d/sas-viya-sasdatasvrc-${dbname}-node${dbnuminfo} status)
					if [[ $? == 0 ]]; then
						dbstatus=$(echo "$dbstatus"|grep 'is running')
						if [[ "$dbstatus" == "" ]]; then
							su - sas -c "$DBDIR/node${dbnuminfo}/startall"
							if [[ $? != 0 ]]; then
								#retry: work around consul template issue
								echo "info: startdb retry node${dbnuminfo}"
								su - sas -c "$DBDIR/node${dbnuminfo}/startall"
								if [[ $? != 0 ]]; then
									let "FAIL+=1"
								fi
							fi
						fi
					else
						echo "ERROR: command error: sas-viya-sasdatasvrc-${dbname}-node${dbnuminfo} status"
						exit 1
					fi
				else
					echo "ERROR: consul has issue, need to be fixed before starting nodes"
					exit 1
				fi
			fi
		    else
			echo "ERROR: postgres install issue, file not found: $DBDIR/node${dbnuminfo}/startall"
			exit 1
		    fi
		fi
	else
		LIST=$(find . -name "sas-viya-sasdatasvrc-${dbname}-node*-ct-*"| cut -c3-)
		do_ps_common start "$LIST"
	fi

}

do_stopdbct()
{
	local LIST
	LIST=
	if [[ "$viya35" == "1" ]]; then
		dbtype=$dbarg2
		check_vault
		if [[ $? == 0 ]]; then
		    for dbtype in pgpool node
		    do
			LIST1=$(find . -name "sas-viya-sasdatasvrc-${dbname}-${dbtype}[[:digit:]]*-consul-template-operation_node"| cut -c3-|sort)
			LIST2=$(find . -name "sas-viya-sasdatasvrc-${dbname}-${dbtype}[[:digit:]]*-consul-template-*_hba"| cut -c3-|sort)
			LIST="$LIST2 $LIST1 $LIST"
		    done
		else
		    echo "Warning: vault service is not running or not ready"
		fi
	else
		LIST=$(find . -name "sas-viya-sasdatasvrc-${dbname}-node*-ct-*"| cut -c 3-)
	fi
	do_ps_common stop "$LIST"
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

clean_dbps()
{
	local LIST=$(ps -e -o "user pid ppid cmd"|\
		grep -E 'sds_consul_health_check|sas-crypto-management|sds_load_config_service_kv_definition|sas-configuration-cli'|\
		grep -v grep |awk 'BEGIN{OFS=" "} { print $1, $2, $4, $5}')
	do_cleanps "$LIST"
}

get_dbnuminfo()
{
	local dbtype=$1
	cd "$DBDIR"
	dbnuminfo=$(ls -d ${dbtype}* |sed -e "s/$dbtype//" |sort -n|head -1)
	if [[ "$dbnuminfo" == "" ]]; then
		echo "ERROR: postgres install issue in $DBDIR can't get corresponding $dbype number"
		exit 1
	fi
}
do_cleanps()
{
	local flag
	local NLIST
	local LIST=$*

	if [[ "$LIST" == "" ]]; then
		return 0
	fi

	if [[ "$1" == "-s" ]]; then
		flag=$1
		shift
		LIST=$*
		NLIST=$(echo "$LIST"|awk '{printf "%s ",$2}')
	elif [[ "$1" == "-p" ]]; then
		shift
		NLIST=$*
	else
		NLIST=$(echo "$LIST"|awk '{printf "%s ",$2}')
	fi

	if [[ "$NLIST" == "" ]]; then
		return 0
	fi

	for p in $NLIST
	do
		ps -p $p > /dev/null
		if [[ $? == 0 ]]; then
			pkill -P $p 2>/dev/null
			kill -KILL $p 2>/dev/null
		fi
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
		if [[ "$HURL" == "" ]]; then
			HURL="http"
		fi
		cat $FILE|grep 'ProxyPass '|egrep -e "/SAS|/ModelStudio"|awk "{print \$2}"|sort|uniq|sed "s/^/${HURL}:\/\/"$host"/"
	fi
	return 0
}

initdb()
{
	ls sas-viya-sasdatasvrc-*consul-template-operation_node > /dev/null 2>&1
	if [[ $? == 0 ]]; then
		viya35=1
		DBDIR=/opt/sas/viya/config/data/sasdatasvrc/$dbname
	else
		viya35=
	fi
}

check_vault()
{
	local CONF=/opt/sas/viya/config/consul.conf
	source $CONF
	local info=$(/opt/sas/viya/home/bin/consul catalog services 2>&1)
	local rc=$?
	if [[ $rc == 0 ]]; then
		echo "$info"| grep "^vault$" > /dev/null
		return $?
	else
		echo "$info"
		return $rc
	fi
}

check_consul()
{
	local CMD=/etc/init.d/sas-viya-consul-default
	if [[ ! -x "$CMD" ]]; then
		echo "ERROR: command not found: $CMD"
		exit 2
	fi

	$CMD status|grep -q 'is dead' 
	if [[ $? == 0 ]]; then
		return 255
	fi
	
	local CONF=/opt/sas/viya/config/consul.conf
	if [[ ! -f "$CONF" ]]; then
		echo "ERROR: consul config file is missing ($CONF)"
		exit 1
	fi

	source $CONF
	local info
	info=$(/opt/sas/viya/home/bin/consul members 2>&1)
	rc=$?
	if [[ $rc != 0 ]]; then
		#retry: work around with consul bug
		do_ps_common stop sas-viya-consul-default
		do_ps_common start sas-viya-consul-default
		sleep 1
		info=$(/opt/sas/viya/home/bin/consul members)
		rc=$?
		if [[ $rc != 0 ]]; then
			echo "ERROR: consul may have a slow start, please rerun the playbook. If the problem is persisted, please check the consul log."
			exit $rc
			#return $rc
		fi
	fi

	local cnt
	cnt=$(echo "$info"| grep -v -E 'Status|alive'|wc -l)
	if [[ $cnt != 0 ]]; then
		echo "$info"
		echo "ERROR: consul is not healthy, please check consul log."
		exit $cnt
		#return $cnt 
	fi

	/opt/sas/viya/home/bin/sas-csq list-services | grep -q $dbname
	rc=$?
	if [[ $rc != 0 ]]; then
		echo "ERROR: consul has error, database $dbname service is missing: $rc"
		exit $rc
		#return $rc
	fi
}

do_deregconsul()
{
	SNAME=sas-viya-consul-default
	if [[ ! -x "/etc/init.d/$SNAME" ]]; then
                echo "Warning: service $SNAME not found"
		return
	fi

	local rc=$(/etc/init.d/$SNAME status|grep 'is running')
	if [[ "$rc" != "0" ]]; then
                echo "deregconsul: $rc"
		return
	fi

        local CONF=/opt/sas/viya/config/consul.conf
        if [[ ! -f "$CONF" ]]; then
                echo "Warning: consul config file is missing ($CONF)"
                return
        fi
        source $CONF
        export CONSUL_HTTP_TOKEN=$($SUDO cat /opt/sas/viya/config/etc/SASSecurityCertificateFramework/tokens/consul/default/client.token)

        local BT=/opt/sas/viya/home/bin/sas-bootstrap-config

	local i=0
	while true;
	do
		local idlist=$($BT agent service list 2>&1)
		echo "$idlist" | grep 'ERROR: Unable to retrieve' > /dev/null 2>&1
		if [[ $? != 0 ]]; then
			idlist=$(echo "$idlist"|grep '"ID":'|grep -v -E 'postgres-'|awk '{print $2}'|sed -e 's/["|,| ]//g')
			echo "info: consul deregister: idlist ($idlist)"
			for id in $idlist
			do
				$BT agent service deregister $id
			done
			break
		else
			if [[ $i > $consul_retry_counter ]]; then
				break
			fi
		fi
		((i=i+1))
	done

	rc=$(do_service stop $SNAME)
	if [[ "$rc" != "0" ]]; then
		wait $rc
	fi

	local LIST=$(ps -e -o "user pid ppid cmd"|grep -E '/opt/sas/spre/|/opt/sas/viya/'| \
		grep -E 'sds_consul_health_check|sas-crypto-management|kill_consul_helper|sas-bootstrap-config'|grep -v grep)
	do_cleanps -s "$LIST"
}

check_svcignore()
{
	local key=$1
	if [[ "$IGNORE" =~ "$key" ]]; then
		return 1
	else
		return 0
	fi
}

init()
{
	SYSTYPE=$(ps -p 1|grep -v PID|awk '{print $4}')
	DEBUG=
	LIST=
	cd /etc/init.d
	PIDROOT=/var/run/sas

	IGNORE=
	local SVCFILE=/opt/sas/viya/config/etc/viya-svc-mgr/svc-ignore
	if [[ -f "$SVCFILE" ]]; then
		IGNORE=$(sed -e 's/#.*$//' -e '/^$/d' $SVCFILE)
	fi
}
######
# main
######
OPT=$1
init

case "$OPT" in
	deregconsul)
		consul_retry_counter=$2
		do_$OPT ;;
	stopms|stopmt|startmt|startcas|stopcas|svastatus)
		FAIL=0; do_$OPT; exit $FAIL ;;
	startdbct|startdb|stopdb|stopdbct)
		shift 1
		dbname=$1
		dbarg2=$2
		dbarg3=$3
		initdb
		FAIL=0; do_$OPT; exit $FAIL ;;
	checkdb)
		shift 1
		dbname=$1
		dbnum=$2
		initdb
		do_$OPT; exit $? ;;
	start|stop)
		shift 1
		consul_retry_counter=0
		if [[ "$OPT" == "stop" && "$1" == "sas-viya-consul-default" ]]; then
			consul_retry_counter=$2
			TLIST=sas-viya-consul-default
		else
			TLIST=$*
		fi
		LIST=
		for l in $TLIST
		do
			if [[ -x "/etc/init.d/$l" ]]; then
				LIST="$l $LIST"
			else
				echo "ERROR: command not found: $l"
				exit 1
			fi
		done

		do_ps_common $OPT "$LIST"

		if [[ $consul_retry_counter > 0 ]]; then
			do_deregconsul
			if [[ -d /var/run/sas ]]; then
				PLIST=
				SLIST=
				cd /var/run/sas
				FILES=$(ls sas*.pid|grep -v sas-viya-all-services)
				for f in $FILES
				do
					p=$(cat $f)
					ps -p $p >/dev/null 2>&1
					if [[ $? == 0 ]]; then
						PLIST="$PLIST $p"
						pname=$(echo "$f" | sed 's/.pid//')
						SLIST="$SLIST $pname"
					fi
				done
				do_ps_common stop "$SLIST"
				do_cleanps -p "$PLIST"
				/bin/rm -f "$FILES"
			fi
			clean_dbps
		fi
		;;
	cleanps)
		shift 1
		DLIST=$*
		LIST=$(echo "$DLIST" | sed -e "{ s/[][]//g ; s/\,/\n/g ; s/'//g }" | awk '{print $1 " " $2}')
		do_cleanps "$LIST"
		;;
	cleancomp)
		LIST=$(ps -e -o "user pid ppid cmd"|grep -E '/opt/sas/spre/|/opt/sas/viya/'|grep -v grep |\
			awk 'BEGIN{OFS=" "} { print $1, $2, $4, $5}'| grep -E 'launcher|compsrv')
		do_cleanps "$LIST"
		;;
	checkspace)
		DIR=$2; SIZE=$3
		$OPT; exit $? ;;
	geturls)
		HURL=$2
		do_$OPT
		;;
	checkps)
		shift 1
		CNT=$*
		if [[ $CNT -eq 0 ]]; then
			info=$(ps -ef|grep -E '/opt/sas/spre/|/opt/sas/viya/|pgpool|postgres'|grep -v grep|awk '{print}')
		        echo "$info"
		else
			info=$(ps -ef|grep -E '/opt/sas/spre/|/opt/sas/viya/|pgpool|postgres'|grep -v grep)
			if [[ "$info" == "" ]]; then
				exit 0
			fi
			total=$(echo "$info"|wc -l)
			if [[ $CNT -ne 1 && $total -gt $CNT ]]; then
				echo "Partial of the processes listed: $CNT/$total"
			fi
			echo "$info" | tail -$CNT
		fi
		exit 0
		;;
	*)
		do_usage; exit 1 ;;
esac
