#!/bin/sh

####################################################################
#### sds_micro_service_pg_connection_test.sh                    ####
####################################################################


####################################################################
#### Author: SAS Institute Inc.                                 ####
####                                                            ####
####  Copyright (c) 2018,                                       ####
####  SAS Institute Inc., Cary, NC, USA, All Rights Reserved    ####
####                                                            ####
####################################################################
#
# Copyright (c) 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0 
#
####################################################################
#### Usage                                                      ####
####################################################################
# SAS DataServer utility script to test and get connection count#### 
# per micro service for a given cluster.                        ####
####################################################################


#-------------------------------------------------------------------------
# Functions
#-------------------------------------------------------------------------

usage() {
	echo
	echo "Usage:" 
	echo
	echo "  $0 -s [ServiceName|ClusterName] -i [No of iterations] -w [Wait time]"
	echo
	echo "Options:"
	echo "  s - ServiceName or ClusterName, for example, 'sds-ci' or 'postgres' - Optional parameter"
	echo "  i - No of iterations,           for example, '10' or '25'           - Optional parameter"
	echo "  w - Wait time in seconds,       for example, '5' or '15'            - Optional parameter"
	echo
	echo Defaults:
	echo "  ClusterName is set to       : All Clusters define in the Consul"
	echo "  No of iterations are set to : 1"
	echo "  Wait time is set to         : 5 seconds"
	echo
	echo Command examples:
	echo "  $0 -s postgres -i 25 -w 10   :-> One cluster  and 25 iterations, wait 10 seconds"
	echo "  $0 -s postgres               :-> One cluster  and  1 iteration , wait  5 seconds"
	echo "  $0                           :-> All clusters and  1 iteration , wait  5 seconds"
	echo "  $0 -i 5 -w 15                :-> All clusters and  5 iterations, wait 15 seconds"
	echo
	exit 0
}

f_db_conn_test() {
	echo
	echo INFO: Testing pgpool connection...
	$SASHOME/bin/psql -h $CLUSTER_POOL_PRIMARY_HOSTNAME -p $CLUSTER_POOL_PRIMARY_PORT -d postgres -c '\conninfo'
	echo
	echo INFO: Testing Postgres node connection...
	$SASHOME/bin/psql -h $CLUSTER_PG_PRIMARY_HOSTNAME -p $CLUSTER_PG_PRIMARY_PORT -d postgres -c '\conninfo'
}

