SELECT
    users.user_id AS "user_id",
    users.created_date as "initial_registration_date",
    users.name as "user_name",
    users.email AS "registered_user_email",
    users.phone_number AS "users_phone_number",
    users.last_modified_date AS "users_last_modofied_date",
    pengurus.pengurus_id AS "corporate_pengurus_id",
    pengurus.nama AS "pengurus_corporate_name",
    pengurus.id_ktp AS "pengurus_corporate_idnumber",
    pengurus.phone_number AS "pengurus_corporate_phone_number",
    pengurus.pob AS "pengurus_corporate_place_of_birth",
    pengurus.dob AS "pengurus_corporate_date_of_birth",
    pengurus.npwp AS "pengurus_corporate_npwp",
    pengurus.address AS "pengurus_corporate_domicile_address",
    lk7.description AS "pengurus_corporate_jabatan",
    pengurus.nominal_saham AS "pengurus_nominal_saham",
    pengurus.last_modified_date AS "pengurus_corporate_last_update_date",
    corporate_legal.created_date AS "users_upgrade_to_corporate",
    corporate.company_name AS "corporate_name",
    corporate.phone_number AS "corporate_phone_number",
    corporate_legal.nib AS "corporate_nib",
    corporate_legal.npwp AS "corporate_npwp",
    corporate_legal.siup AS "corporate_siup",
    corporate_legal.skdp AS "corporate_skdp",
    corporate_legal.last_modified_date "corporate_legal_last_modified_date",
    address.deskripsi AS "corporate_domicile_address",
    lk2.description AS "corporate_asset",
    lk3.description AS "corporate_source_of_fund",
    lk4.description AS "corporate_business_field",
    lk5.description AS "corporate_type_of_annual_income",
    corporate_finance.annual_income AS "corporate_annual_income",
    lk6.description AS "corporate_investment_goals"
FROM users
INNER JOIN corporate ON users.user_id = corporate.user_id
LEFT JOIN address ON corporate.address_address_id = address.address_id
LEFT JOIN corporate_legal ON corporate.corporate_id = corporate_legal.corporate_id
LEFT JOIN pengurus ON corporate_legal.corporate_legal_id = pengurus.corporate_legal_id
LEFT JOIN corporate_finance ON corporate.corporate_id = corporate_finance.corporate_id
LEFT JOIN corporate_asset_data ON corporate_finance.corporate_finance_id = corporate_asset_data.corporate_finance_corporate_finance_id
LEFT JOIN corporate_profit_data ON corporate_finance.corporate_finance_id = corporate_profit_data.corporate_finance_corporate_finance_id
LEFT JOIN lookup lk2 ON corporate_asset_data.asset_lookup_id = lk2.lookup_id
LEFT JOIN lookup lk3 ON corporate.sof_corp_lookup_id = lk3.lookup_id
LEFT JOIN lookup lk4 ON corporate.business_type_lookup_id = lk4.lookup_id
LEFT JOIN lookup lk5 ON corporate_profit_data.profit_lookup_id = lk5.lookup_id
LEFT JOIN lookup lk6 ON corporate.investment_corp_lookup_id = lk6.lookup_id
LEFT JOIN lookup lk7 ON pengurus.jabatan_lookup_id = lk7.lookup_id
WHERE
    lk2.description IS NOT NULL
    AND lk5.description IS NOT NULL
    AND users.email NOT LIKE '%+%';