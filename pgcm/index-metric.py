import sys
import logging
import pg8000
import boto3
import rds_config
import json
import tables_config
import ssl
import os


#rds settings
rds_host  = rds_config.rds_host
name = 'postgreadmin'#rds_config.db_username
db_name = "tada_ride_service" #rds_config.db_name
region = rds_config.db_region
port = rds_config.db_port
auth_type = rds_config.auth_type
secret_name = rds_config.db_secret_name
username_password = 'xmcHh9b.rBR3ZkX' #rds_config.username_password
metric_name=rds_config.metric_name

schema_list = tables_config.schema_list

sslctx = None

query_index_stat = """SELECT current_database(), nspname AS schemaname, tblname, idxname, bs*(relpages)::bigint AS real_size,
  bs*(relpages-est_pages)::bigint AS extra_size,
  round((100 * (relpages-est_pages)::float / relpages)::numeric, 2) AS extra_pct,
  fillfactor,
  CASE WHEN relpages > est_pages_ff
    THEN bs*(relpages-est_pages_ff)
    ELSE 0
  END AS bloat_size,
  round((100 * (relpages-est_pages_ff)::float / relpages)::numeric, 2) AS bloat_pct,
  is_na
FROM (
  SELECT coalesce(1 +
         ceil(reltuples/floor((bs-pageopqdata-pagehdr)/(4+nulldatahdrwidth)::float)), 0
      ) AS est_pages,
      coalesce(1 +
         ceil(reltuples/floor((bs-pageopqdata-pagehdr)*fillfactor/(100*(4+nulldatahdrwidth)::float))), 0
      ) AS est_pages_ff,
      bs, nspname, tblname, idxname, relpages, fillfactor, is_na
  FROM (
      SELECT maxalign, bs, nspname, tblname, idxname, reltuples, relpages, idxoid, fillfactor,
            ( index_tuple_hdr_bm +
                maxalign - CASE
                  WHEN index_tuple_hdr_bm %% maxalign = 0 THEN maxalign
                  ELSE index_tuple_hdr_bm %% maxalign
                END
              + nulldatawidth + maxalign - CASE
                  WHEN nulldatawidth = 0 THEN 0
                  WHEN nulldatawidth::integer %% maxalign = 0 THEN maxalign
                  ELSE nulldatawidth::integer %% maxalign
                END
            )::numeric AS nulldatahdrwidth, pagehdr, pageopqdata, is_na
      FROM (
          SELECT n.nspname, i.tblname, i.idxname, i.reltuples, i.relpages,
              i.idxoid, i.fillfactor, current_setting('block_size')::numeric AS bs,
              CASE
                WHEN version() ~ 'mingw32' OR version() ~ '64-bit|x86_64|ppc64|ia64|amd64' THEN 8
                ELSE 4
              END AS maxalign,
              24 AS pagehdr,
              16 AS pageopqdata,
              CASE WHEN max(coalesce(s.null_frac,0)) = 0
                  THEN 2
                  ELSE 2 + (( 32 + 8 - 1 ) / 8)
              END AS index_tuple_hdr_bm,
              sum( (1-coalesce(s.null_frac, 0)) * coalesce(s.avg_width, 1024)) AS nulldatawidth,
              max( CASE WHEN i.atttypid = 'pg_catalog.name'::regtype THEN 1 ELSE 0 END ) > 0 AS is_na
          FROM (
              SELECT ct.relname AS tblname, ct.relnamespace, ic.idxname, ic.attpos, ic.indkey, ic.indkey[ic.attpos], ic.reltuples, ic.relpages, ic.tbloid, ic.idxoid, ic.fillfactor,
                  coalesce(a1.attnum, a2.attnum) AS attnum, coalesce(a1.attname, a2.attname) AS attname, coalesce(a1.atttypid, a2.atttypid) AS atttypid,
                  CASE WHEN a1.attnum IS NULL
                  THEN ic.idxname
                  ELSE ct.relname
                  END AS attrelname
              FROM (
                  SELECT idxname, reltuples, relpages, tbloid, idxoid, fillfactor, indkey,
                      pg_catalog.generate_series(1,indnatts) AS attpos
                  FROM (
                      SELECT ci.relname AS idxname, ci.reltuples, ci.relpages, i.indrelid AS tbloid,
                          i.indexrelid AS idxoid,
                          coalesce(substring(
                              array_to_string(ci.reloptions, ' ')
                              from 'fillfactor=([0-9]+)')::smallint, 90) AS fillfactor,
                          i.indnatts,
                          pg_catalog.string_to_array(pg_catalog.textin(
                              pg_catalog.int2vectorout(i.indkey)),' ')::int[] AS indkey
                      FROM pg_catalog.pg_index i
                      JOIN pg_catalog.pg_class ci ON ci.oid = i.indexrelid
                      WHERE ci.relam=(SELECT oid FROM pg_am WHERE amname = 'btree')
                      AND ci.relpages > 0
                  ) AS idx_data
              ) AS ic
              JOIN pg_catalog.pg_class ct ON ct.oid = ic.tbloid
              LEFT JOIN pg_catalog.pg_attribute a1 ON
                  ic.indkey[ic.attpos] <> 0
                  AND a1.attrelid = ic.tbloid
                  AND a1.attnum = ic.indkey[ic.attpos]
              LEFT JOIN pg_catalog.pg_attribute a2 ON
                  ic.indkey[ic.attpos] = 0
                  AND a2.attrelid = ic.idxoid
                  AND a2.attnum = ic.attpos
            ) i
            JOIN pg_catalog.pg_namespace n ON n.oid = i.relnamespace
            JOIN pg_catalog.pg_stats s ON s.schemaname = n.nspname
                                      AND s.tablename = i.attrelname
                                      AND s.attname = i.attname
            GROUP BY 1,2,3,4,5,6,7,8,9,10,11
      ) AS rows_data_stats
  ) AS rows_hdr_pdg_stats
) AS relation_stats
where nspname in """ + schema_list + """
ORDER BY bloat_Size desc, nspname, tblname, idxname; """


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger_debug = logging.getLogger("pgcm")
logger_debug.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