f_pg_conn_ms_count() {

	# Check pgpool primary hostname
	export CLUSTER_POOL_PRIMARY_HOSTNAME=$($SASHOME/bin/sas-bootstrap-config $(echo $BOOTSTRAP_SWITCH) catalog service $SERVICE_NAME | egrep 'serviceAddress|serviceID|servicePort|"standby"|"primary"|pgpool:' | xargs -n4 -d'\n' | grep pgpool: | awk -F ',' '{print $1}' | awk -F '"' '{print $4}')
	if [ $? -ne 0 ]; then
		echo "ERROR: $SASHOME/bin/sas-bootstrap-config $(echo $BOOTSTRAP_SWITCH) catalog service $SERVICE_NAME failed" 1>&2
		return 1
	elif [ -z "$CLUSTER_POOL_PRIMARY_HOSTNAME" ]; then
		echo "ERROR: pgpool node was not found for the $SERVICE_NAME cluster in Consul service store" 1>&2
		echo "ERROR: Unable to set CLUSTER_POOL_PRIMARY_HOSTNAME variable" 1>&2
		return 1
	fi

	export CLUSTER_POOL_PRIMARY_PORT=$($SASHOME/bin/sas-bootstrap-config $(echo $BOOTSTRAP_SWITCH) catalog service $SERVICE_NAME | egrep 'serviceAddress|serviceID|servicePort|"standby"|"primary"|pgpool:' | xargs -n4 -d'\n'  | grep pgpool: | sort -V | awk -F ',' '{print $3}' | awk '{print $NF}')
	if [ $? -ne 0 ]; then
		echo "ERROR: $SASHOME/bin/sas-bootstrap-config $(echo $BOOTSTRAP_SWITCH) catalog service $SERVICE_NAME failed" 1>&2
		return 1
	elif [ -z "$CLUSTER_POOL_PRIMARY_PORT" ]; then
		echo "ERROR: pgpool node was not found for the $SERVICE_NAME cluster in Consul service store" 1>&2
		echo "ERROR: Unable to set CLUSTER_POOL_PRIMARY_PORT variable" 1>&2
		return 1
	fi

	# Check pg primary hostname
	export CLUSTER_PG_PRIMARY_HOSTNAME=$($SASHOME/bin/sas-bootstrap-config $(echo $BOOTSTRAP_SWITCH) catalog service $SERVICE_NAME | egrep 'serviceAddress|serviceID|servicePort|"standby"|"primary"|pgpool:' | xargs -n4 -d'\n' | grep -v pgpool: | grep '"primary"' | awk -F ',' '{print $1}' | awk -F '"' '{print $4}')
	if [ $? -ne 0 ]; then
		echo "ERROR: $SASHOME/bin/sas-bootstrap-config $(echo $BOOTSTRAP_SWITCH) catalog service $SERVICE_NAME failed" 1>&2
		return 1
	elif [ -z "$CLUSTER_PG_PRIMARY_HOSTNAME" ]; then
		echo "ERROR: pg primary hostname was not found for the $SERVICE_NAME cluster in Consul service store" 1>&2
		echo "ERROR: Unable to set CLUSTER_PG_PRIMARY_HOSTNAME variable" 1>&2
		return 1
	fi

	# Check pg primary port
	export CLUSTER_PG_PRIMARY_PORT=$($SASHOME/bin/sas-bootstrap-config $(echo $BOOTSTRAP_SWITCH) catalog service $SERVICE_NAME | egrep 'serviceAddress|serviceID|servicePort|"standby"|"primary"|pgpool:' | xargs -n4 -d'\n' | grep -v pgpool: | grep '"primary"' | awk -F ',' '{print $3}' | awk -F ': ' '{print $2}')
	if [ $? -ne 0 ]; then
		echo "ERROR: $SASHOME/bin/sas-bootstrap-config $(echo $BOOTSTRAP_SWITCH) catalog service $SERVICE_NAME failed" 1>&2
		return 1
	elif [ -z "$CLUSTER_PG_PRIMARY_PORT" ]; then
		echo "ERROR: pg primary port was not found for the $SERVICE_NAME cluster in Consul service store" 1>&2
		echo "ERROR: Unable to set CLUSTER_PG_PRIMARY_PORT variable" 1>&2
		return 1
	fi

	# Setting sas/INSTALL_USER
	export PGUSER=$($SASHOME/bin/sas-bootstrap-config     kv read --recurse config | grep $SERVICE_NAME | grep sr_check_user     | cut -d'=' -f 2);
	export PGPASSWORD=$($SASHOME/bin/sas-bootstrap-config kv read --recurse config | grep $SERVICE_NAME | grep sr_check_password | cut -d'=' -f 2);

	echo INFO: Testing database connection with db user sas...
	f_db_conn_test

	# Setting dbmsowner
	export PGUSER=$($SASHOME/bin/sas-bootstrap-config     kv read --recurse config/application/sas/database | grep $SERVICE_NAME | grep username | cut -d'=' -f 2);
	export PGPASSWORD=$($SASHOME/bin/sas-bootstrap-config kv read --recurse config/application/sas/database | grep $SERVICE_NAME | grep password | cut -d'=' -f 2);
	echo
	echo INFO: Testing db database with db user dbmsowner...
	f_db_conn_test
	
	echo
	echo INFO: Getting cluster connection count by Micro services per schema or database, total connections and db list...
	echo
	$SASHOME/bin/psql -h $CLUSTER_PG_PRIMARY_HOSTNAME -p $CLUSTER_PG_PRIMARY_PORT -d postgres <<EOF
		SELECT datname Database_Name, application_name, COUNT(*) Connection_Count FROM pg_stat_activity GROUP BY datname,application_name ORDER BY 1,3;
		SELECT datname Database_Name, SUM(conn_cnt) Total_Connections_By_Database FROM (SELECT datname, application_name, COUNT(*) conn_cnt FROM pg_stat_activity GROUP BY datname, application_name) AS s  GROUP BY datname;
		SELECT SUM(conn_cnt) Total_Connections FROM (SELECT datname, application_name, COUNT(*) conn_cnt FROM pg_stat_activity GROUP BY datname, application_name) AS s;
		\l+
EOF
	echo
	echo INFO: Checking the cluster status...

	# -----
	# Note: "echo q |" need on SUSE to avoid to quit status output otherwise one should manually quit i.e. typing "q" on keyboard.
	# -----

	if [ -f /etc/init.d/sas-viya-sasdatasvrc-${SERVICE_NAME} ]; then
		# Checking status locally 
		echo q | /etc/init.d/sas-viya-sasdatasvrc-${SERVICE_NAME} status
		echo
	else
		# Checking status remotely, if pgpool is on different machine.
		ssh -i $SSH_KEY_FILE -o StrictHostKeychecking=no -T $CLUSTER_POOL_PRIMARY_HOSTNAME "
			echo q | /etc/init.d/sas-viya-sasdatasvrc-${SERVICE_NAME} status
			echo
"

	fi
} # f_pg_conn_ms_count


