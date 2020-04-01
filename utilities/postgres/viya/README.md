# SAS Viya Administration Resource Kit (SAS Viya ARK) - Connection Test Script

### NOTE: 
  - In Viya 3.5 **sds_micro_service_pg_connection_test.sh** is renamed to **monitor_pg_connection.sh** and it moved to sasdatasvrc RPM. 
  - Path and the file name is */opt/sas/viya/home/libexec/sasdatasvrc/script/maintenance/monitor_pg_connection.sh*
  - sds_micro_service_pg_connection_test.sh remains available here only for backwards compatibility with SAS Viya 3.4.
  - It should not be used from SAS Viya 3.5 or higher onwards.

## Introduction
SAS Viya ARK provides a utility that supports the deployment of the SAS Infrastructure Data Server component of SAS Viya. SAS Infrastructure Data Server is a PostgreSQL server that stores user data. 

This utility, a shell script named **sds_micro_service_pg_connection_test.sh**, gets a connection or session count per microservice for a given cluster in the SAS Viya environment. 

It also tests connectivity for PostgreSQL and pgpool hosts. 

Run this script after the SAS Viya deployment has completed.

You can run this script with the interval option to capture a snapshot of the number of connections. This data is helpful for identifying microservices that are using the minimum and maximum connections in the deployment.
You can also run this script to determine whether the PostgreSQL instance is running.
If you are having issues with the number of connections in your environment, you can run this script to see the number of connections by application.

For more information about SAS Infrastructure Data Server connections, see the SAS Viya documentation about tuning the server:
[SAS® Viya® 3.4 Administration: Tuning](https://go.documentation.sas.com/?cdcId=calcdc&cdcVersion=3.4&docsetId=caltuning&docsetTarget=p1af06ydz72zztn1be8ml24ilnr8.htm) .
  
## Prerequisites for Running the Shell Script
All SAS Viya 3.4 services must be up and running.

## Running the Script

To run the script, log on to the machine that is specified in the inventory file as the pgpool host as root or sudoer. Then switch to the 'sas' user.

### Usage
<pre>
./sds_micro_service_pg_connection_test.sh -s [ServiceName|ClusterName] -i [Number of iterations] -w [Wait time]
</pre>

### Options 
<pre>
s - ServiceName or ClusterName, for example, 'sds-ci' or 'postgres' - Optional parameter
i - Number of iterations,       for example, '10' or '25'           - Optional parameter
w - Wait time in seconds,       for example, '5' or '15'            - Optional parameter
</pre>

 ### Defaults
<pre>
 ClusterName is set to: All clusters that are defined in SAS Configuration Server (Consul)
 Number of iterations is set to: 1
 Wait time is set to: 5 seconds
</pre>

 ### Examples 
<pre>
./sds_micro_service_pg_connection_test.sh -s postgres -i 25 -w 10   -> One cluster  and 25 iterations, wait 10 seconds
./sds_micro_service_pg_connection_test.sh -s postgres               -> One cluster  and  1 iteration,  wait  5 seconds

./sds_micro_service_pg_connection_test.sh                           -> All clusters and  1 iteration,  wait  5 seconds
./sds_micro_service_pg_connection_test.sh -i 5 -w 15                -> All clusters and  5 iterations, wait 15 seconds
</pre>

Copyright (c) 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
SPDX-License-Identifier: Apache-2.0 

