SELECT
    users.user_id "user_id",
    publisher.company_name AS "publisher_company_name",
    users.created_date AS "initial_registration_date",
    publisher.created_date AS "publisher_created_date",
    publisher_legal.created_date AS "publisher_legal_created_date",
    publisher_finance.created_date AS "publisher_finance_created_date",
    publisher_proposal.created_date AS "publisher_proposal_created_date",
    primary_product_registration.va_created_date AS "primary_va_registration_created_date",
    va_operational_approval.application_end_date AS "va_operational_approval",
    approval_registration_fee.application_end_date as "approval_registration_fee",
    primary_offering_input.application_end_date AS "primary_offering_input",
    confirmation_primary_offering.application_end_date AS "confirmation_primary_offering",
    cbestreporting.application_end_date AS "cbestreporting",
    investation_success_sk_upload.application_end_date AS "investation_success_sk_upload",
    investation_success_check.application_end_date AS "investation_success_check",
    investation_success_approval.application_end_date AS "investation_success_approval",
    investation_success_fund_transfer.application_end_date AS "investation_success_fund_transfer",
    investation_success_share_distribution.application_end_date AS "investation_success_share_distribution"
FROM
    users
INNER JOIN publisher ON users.user_id = publisher.user_id
LEFT JOIN publisher_finance ON publisher.publisher_id = publisher_finance.publisher_id
LEFT JOIN publisher_legal ON publisher.publisher_id = publisher_legal.publisher_id
LEFT JOIN publisher_proposal ON publisher.publisher_id = publisher_proposal.publisher_id
LEFT JOIN (
    SELECT
        manual_transaction.transaction_id AS "va_transaction_id",
        manual_transaction.opening_date AS "va_created_date",
        publisher.publisher_id AS "publisher_id",
        manual_transaction.status AS "va_transaction_status",
        manual_transaction.last_modified_date AS "va_last_modified_date",
        ROW_NUMBER() OVER (PARTITION BY publisher.publisher_id ORDER BY manual_transaction.opening_date DESC) AS row_num
    FROM
        publisher
    LEFT JOIN manual_transaction ON publisher.publisher_id = manual_transaction.publisher_publisher_id
    LEFT JOIN application ON manual_transaction.application_application_id = application.application_id
    LEFT JOIN application_process_task ON application.application_id = application_process_task.application_application_id
    LEFT JOIN process_task ON application_process_task.process_task_process_seq = process_task.process_seq
    LEFT JOIN workflow ON application.workflow_workflow_id = workflow.workflow_id
    WHERE
        workflow.workflow_id = '3'
        AND manual_transaction.type LIKE '%%REGISTRATION_OPENING%%'
) primary_product_registration ON publisher.publisher_id = primary_product_registration.publisher_id AND primary_product_registration.row_num = 1
LEFT JOIN (
    SELECT
        publisher.publisher_id AS "publisher_id",
        application_process.last_modified_date AS "application_end_date",
        ROW_NUMBER() OVER (PARTITION BY publisher.publisher_id ORDER BY application_process.last_modified_date DESC) AS row_num
    FROM
        publisher
    LEFT JOIN manual_transaction ON publisher.publisher_id = manual_transaction.publisher_publisher_id
    LEFT JOIN application ON manual_transaction.application_application_id = application.application_id
    LEFT JOIN application_process ON application.application_id = application_process.application_application_id
    WHERE
        application_process.process_workflow_workflow_id = '3'
        AND application_process.process_process_seq = '5'
) va_operational_approval ON publisher.publisher_id = va_operational_approval.publisher_id AND va_operational_approval.row_num = 1
LEFT JOIN (
    SELECT
        publisher.publisher_id AS "publisher_id",
        application_process.last_modified_date AS "application_end_date",
        ROW_NUMBER() OVER (PARTITION BY publisher.publisher_id ORDER BY application_process.last_modified_date DESC) AS row_num
    FROM
        publisher
    LEFT JOIN manual_transaction ON publisher.publisher_id = manual_transaction.publisher_publisher_id
    LEFT JOIN application ON manual_transaction.application_application_id = application.application_id
    LEFT JOIN application_process ON application.application_id = application_process.application_application_id
    WHERE
        application_process.process_workflow_workflow_id = '3'
        AND application_process.process_process_seq = '6'
) approval_registration_fee ON publisher.publisher_id = approval_registration_fee.publisher_id
LEFT JOIN (
    SELECT
        publisher.publisher_id AS "publisher_id",
        application_process.last_modified_date AS "application_end_date",
        ROW_NUMBER() OVER (PARTITION BY publisher.publisher_id ORDER BY application_process.last_modified_date DESC) AS row_num
    FROM
        publisher
    LEFT JOIN manual_transaction ON publisher.publisher_id = manual_transaction.publisher_publisher_id
    LEFT JOIN application ON manual_transaction.application_application_id = application.application_id
    LEFT JOIN application_process ON application.application_id = application_process.application_application_id
    WHERE
        application_process.process_workflow_workflow_id = '3'
        AND application_process.process_process_seq = '7'
) primary_offering_input ON publisher.publisher_id = primary_offering_input.publisher_id
LEFT JOIN (
    SELECT
        publisher.publisher_id AS "publisher_id",
        application_process.last_modified_date AS "application_end_date",
        ROW_NUMBER() OVER (PARTITION BY publisher.publisher_id ORDER BY application_process.last_modified_date DESC) AS row_num
    FROM
        publisher
    LEFT JOIN manual_transaction ON publisher.publisher_id = manual_transaction.publisher_publisher_id
    LEFT JOIN application ON manual_transaction.application_application_id = application.application_id
    LEFT JOIN application_process ON application.application_id = application_process.application_application_id
    WHERE
        application_process.process_workflow_workflow_id = '3'
        AND application_process.process_process_seq = '8'
) confirmation_primary_offering ON publisher.publisher_id = confirmation_primary_offering.publisher_id
LEFT JOIN (
    SELECT
        publisher.publisher_id AS "publisher_id",
        application_process.last_modified_date AS "application_end_date",
        ROW_NUMBER() OVER (PARTITION BY publisher.publisher_id ORDER BY application_process.last_modified_date DESC) AS row_num
    FROM
        publisher
    LEFT JOIN share ON publisher.publisher_id = share.publisher
    LEFT JOIN investation ON share.investation = investation.investation_id
    LEFT JOIN application ON investation.finished_application_application_id = application.application_id
    LEFT JOIN application_process ON application.application_id = application_process.application_application_id
    WHERE
        application_process.process_workflow_workflow_id = '6'
        AND application_process.process_seq = '1'
) cbestreporting ON publisher.publisher_id = cbestreporting.publisher_id
LEFT JOIN (
    SELECT
        publisher.publisher_id AS "publisher_id",
        application_process.last_modified_date AS "application_end_date",
        ROW_NUMBER() OVER (PARTITION BY publisher.publisher_id ORDER BY application_process.last_modified_date DESC) AS row_num
    FROM
        publisher
    LEFT JOIN share ON publisher.publisher_id = share.publisher
    LEFT JOIN investation ON share.investation = investation.investation_id
    LEFT JOIN application ON investation.finished_application_application_id = application.application_id
    LEFT JOIN application_process ON application.application_id = application_process.application_application_id
    WHERE
        application_process.process_workflow_workflow_id = '6'
        AND application_process.process_seq = '2'
) investation_success_sk_upload ON publisher.publisher_id = investation_success_sk_upload.publisher_id
LEFT JOIN (
    SELECT
        publisher.publisher_id AS "publisher_id",
        application_process.last_modified_date AS "application_end_date",
        ROW_NUMBER() OVER (PARTITION BY publisher.publisher_id ORDER BY application_process.last_modified_date DESC) AS row_num
    FROM
        publisher
    LEFT JOIN share ON publisher.publisher_id = share.publisher
    LEFT JOIN investation ON share.investation = investation.investation_id
    LEFT JOIN application ON investation.finished_application_application_id = application.application_id
    LEFT JOIN application_process ON application.application_id = application_process.application_application_id
    WHERE
        application_process.process_workflow_workflow_id = '6'
        AND application_process.process_seq = '3'
) investation_success_check ON publisher.publisher_id = investation_success_check.publisher_id
LEFT JOIN(
    SELECT
        publisher.publisher_id AS "publisher_id",
        application_process.last_modified_date AS "application_end_date",
        ROW_NUMBER() OVER (PARTITION BY publisher.publisher_id ORDER BY application_process.last_modified_date DESC) AS row_num
    FROM
        publisher
    LEFT JOIN share ON publisher.publisher_id = share.publisher
    LEFT JOIN investation ON share.investation = investation.investation_id
    LEFT JOIN application ON investation.finished_application_application_id = application.application_id
    LEFT JOIN application_process ON application.application_id = application_process.application_application_id
    WHERE
        application_process.process_workflow_workflow_id = '6'
        AND application_process.process_seq = '4'
) investation_success_approval ON publisher.publisher_id = investation_success_approval.publisher_id
LEFT JOIN (
    SELECT
        publisher.publisher_id AS "publisher_id",
        application_process.last_modified_date AS "application_end_date",
        ROW_NUMBER() OVER (PARTITION BY publisher.publisher_id ORDER BY application_process.last_modified_date DESC) AS row_num
    FROM
        publisher
    LEFT JOIN share ON publisher.publisher_id = share.publisher
    LEFT JOIN investation ON share.investation = investation.investation_id
    LEFT JOIN application ON investation.finished_application_application_id = application.application_id
    LEFT JOIN application_process ON application.application_id = application_process.application_application_id
    WHERE
        application_process.process_workflow_workflow_id = '6'
        AND application_process.process_seq = '5'
) investation_success_fund_transfer ON publisher.publisher_id = investation_success_fund_transfer.publisher_id
LEFT JOIN (
    SELECT
        publisher.publisher_id AS "publisher_id",
        application_process.last_modified_date AS "application_end_date",
        ROW_NUMBER() OVER (PARTITION BY publisher.publisher_id ORDER BY application_process.last_modified_date DESC) AS row_num
    FROM
        publisher
    LEFT JOIN share ON publisher.publisher_id = share.publisher
    LEFT JOIN investation ON share.investation = investation.investation_id
    LEFT JOIN application ON investation.finished_application_application_id = application.application_id
    LEFT JOIN application_process ON application.application_id = application_process.application_application_id
    WHERE
        application_process.process_workflow_workflow_id = '6'
        AND application_process.process_seq = '6'
) investation_success_share_distribution ON publisher.publisher_id = investation_success_share_distribution.publisher_id
WHERE
    users.email NOT LIKE '%%+%%'
    AND users.email NOT LIKE '%%Test%%'
    AND publisher.company_name NOT LIKE '%%Test%%'