#-------------------------------------------------------------------------
# Main Program
#-------------------------------------------------------------------------

# Read and set command line options
while getopts ":?h:s:w:i:" args; do
    case "${args}" in
	    s) export param_cluster_name=${OPTARG}
	       ;;
	    i) export param_no_of_interations=${OPTARG}
	       ;;
	    w) export param_wait_in_time_sec=${OPTARG}
	       ;;
	h|?|*) usage
	       ;;
    esac
done
shift $((OPTIND-1))

# Get sds_set_env_variable.sh and sds_env_var.sh file path dynamically.
export sas_viya_opt_path=/opt/sas

#------------------------------------------------------------------------------------------------
# Note: In "find -L 2>/dev/null" i.e. 2>/dev/null is needed to ignore "Permission denied" errors.
#------------------------------------------------------------------------------------------------

export sds_set_env_variable=$(find -L $sas_viya_opt_path 2>/dev/null -name sds_set_env_variable.sh | sort -u | head -n 1)
export sds_env_var=$(find -L $sas_viya_opt_path 2>/dev/null -name sds_env_var.sh | sort -u | head -n 1)

if [ -z "${sds_set_env_variable}" ] || [ -z "${sds_env_var}" ]; then
    echo ERROR: sds_set_env_variable:$sds_set_env_variable or sds_env_var:$sds_env_var is null. >&2
    exit 2
fi

if [ ! -f $sds_set_env_variable ]; then
    echo ERROR: $sds_set_env_variable script not found. >&2
    exit 2
fi

if [ ! -r $sds_env_var ]; then
    echo ERROR: $sds_env_var Config file not found. >&2
    echo
    exit 2
fi

# Set env vars.
eval source $sds_set_env_variable $sds_env_var > /dev/null
RETURN_CODE=$?
if [ $RETURN_CODE -ne 0 ]; then
    echo ERROR: source $sds_set_env_variable $sds_env_var failed. >&2
    exit $RETURN_CODE
fi

# User check
if [ $(whoami) != "$INSTALL_USER" ]
then
	echo
	echo "ERROR: The current user is '$(whoami)' and the script must be executed under '$INSTALL_USER' user."  >&2  # Do not log it to log file since it does not exist.
	echo
	exit 1
fi

# Set wait time to default, if user did not provide the input.
if [ -z "$param_wait_in_time_sec" ]; then
	param_wait_in_time_sec=0
fi

# Set no of iterations to default, if user did not provide the input.
if [ -z "$param_no_of_interations" ]; then
	param_no_of_interations=1
fi

echo param_cluster_name      : $param_cluster_name
echo param_wait_in_time_sec  : $param_wait_in_time_sec
echo param_no_of_interations : $param_no_of_interations

for i in $(seq 1 $param_no_of_interations);
do
	if [ -n "$param_cluster_name" ]; then
		# User provided cluster name
		export PSQL=$PGBIN/psql
		export SERVICE_NAME=$param_cluster_name
		echo
		echo "INFO: Start:----> $(date) :----> Cluster Name: $SERVICE_NAME"
		echo
		f_pg_conn_ms_count
		echo "INFO: Ends :----> $(date) :----> Cluster Name: $SERVICE_NAME"
		echo
	else
		# Create cluster or service name list from Consul KV store. 
		cluster_name_list=$(
			for env_dile_path in $($SASHOME/bin/sas-bootstrap-config kv read --recurse config/application/sas/database | egrep -v 'schema=|databaseServerName=|database=' )
			do
				basename $(dirname $env_dile_path)
			done | sort -u
		)

		for cluster_name in $(echo $cluster_name_list)
		do
			# Define log file
			export PSQL=$PGBIN/psql
			export SERVICE_NAME=$cluster_name
			echo
			echo "INFO: Start:----> $(date) :----> Cluster Name: $SERVICE_NAME"
			echo
			f_pg_conn_ms_count
			echo "INFO: Ends :----> $(date) :----> Cluster Name: $SERVICE_NAME"
			echo
		done
	fi

	if [ $i -lt $param_no_of_interations ]
	then
		echo INFO: Iteration $i done. Waiting for $param_wait_in_time_sec seconds...
		sleep $param_wait_in_time_sec
	else
		echo INFO: Iteration $i done.
		echo
	fi
done
