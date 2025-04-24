#!/bin/bash

# Ambil dari environment variable
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
EXTERNAL_DB_USER=${EXTERNAL_DB_USERNAME}
EXTERNAL_DB_PASSWORD=${EXTERNAL_DB_PASSWORD}

# Gabungkan password dan username
COMBINED_DB_INTERNAL="${DB_PASSWORD}${DB_USER}"
COMBINED_DB_EXTERNAL="${EXTERNAL_DB_PASSWORD}${EXTERNAL_DB_USER}"

# Hash gabungan menggunakan md5
HASH_INTERNAL=$(echo -n "$COMBINED_DB_INTERNAL" | md5sum | awk '{print $1}')
HASH_EXTERNAL=$(echo -n "$COMBINED_DB_EXTERNAL" | md5sum | awk '{print $1}')

# Tambahkan prefix 'md5'
FINAL_HASH_INTERNAL="md5$HASH_INTERNAL"
FINAL_HASH_EXTERNAL="md5$HASH_EXTERNAL"

# Tampilkan hasil
echo "MD5 Hash DB Internal: $FINAL_HASH_INTERNAL"
echo "MD5 Hash DB External: $FINAL_HASH_EXTERNAL"
