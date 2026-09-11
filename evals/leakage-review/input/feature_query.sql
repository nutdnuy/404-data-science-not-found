SELECT s.customer_id, s.snapshot_at,
       s.sessions_last_7d,
       CASE WHEN c.cancelled_at BETWEEN s.snapshot_at AND s.snapshot_at + INTERVAL '30 days'
            THEN 1 ELSE 0 END AS cancelled_next_30d,
       c.cancellation_reason,
       s.tenure_days
FROM weekly_snapshots s
LEFT JOIN cancellations c USING (customer_id);