def handler(event, context):
    logger.info( "Starting PG metric Process on " + rds_host)
    # logger.info( "Metric Dimension Name: "+ metric_dimension_name)
    logger.info( "Database: " + db_name)
    logger.info( "Database User Name: " + name)
    logger.info( "Database Port: " + str(port))
    logger.info( "schema list: " + schema_list)
    #logger.info( "tables list: " + tables_list)
    try:
        logger.info("-----------------------------")
        logger.info("Test the database connection")
        logger.info("-----------------------------")
        if auth_type == 'password':
            logger.info("Using clear password to connect to the DB")
            token = username_password
            logger_debug.debug("the password: " + token)
        elif auth_type == 'secret_manager':
            logger.info("Using the AWS secret manager to get the password")
            secretValues=json.loads(get_secret())
            token = secretValues['password']
            logger_debug.debug(secretValues)
            logger_debug.debug("the password: " + token)
        else:
            logger.info("Using the IAM DB authentication to create an authentication token")
            client = boto3.client("rds",region_name=region)
            token = client.generate_db_auth_token(rds_host,port, name)
            logger_debug.debug("the password is " + token)
        conn = pg8000.dbapi.connect(database=db_name, host=rds_host, user=name, password=token, port=port, ssl_context=sslctx, timeout=10)
    except (Exception) as error:
        logger.error(error)
        putErrorMetric()
        return None
    logger.info("SUCCESS: Connection to RDS postgres instance succeeded")
    try:
        logger.info("------------------------------")
        logger.info("Sarting the queries execution")
        logger.info("------------------------------")

        logger_debug.debug("Executing result_index_stat")
        result_index_stat = executeSQL(conn, query_index_stat)
        logger.info(result_index_stat)

        # Create CloudWatch client
        logger.info("-------------------------------------")
        logger.info("starting  cloudwatch.put_metric_data")
        logger.info("-------------------------------------")
        cloudwatch = boto3.client('cloudwatch')

        for row in result_index_stat :
            tblname = row[2]
            idxname = row[3]
            real_size = row[4]
            extra_size = row[5]
            extra_pct = row[6]
            bloat_size = row[8]
            bloat_pct = row[9]

            logger.info("tblname:" + tblname + ", idxname:"+idxname+", real_size:"+str(real_size)+", extra_size:"+str(extra_size)+", extra_pct:"+str(extra_pct)+", bloat_size:"+str(bloat_size)+", bloat_pct:"+str(bloat_pct));

            # Put Counter custom metrics
            cloudwatch.put_metric_data(
                MetricData=[
                    {
                        'MetricName': 'index_stat_real_size',
                        'Dimensions': [
                            {
                                'Name': 'DBInstanceIdentifier',
                                'Value': rds_config.metric_name
                            },
                            {
                                'Name': 'TableName',
                                'Value': tblname
                            },
                            {
                                'Name': 'IndexName',
                                'Value': idxname
                            },
                        ],
                        'Unit': 'Bytes',
                        'Value': real_size
                    },
                ],
                Namespace='PG Counter Metrics'
            )

            cloudwatch.put_metric_data(
                MetricData=[
                    {
                        'MetricName': 'index_stat_extra_size',
                        'Dimensions': [
                            {
                                'Name': 'DBInstanceIdentifier',
                                'Value': rds_config.metric_name
                            },
                            {
                                'Name': 'TableName',
                                'Value': tblname
                            },
                            {
                                'Name': 'IndexName',
                                'Value': idxname
                            },
                        ],
                        'Unit': 'Bytes',
                        'Value': extra_size
                    },
                ],
                Namespace='PG Counter Metrics'
            )

            cloudwatch.put_metric_data(
                MetricData=[
                    {
                        'MetricName': 'index_stat_extra_pct',
                        'Dimensions': [
                            {
                                'Name': 'DBInstanceIdentifier',
                                'Value': rds_config.metric_name
                            },
                            {
                                'Name': 'TableName',
                                'Value': tblname
                            },
                            {
                                'Name': 'IndexName',
                                'Value': idxname
                            },
                        ],
                        'Unit': 'Percent',
                        'Value': extra_pct
                    },
                ],
                Namespace='PG Counter Metrics'
            )

            cloudwatch.put_metric_data(
                MetricData=[
                    {
                        'MetricName': 'index_stat_bloat_size',
                        'Dimensions': [
                            {
                                'Name': 'DBInstanceIdentifier',
                                'Value': rds_config.metric_name
                            },
                            {
                                'Name': 'TableName',
                                'Value': tblname
                            },
                            {
                                'Name': 'IndexName',
                                'Value': idxname
                            },
                        ],
                        'Unit': 'Bytes',
                        'Value': bloat_size
                    },
                ],
                Namespace='PG Counter Metrics'
            )

            cloudwatch.put_metric_data(
                MetricData=[
                    {
                        'MetricName': 'index_stat_bloat_pct',
                        'Dimensions': [
                            {
                                'Name': 'DBInstanceIdentifier',
                                'Value': rds_config.metric_name
                            },
                            {
                                'Name': 'TableName',
                                'Value': tblname
                            },
                            {
                                'Name': 'IndexName',
                                'Value': idxname
                            },
                        ],
                        'Unit': 'Percent',
                        'Value': bloat_pct
                    },
                ],
                Namespace='PG Counter Metrics'
            )

    except (Exception) as error:
        logger.error(error)
        putErrorMetric()
        return None
    finally:
        if conn is not None:
            conn.close()
    logger.info("SUCCESS: PG Counter Metrics")
    return "SUCCESS: PG Counter Metrics"

