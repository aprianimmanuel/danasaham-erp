SELECT
    users.user_id "user_id",
    personal.name AS "personal_name",
    users.created_date AS "initial_registration_date",
    personal_legal.created_date AS "personal_legal_created_date",
    personal_finance.created_date AS "personal_finance_created_date",
    personal_ksei_id.created_date AS "personal_ksei_id_created_date",
    personal_limit.last_modified_date AS "personal_limit_last_modified_date",
    personal_data_checking.application_end_date AS "personal_data_checking_application_end_date",
    initial_primary_order.transaction_date AS "initial_primary_investment"
FROM
    users
INNER JOIN personal ON users.user_id = personal.user_id
LEFT JOIN personal_legal ON personal.personal_id = personal_legal.personal_id
LEFT JOIN personal_finance ON personal.personal_id = personal_finance.personal_id
LEFT JOIN personal_ksei_id ON personal.personal_id = personal_ksei_id.personal_id
LEFT JOIN personal_limit ON personal.personal_id = personal_limit.personal_personal_id
LEFT JOIN (
    SELECT
        personal_id AS "personal_id",
        last_modified_date AS "application_end_date"
    FROM (
        SELECT
            personal.personal_id AS "personal_id",
            application_process.last_modified_date AS "last_modified_date",
            ROW_NUMBER() OVER (PARTITION BY personal.personal_id ORDER BY application_process.last_modified_date DESC) AS row_num
        FROM
            personal
        INNER JOIN users ON personal.user_id = users.user_id
        LEFT JOIN application ON users.user_id = application.initiator_user_id
        LEFT JOIN application_process ON application.application_id = application_process.application_application_id
        WHERE
            application_process.process_workflow_workflow_id = '1'
            AND application_process.process_seq = '2'
    ) filtered
    WHERE
        filtered.row_num = 1
) personal_data_checking ON personal.personal_id = personal_data_checking.personal_id
LEFT JOIN (
    SELECT
        personal_id AS "personal_id",
        transaction_date AS "transaction_date"
    FROM (
        SELECT
            personal.personal_id AS "personal_id",
            transaction_detail.transaction_date "transaction_date",
            ROW_NUMBER() OVER (PARTITION BY personal.personal_id ORDER BY transaction_detail.transaction_date DESC) AS row_num
        FROM
            personal
        INNER JOIN users ON personal.user_id = users.user_id
        LEFT JOIN transaction_detail ON transaction_detail.user_id = users.user_id
        WHERE
            transaction_detail.transaction_type = 'BUY'
    ) filtered
    WHERE
        filtered.row_num = 1
) initial_primary_order ON personal.personal_id = initial_primary_order.personal_id
WHERE
    users.email NOT LIKE '%%+%%'
    AND users.email NOT LIKE '%%Test%%'
    AND personal.name NOT LIKE '%%Test%%'
    AND personal.name NOT LIKE '%%test%%'
    AND personal.name != 'asas'
    AND personal.name != 'masterdev'