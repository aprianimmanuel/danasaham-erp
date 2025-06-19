WITH dsb_user_personal AS (
    SELECT
        users.user_id AS "user_id",
        users.created_date AS "initial_registration_date",
        users.name AS "user_name",
        users.email AS "users_email_registered",
        users.last_modified_date AS "users_last_modified_date",
        personal.created_date AS "user_upgrade_to_personal_date",
        personal_legal.ktp_name AS "personal_name",
        personal.phone_number AS "personal_phone_number",
        personal_legal.gender AS "personal_gender",
        personal_legal.id_card AS "personal_nik",
        personal_legal.birth_date AS "personal_birth_date",
        NULLIF(personal_ksei_id.sre, '') AS "personal_ksei_sre",
        NULLIF(personal_ksei_id.sid, '') AS "personal_ksei_sid",
        NULLIF(personal_legal.spouse_name, '') AS "personal_spouse_name",
        personal_legal.mother_name AS "personal_mother_name",
        personal_legal.last_modified_date AS "personal_last_modified_date",
        address.deskripsi AS "personal_domicile_address",
        address.kodepos AS "personal_domicile_address_postalcode",
        lk1.description AS "personal_investment_goals",
        lk2.description AS "personal_marital_status",
        lk3.descriptioN AS "personal_birth_place",
        lk4.description AS "personal_nationality",
        lk5.description AS "personal_source_of_fund",
        ROW_NUMBER() OVER (PARTITION BY users.user_id ORDER BY users.last_modified_date DESC) AS row_num
    FROM
        users
    INNER JOIN personal ON users.user_id = personal.user_id
    INNER JOIN personal_legal ON personal.personal_id = personal_legal.personal_id
    LEFT JOIN address ON personal_legal.address = address.address_id
    LEFT JOIN personal_ksei_id ON personal.personal_id = personal_ksei_id.personal_id
    LEFT JOIN lookup lk1 ON personal_legal.investment_indv_lookup_id = lk1.lookup_id
    LEFT JOIN lookup lk2 ON personal_legal.marital_status_lookup_id = lk2.lookup_id
    LEFT JOIN lookup lk3 ON personal_legal.birth_place_lookup_id = lk3.lookup_id
    LEFT JOIN lookup lk4 ON personal_legal.nationality_lookup_id = lk4.lookup_id
    LEFT JOIN lookup lk5 ON personal_legal.sof_indv_lookup_id = lk5.lookup_id
    WHERE
        users.email NOT LIKE '%%+%%'
        AND users.name NOT LIKE '%%test%%'
        AND users.name NOT LIKE '%%Testing%%'
        AND users.name NOT LIKE '%%Test%%'
        AND users.email NOT LIKE '%%$$%%'
)
SELECT
    "user_id",
    "initial_registration_date",
    "user_name",
    "users_email_registered",
    "users_last_modified_date",
    "user_upgrade_to_personal_date",
    "personal_name",
    "personal_phone_number",
    "personal_gender",
    "personal_nik",
    "personal_birth_date",
    "personal_ksei_sre",
    "personal_ksei_sid",
    "personal_spouse_name",
    "personal_mother_name",
    "personal_last_modified_date",
    "personal_domicile_address",
    "personal_domicile_address_postalcode",
    "personal_investment_goals",
    "personal_marital_status",
    "personal_birth_place",
    "personal_nationality",
    "personal_source_of_fund"
FROM
    dsb_user_personal
WHERE
    row_num = 1
    AND TEXTREGEXEQ(personal_phone_number, '^[0-9]+$')
    AND TEXTREGEXEQ(personal_nik, '^[0-9]+$');