def executeSQL(connection, sqlString, bindHash={}, supress=False):
    """
    A wrapper for SQL execution, handling exceptions, and managing
    return values for non-select statements.
    The supress flag allows us to prevent chatty error logs for specific
    queries that we know may fail without us needing to worry about it.
    We still return False, though, so that we can detect the error.
    """
    isSelect = False
    if sqlString.upper().find("SELECT") == 0:
        isSelect = True

    success = True
    #statement_timeout in millisecond
    #It only applies to current session
    timeout = 10000;
    timeoutString = "SET statement_timeout = " + str(timeout)
    results = []
    try:
        cursor = connection.cursor()
        cursor.execute(timeoutString)
        cursor.execute(sqlString, bindHash)
        try:
            if isSelect:
                results = cursor.fetchall()
        except:
            results = None

    except (Exception) as error:
        logger.error("ERROR: Unexpected error: Could not submit request: " + sqlString)
        logger.error("ERROR Message: " + str(error))
        success = False
    finally:
        connection.commit()
        cursor.close()
    if not success:
        return False
    elif isSelect:
        return results
    else:
        return None

def putErrorMetric():
    # Create CloudWatch client
    cloudwatch = boto3.client('cloudwatch')
    # Put custom metrics
    cloudwatch.put_metric_data(
        MetricData=[
            {
                'MetricName': 'PG_Counter_Metrics_Error_Count',
                'Dimensions': [
                    {
                        'Name': 'DBInstanceIdentifier',
                        'Value': rds_config.metric_name
                    },
                ],
                'Unit': 'None',
                'Value': 1
            },
        ],
        Namespace='PG Counter Metrics'
    )


handler(None, None)
