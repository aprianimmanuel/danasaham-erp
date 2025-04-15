WITH dsb_user_publisher AS (
    SELECT
        users.user_id AS "user_id",
        users.created_date AS "initial_registration_date",
        users.name AS "user_name",
        NULLIF(users.email, '') AS "users_email_registered", users.email AS "registered_user_email",
        users.phone_number AS "users_phone_number",
        users.last_modified_date AS "users_last_modified_date",
        publisher.created_date AS "user_upgrade_to_publisher_date",
        NULLIF(publisher.company_name, '') AS "publisher_registered_name",
        NULLIF(publisher.corporate_type, '') AS "publisher_corporate_type",
        NULLIF(publisher.phone_number, '') AS "publisher_phone_number",
        NULLIF(publisher.business_field, '') AS "publisher_business_field",
        NULLIF(company_profile.main_business, '') AS "publisher_main_business",
        address.deskripsi AS "domicile_address_publisher_1",
        NULLIF(address.detail, '') AS "domicile_address_publisher_2",
        NULLIF(company_profile.domicile, '') AS "domicile_address_publisher_3_city",
        publisher.last_modified_date AS "publisher_last_modified_date",
        pengurus.pengurus_id AS "publisher_pengurus_id",
        NULLIF(pengurus.nama, '') AS "publisher_pengurus_name",
        NULLIF(pengurus.id_ktp, '') AS "publisher_pengurus_id_number",
        NULLIF(pengurus.phone_number, '') AS "publisher_pengurus_phone_number",
        CASE
            WHEN pengurus.is_company = 'TRUE' AND pengurus.is_contact_person = 'FALSE' AND pengurus.is_owner = 'FALSE' THEN 'PENERBIT'
            WHEN pengurus.is_company = 'FALSE' AND pengurus.is_contact_person = 'TRUE' AND pengurus.is_owner = 'FALSE' THEN 'CONTACT PERSON / BUKAN PEMILIK'
            WHEN pengurus.is_company = 'FALSE' AND pengurus.is_contact_person = 'FALSE' AND pengurus.is_owner = 'TRUE' THEN 'PEMILIK'
            WHEN pengurus.is_company = 'TRUE' AND pengurus.is_contact_person = 'TRUE' AND pengurus.is_owner = 'TRUE' THEN 'PEMILIK SEKALIGUS CONTACT PERSON'
            WHEN pengurus.is_company = 'FALSE' AND pengurus.is_contact_person = 'TRUE' AND pengurus.is_owner = 'TRUE' THEN 'PEMILIK SEKALIGUS CONTACT PERSON'
            WHEN pengurus.is_company IS NULL AND pengurus.is_contact_person = 'TRUE' AND pengurus.is_owner IS NULL THEN 'CONTACT PERSON / BUKAN PEMILIK / BISA JADI DIREKSI/KOMISARIS/STAFF'
            WHEN pengurus.is_company = 'FALSE' AND pengurus.is_contact_person = 'FALSE' AND pengurus.is_owner = 'FALSE' THEN 'DIREKSI / STAFF / KOMISARIS'
            WHEN pengurus.is_company = 'TRUE' AND pengurus.is_contact_person = 'FALSE' AND pengurus.is_owner = 'TRUE' THEN 'DIREKSI / STAFF / KOMISARIS'
            WHEN pengurus.is_company IS NULL AND pengurus.is_contact_person IS NULL AND pengurus.is_owner IS NULL THEN 'DIREKSI / KOMISARIS / STAFF'
            ELSE ''
        END AS "publisher_pengurus_role_as",
        NULLIF(lk1.description, '') AS "publisher_jabatan_pengurus",
        NULLIF(pengurus.address,'') AS "publisher_address_pengurus",
        NULLIF(TO_CHAR(TO_DATE(pengurus.dob, 'DD/MM/YYYY'), 'YYYY-MM-DD'), '') AS "publisher_tgl_lahir_pengurus",
        NULLIF(pengurus.pob, '') AS "publisher_tempat_lahir_pengurus",
        pengurus.last_modified_date AS "pengurus_publisher_last_modified_date",
        ROW_NUMBER() OVER (PARTITION BY pengurus.pengurus_id ORDER BY pengurus.last_modified_date DESC) AS row_num
    FROM users
    INNER JOIN publisher ON users.user_id = publisher.user_id
    LEFT JOIN personal ON publisher.contact_person_id = personal.personal_id
    LEFT JOIN address ON publisher.address_address_id = address.address_id
    INNER JOIN publisher_legal ON publisher.publisher_id = publisher_legal.publisher_id
    LEFT JOIN pengurus ON publisher_legal.publisher_legal_id = pengurus.publisher_legal_id
    LEFT JOIN investation ON publisher.publisher_id = investation.publisher_publisher_id
    LEFT JOIN company_profile ON investation.company_profile_owner_profile_id = company_profile.owner_profile_id
    LEFT JOIN lookup lk1 ON pengurus.jabatan_lookup_id = lk1.lookup_id
    WHERE
        users.email NOT LIKE '%%+%%'
        AND publisher.corporate_type IS NOT NULL
        AND publisher.company_name NOT LIKE '%%testing%%'
        AND publisher.company_name NOT LIKE '%%Test%%'
        AND publisher.company_name NOT LIKE '%%test%%'
        AND publisher.company_name NOT LIKE '%%abcd%%'
        AND pengurus.pengurus_id IS NOT NULL
)
SELECT
    "user_id",
    "initial_registration_date",
    "user_name",
    "registered_user_email",
    "users_phone_number",
    "users_last_modified_date",
    "user_upgrade_to_publisher_date",
    "publisher_registered_name",
    "publisher_corporate_type",
    "publisher_phone_number",
    "publisher_business_field",
    "publisher_main_business",
    "domicile_address_publisher_1",
    "domicile_address_publisher_2",
    "domicile_address_publisher_3_city",
    "publisher_last_modified_date",
    "publisher_pengurus_id",
    "publisher_pengurus_name",
    "publisher_pengurus_id_number",
    "publisher_pengurus_phone_number",
    "publisher_pengurus_role_as",
    "publisher_jabatan_pengurus",
    "publisher_address_pengurus",
    "publisher_tgl_lahir_pengurus",
    "publisher_tempat_lahir_pengurus",
    "pengurus_publisher_last_modified_date"
FROM dsb_user_publisher
WHERE row_num = 1;
