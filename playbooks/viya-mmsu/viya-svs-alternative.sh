#!/bin/bash
#### viya-svs-alternative.sh                                    ####
####################################################################

TIME_START="$(date -u +%s)"

# Viariables initialization
DEBUG=$1
SYSTEM_TYPE=$(ps -p 1 | grep -v PID | awk '{ print $4 }')
COMMAND_TYPE="$2"
# SYSTEM_TYPE=sysV
if [[ "${SYSTEM_TYPE}" == "systemd" ]]; then
	COMMAND="nohup systemctl ${COMMAND_TYPE} SVC >/dev/null 2>&1 &"
else
	COMMAND="nohup service SVC ${COMMAND_TYPE} >/dev/null 2>&1 &"
fi
FILES_LIST=($(ls /etc/init.d/sas-viya* | awk -F '/' '{print $NF}' \
	| grep -vE "all-services|consul|vault|httpproxy|rabbitmq|sasdatasvrc|pgpoolc|cascontroller|cachelocator|cacheserver"))
FILES_TO_PROCESS=(${FILES_LIST[@]})
NUMBER_OF_PROCESS=0
if [ ${COMMAND_TYPE} == "start" ]; then
	NUMBER_OF_PROCESS_LIMIT=1
	SLEEP_TIME_PROCESSES=3
else
	NUMBER_OF_PROCESS_LIMIT=15
	SLEEP_TIME_PROCESSES=1
fi   
SLEEP_TIME_TEST_CPUS_USAGE=5
CPUS_USAGE_MAX=95

#
if [ ${DEBUG} == 1 ]; then 
	echo "Variables:"
	echo "   System type="${SYSTEM_TYPE}
	echo "   Command type="${COMMAND_TYPE}
	echo "   Command="${COMMAND}
	echo "   List of files="${FILES_LIST}
	echo "   Number of files="${#FILES_LIST[@]}
	echo "   List of files="${FILES_TO_PROCESS}
	echo "   Number of files="${#FILES_TO_PROCESS[@]}
	echo "   Number processes executed"=${NUMBER_OF_PROCESS}
	echo "   Max number of process to execute"=${NUMBER_OF_PROCESS_LIMIT}
	echo "   Max CPUs usage in %"=${CPUS_USAGE_MAX}
	echo "   Pause between process in seconds"=${SLEEP_TIME_PROCESSES}
	echo "   Pause between CPUs usage tests"=${SLEEP_TIME_TEST_CPUS_USAGE}
fi

# Execute startup/shutdown command
for ((i=0; i<${#FILES_TO_PROCESS[@]}; i++)); do
	if [ ${NUMBER_OF_PROCESS} == ${NUMBER_OF_PROCESS_LIMIT} ]; then
		NUMBER_OF_PROCESS=0
		sleep ${SLEEP_TIME_PROCESSES}
		if [ ${DEBUG} == 1 ]; then 
			echo "execute CPUs usage test (max load average: ${CPUS_USAGE_MAX})"
		fi
		DO_IT=1
		while [ ${DO_IT} == 1 ]; do
			CPUS_USAGE_CURRENT=`expr $(dstat --cpu --noheader 2 1 | tail -n 1 | cut -c1-3) + 0`
			if [ ${DEBUG} == 1 ]; then 
				echo "CPUS_USAGE_CURRENT=${CPUS_USAGE_CURRENT} (max=${CPUS_USAGE_MAX})"
			fi
			if [ ${CPUS_USAGE_CURRENT} -gt ${CPUS_USAGE_MAX} ]; then
				if [ ${DEBUG} == 1 ]; then 
					echo "Sleep for ${SLEEP_TIME_TEST_CPUS_USAGE} seconds"
				fi
				sleep ${SLEEP_TIME_TEST_CPUS_USAGE}
			else
				DO_IT=0
			fi
		done
	fi
	echo "execute command ${COMMAND_TYPE} for: ${i} ${NUMBER_OF_PROCESS} ${FILES_TO_PROCESS[$i]}: $(echo ${COMMAND} \
		| sed 's/SVC/'${FILES_TO_PROCESS[$i]}'/g')"
	$(echo ${COMMAND} | sed 's/SVC/'${FILES_TO_PROCESS[$i]}'/g')
	NUMBER_OF_PROCESS=$(expr ${NUMBER_OF_PROCESS} + 1)
	SERVICES_PROCESSED[i]=`echo ${FILES_TO_PROCESS[$i]}`
done

TIME_END="$(date -u +%s)"
TIME_ELAPSED="$((${TIME_END}-${TIME_START}))"
echo "Total of ${TIME_ELAPSED} seconds elapsed for process"
