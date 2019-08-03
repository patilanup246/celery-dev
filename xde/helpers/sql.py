DG_CLASSIFIED_PROFILE_COUNT = """
SELECT COUNT(1)
FROM
(
SELECT sns_id
FROM sns_account_enriched se
WHERE sns_name = :sns_name
AND sns_id IN 
(
SELECT follower_id
FROM sns_follower
WHERE sns_name = :sns_name
AND sns_id = :sns_id
LIMIT :follower_set_limit
)
AND se.birthyear IS NOT NULL 
AND se.gender IS NOT NULL
AND se.ethnicity IS NOT NULL
AND se.locations IS NOT NULL
LIMIT :prioritizing_threshold
) AS classsified;
"""

DG_CLASSIFIED_PROFILE_SNS_ID = """
SELECT sns_id
FROM
(
SELECT sns_id
FROM sns_account_enriched se
WHERE sns_name = :sns_name
AND sns_id IN 
(
SELECT follower_id
FROM sns_follower
WHERE sns_name = :sns_name
AND sns_id = :sns_id
LIMIT :follower_set_limit
)
AND se.birthyear IS NOT NULL 
AND se.gender IS NOT NULL
AND se.ethnicity IS NOT NULL
AND se.locations IS NOT NULL
LIMIT :prioritizing_threshold
) AS classsified;
"""

COLLECT_ENRICHED_PROFILES = """
SELECT *
FROM sns_account sa LEFT OUTER JOIN sns_account_enriched se USING(sns_id, sns_name) 
WHERE sa.sns_id IN :sns_ids AND sa.sns_name = :sns_name
;
"""


COLLECT_TS_POST_IN_WINDOW = """
SELECT *
FROM ts_72_hours
WHERE last_crawl_min = :last_crawl_min
ORDER BY last_crawl_sec
"""

COLLECT_COMMENT_BY_SNS_ID = """
WITH cm as (
SELECT {} FROM audience 
WHERE sns_name= :sns_name 
AND post_sns_id = :post_sns_id 
AND action=1
AND sns_id IS NOT NULL
AND sns_id > :sns_id
ORDER BY sns_id) 
SELECT * from cm LIMIT :limit  
"""

COLLECT_COMMENT_BY_POST_SNS_ID = """
WITH cm as (
SELECT {} FROM audience 
WHERE sns_name= :sns_name 
AND post_sns_id = :post_sns_id 
AND action=1
AND body IS NOT NULL
AND acted_at >= :acted_at
ORDER BY acted_at) 
SELECT * from cm LIMIT :limit
"""
