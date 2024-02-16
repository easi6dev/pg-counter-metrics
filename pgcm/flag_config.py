import os

check_active_replication_slot = os.getenv("CHECK_ACTIVE_REPLICATION_SLOT", False)
check_active_sessions = os.getenv("CHECK_ACTIVE_SESSIONS", False) 
check_autoanalyze_count_per_day = os.getenv("check_autoanalyze_count_per_day", False) 
check_autoanalyze_count_per_hour = os.getenv("CHECK_AUTOANALYZE_COUNT_PER_HOUR", False)
check_autoanalyze_count_per_min = os.getenv("CHECK_AUTOANALYZE_COUNT_PER_MIN", False)
check_autovacuum_count_per_day = os.getenv("CHECK_AUTOVACUUM_COUNT_PER_DAY", False)
check_autovacuum_count_per_hour = os.getenv("CHECK_AUTOVACUUM_COUNT_PER_HOUR", False)
check_autovacuum_count_per_min = os.getenv("CHECK_AUTOVACUUM_COUNT_PER_MIN", False)
check_autovacuum_freeze_max_age = os.getenv("CHECK_AUTOVACUUM_FREEZE_MAX_AGE", False)
check_autovacuum_multixact_freeze_max_age = os.getenv("CHECK_AUTOVACUUM_MULTIXACT_FREEZE_MAX_AGE", False)
check_blocked_sessions = os.getenv("CHECK_BLOCKED_SESSIONS", False)
check_checkpoints_requested = os.getenv("CHECK_CHECKPOINTS_REQUESTED", False)
check_checkpoints_timed = os.getenv("CHECK_CHECKPOINTS_TIMED", False)
check_connections_utilization = os.getenv("CHECK_CONNECTIONS_UTILIZATION", False)
check_count_replication_slots = os.getenv("CHECK_COUNT_REPLICATION_SLOTS", False)
check_deadlocks = os.getenv("CHECK_DEADLOCKS", False)
check_idle_in_transaction_aborted_sessions = os.getenv("CHECK_IDLE_IN_TRANSACTION_ABORTED_SESSIONS", False)
check_idle_in_transaction_sessions = os.getenv("CHECK_IDLE_IN_TRANSACTION_SESSIONS", False)
check_idle_sessions = os.getenv("CHECK_IDLE_SESSIONS", False)
check_inactive_replication_slot = os.getenv("CHECK_INACTIVE_REPLICATION_SLOT", False)
check_invalid_indexes = os.getenv("CHECK_INVALID_INDEXES", False)
check_lock_mode = os.getenv("CHECK_LOCK_MODE", False)
check_lock_type = os.getenv("CHECK_LOCK_TYPE", False)
check_max_connections = os.getenv("CHECK_MAX_CONNECTIONS", False)
check_n_tables_eligible_for_autovacuum = os.getenv("CHECK_N_TABLES_ELIGIBLE_FOR_AUTOVACUUM", False)
check_not_granted_lock = os.getenv("CHECK_NOT_GRANTED_LOCK", False)
check_oldest_open_idl_in_transaction = os.getenv("CHECK_OLDEST_OPEN_IDL_IN_TRANSACTION", False)
check_oldest_open_transaction = os.getenv("CHECK_OLDEST_OPEN_TRANSACTION", False)
check_oldest_replication_slot_lag_gb_behind = os.getenv("CHECK_OLDEST_REPLICATION_SLOT_LAG_GB_BEHIND", False)
check_oldest_replication_slot_lag_gb_behind_per_slot = os.getenv("CHECK_OLDEST_REPLICATION_SLOT_LAG_GB_BEHIND_PER_SLOT", False)
check_oldest_xid = os.getenv("CHECK_OLDEST_XID", False)
check_percent_towards_emergency_autovacuum = os.getenv("CHECK_PERCENT_TOWARDS_EMERGENCY_AUTOVACUUM", False)
check_percent_towards_wraparound = os.getenv("CHECK_PERCENT_TOWARDS_WRAPAROUND", False)
check_queries_canceled_due_to_lock_deadlocks = os.getenv("CHECK_QUERIES_CANCELED_DUE_TO_LOCK_DEADLOCKS", False)
check_queries_canceled_due_to_lock_timeouts = os.getenv("CHECK_QUERIES_CANCELED_DUE_TO_LOCK_TIMEOUTS", False)
check_result_table_stat_n_mod_since_analyze = os.getenv("CHECK_RESULT_TABLE_STAT_N_MOD_SINCE_ANALYZE", False)
check_ride_entity_index_stat = os.getenv("CHECK_RIDE_ENTITY_INDEX_STAT", False)
check_stat_tup_del_pct = os.getenv("CHECK_STAT_TUP_DEL_PCT", False)
check_stat_tup_upd_pct = os.getenv("CHECK_STAT_TUP_UPD_PCT", False)
check_table_stat_autoanalyze_count = os.getenv("CHECK_TABLE_STAT_AUTOANALYZE_COUNT", False)
check_table_stat_autovacuum_count = os.getenv("CHECK_TABLE_STAT_AUTOVACUUM_COUNT", False)
check_table_stat_dead_tup_percent = os.getenv("CHECK_TABLE_STAT_DEAD_TUP_PERCENT", False)
check_table_stat_idx_tup_fetch = os.getenv("CHECK_TABLE_STAT_IDX_TUP_FETCH", False)
check_table_stat_n_dead_tup = os.getenv("CHECK_TABLE_STAT_N_DEAD_TUP", False)
check_table_stat_n_live_tup = os.getenv("CHECK_TABLE_STAT_N_LIVE_TUP", False)
check_table_stat_n_tup_del = os.getenv("CHECK_TABLE_STAT_N_TUP_DEL", False)
check_table_stat_n_tup_hot_upd = os.getenv("CHECK_TABLE_STAT_N_TUP_HOT_UPD", False)
check_table_stat_n_tup_ins = os.getenv("CHECK_TABLE_STAT_N_TUP_INS", False)
check_table_stat_n_tup_upd = os.getenv("CHECK_TABLE_STAT_N_TUP_UPD", False)
check_table_stat_seq_tup_read = os.getenv("CHECK_TABLE_STAT_SEQ_TUP_READ", False)
check_table_stat_total_fts_scan = os.getenv("CHECK_TABLE_STAT_TOTAL_FTS_SCAN", False)
check_table_stat_total_idx_scan = os.getenv("CHECK_TABLE_STAT_TOTAL_IDX_SCAN", False)
check_table_stat_tup_ins_pct = os.getenv("CHECK_TABLE_STAT_TUP_INS_PCT", False)
check_total_connections = os.getenv("CHECK_TOTAL_CONNECTIONS", False)
check_total_db_size_in_gb = os.getenv("CHECK_TOTAL_DB_SIZE_IN_GB", False)
check_tup_deleted = os.getenv("CHECK_TUP_DELETED", False)
check_tup_fetched = os.getenv("CHECK_TUP_FETCHED", False)
check_tup_inserted = os.getenv("CHECK_TUP_INSERTED", False)
check_tup_returned = os.getenv("CHECK_TUP_RETURNED", False)
check_tup_updated = os.getenv("CHECK_TUP_UPDATED", False)
check_wait_event = os.getenv("CHECK_WAIT_EVENT", False)
check_xact_commit = os.getenv("CHECK_XACT_COMMIT", False)
check_xact_commit_ratio = os.getenv("CHECK_XACT_COMMIT_RATIO", False)
check_xact_rollback = os.getenv("CHECK_XACT_ROLLBACK", False)