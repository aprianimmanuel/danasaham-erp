SELECT
    users.user_id AS "user_id",
    users.created_date AS "initial_registration_date",
    users.name AS "user_name",
    users.email AS "registered_user_email",
    users.phone_number AS "users_phone_number",
    email_confirmed AS "has_email_confirmed",
    users.last_modified_date AS "users_last_modified_date",
    publisher.created_date AS "user_upgrade_to_publisher_date",
    publisher.company_name AS "publisher_registered_name",
    publisher.corporate_type AS "publisher_corporate_type",
    publisher.phone_number AS "publisher_phone_number",
    publisher.business_field AS "publisher_business_field",
    company_profile.main_business AS "publisher_main_business",
    address.deskripsi AS "domicile_address_publisher_1",
    address.detail AS "domicile_address_publisher_2",
    company_profile.domicile AS "domicile_address_publisher_3_city",
    publisher.last_modified_date AS "publisher_last_modified_date",
    pengurus.pengurus_id AS "pengurus_id",
    pengurus.nama AS "pengurus_name",
    pengurus.id_ktp AS "pengurus_id_number",
    pengurus.phone_number AS "pengurus_phone_number",
    CASE
        WHEN pengurus.is_company = 'TRUE' AND pengurus.is_contact_person = 'FALSE' AND pengurus.is_owner = 'FALSE' THEN 'PENERBIT'
        WHEN pengurus.is_company = 'FALSE' AND pengurus.is_contact_person = 'TRUE' AND pengurus.is_owner = 'FALSE' THEN 'CONTACT PERSON / BUKAN PEMILIK'
        WHEN pengurus.is_company = 'FALSE' AND pengurus.is_contact_person = 'FALSE' AND pengurus.is_owner = 'TRUE' THEN 'PEMILIK'
        WHEN pengurus.is_company = 'TRUE' AND pengurus.is_contact_person = 'TRUE' AND pengurus.is_owner = 'TRUE' THEN 'PEMILIK SEKALIGUS CONTACT PERSON'
        WHEN pengurus.is_company = 'FALSE' AND pengurus.is_contact_person = 'TRUE' AND pengurus.is_owner = 'TRUE' THEN 'PEMILIK SEKALIGUS CONTACT PERSON'
        WHEN pengurus.is_company = NULL AND pengurus.is_contact_person = 'TRUE' AND pengurus.is_owner = NULL THEN 'CONTACT PERSON / BUKAN PEMILIK / BISA JADI DIREKSI/KOMISARIS/STAFF'
        WHEN pengurus.is_company = 'FALSE' AND pengurus.is_contact_person = 'FALSE' AND pengurus.is_owner = 'FALSE' THEN 'DIREKSI / STAFF / KOMISARIS'
        WHEN pengurus.is_company = 'TRUE' AND pengurus.is_contact_person = 'FALSE' AND pengurus.is_owner = 'TRUE' THEN 'DIREKSI / STAFF / KOMISARIS'
        WHEN pengurus.is_company = NULL AND pengurus.is_contact_person = NULL AND pengurus.is_owner = NULL THEN 'DIREKSI / KOMISARIS / STAFF'
        ELSE ''
    END AS "role_as",
    lk1.description AS "jabatan_pengurus",
    pengurus.address AS "address_pengurus",
    pengurus.dob AS "tgl_lahir_pengurus",
    pengurus.pob AS "tempat_lahir_pengurus",
    pengurus.last_modified_date AS "pengurus_publisher_last_modified_date"
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
    users.email NOT LIKE '%+%'
    AND publisher.corporate_type IS NOT NULL
    AND publisher.company_name NOT LIKE '%testing%'
    AND publisher.company_name NOT LIKE '%Test%'
    AND publisher.company_name NOT LIKE '%test%'
    AND publisher.company_name NOT LIKE '%abcd%';



