SELECT
    users.user_id "user_id",
    corporate.company_name AS "corporate_company_name",
    users.created_date AS "initial_registration_date",
    corporate_legal.created_date AS "corporate_legal_created_date",
    corporate_finance.created_date AS "corporate_finance_created_date",
    corporate_ksei_id.created_date AS "corporate_ksei_id_created_date",
    corporate_info_check.application_end_date AS "corporate_info_check_application_end_date",
    transaction_detail_modified.transaction_date AS "initial_primary_investment"
FROM
    users
INNER JOIN corporate ON users.user_id = corporate.user_id
LEFT JOIN corporate_legal ON corporate.corporate_id = corporate_legal.corporate_id
LEFT JOIN corporate_finance ON corporate.corporate_id = corporate_finance.corporate_id
LEFT JOIN corporate_ksei_id ON corporate.corporate_id = corporate_ksei_id.corporate_id
LEFT JOIN (
    SELECT
        corporate.corporate_id AS "corporate_id",
        application_process.last_modified_date AS "application_end_date",
        ROW_NUMBER() OVER (PARTITION BY corporate.corporate_id ORDER BY application_process.last_modified_date DESC) AS row_num
    FROM
        corporate
    INNER JOIN users ON corporate.user_id = users.user_id
    LEFT JOIN application ON users.user_id = application.initiator_user_id
    LEFT JOIN application_process ON application.application_id = application_process.application_application_id
    WHERE
        application_process.process_workflow_workflow_id = '2'
        AND application_process.process_seq = '2'
) corporate_info_check ON corporate.corporate_id = corporate_info_check.corporate_id
LEFT JOIN primary_order ON users.user_id = primary_order.user_id
LEFT JOIN transaction ON primary_order.primary_transaction_id = transaction.transaction_id
LEFT JOIN (
    SELECT
        transaction_detail.user_id AS "user_id",
        transaction_detail.transaction_date AS "transaction_date",
        ROW_NUMBER() OVER (PARTITION BY transaction_detail.user_id ORDER BY transaction_detail.transaction_date DESC) AS row_num
    FROM
        transaction_detail
    WHERE
        transaction_detail.transaction_type = 'BUY'
) transaction_detail_modified ON transaction_detail_modified.user_id = users.user_id
WHERE
    users.email NOT LIKE '%%+%%'
    AND users.email NOT LIKE '%%Test%%'
    AND corporate.company_name NOT LIKE '%%Test%%'