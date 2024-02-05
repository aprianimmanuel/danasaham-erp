# Danasaham's Enterprises Resource Planning Apps
### Creating, Managing and Developing Enterprise Resource Planning App using Django and Docker

## List of Endpoints
### 1. *Health Check:* 
  - **Check the avalaible of the API:** `GET /api/health-check/`

### 2. *DTTOT Management:*
  - **Upload New DTTOT List Document:** `POST /api/dttot/documents/`
  - **Get List of Uploaded DTTOT Documents:** `GET /api/dttot/documents/`
  - **Run ETL Script for Uploaded List Document:** `POST /api/dttot/documents/{id}/etl`
  - **Delete Uploaded DTTOT Document:** `DELETE /api/dttot/documents/{id}`
  - **Open Uploaded DTTOT Document into Dataframe:** `GET /api/dttot/documents/{id}/dataframe`
  - **Get List of Processed DTTOT Documents:** `GET /api/dttot/processed-documents/`
  - **Search for DTTOT Data:** `GET /api/dttot/{id}`
  - **Add New Data for Related DTTOT Document:** `POST /api/dttot/{id}/data`
  - **Modify/Update Related DTTOT Data:** `PATCH /api/dttot/{id}/data`
  - **Delete Single Related DTTOT Data:** `DELETE /api/dttot/{id}/data`
  - **Get Summary Statistics for Processed DTTOT Documents:** `GET /api/dttot/summary/`
  - **Export Processed DTTOT Data to CSV:** `GET /api/dttot/export/csv/`
  - **Export Processed DTTOT Data to Excel:** `GET /api/dttot/export/excel/`
  - **Generate Report for Processed DTTOT Documents:** `POST /api/dttot/report/`
  - **Get List of Available ETL Scripts:** `GET /api/dttot/etl-scripts/`
  - **Run Specific ETL Script for DTTOT Document:** `POST /api/dttot/documents/{id}/etl/{script_id}`
  - **Get List of Users Affiliated with DTTOT:** `GET /api/dttot/affiliated-users/`
  - **Review and Approve Affiliation Status for a User:** `PATCH /api/dttot/affiliated-users/{user_id}/approve`
  - **Reject Affiliation Status for a User:** `PATCH /api/dttot/affiliated-users/{user_id}/reject`

### 3. *User Management:*
  - **Create a New User:** `POST /api/users/`
  - **Get List of All Users:** `GET /api/users/`
  - **Get Details of a Specific User:** `GET /api/users/{user_id}`
  - **Update Details of a User:** `PUT /api/users/{user_id}`
  - **Delete a User:** `DELETE /api/users/{user_id}`
  - **Search for Users by Name or Email:** `GET /api/users/search/`
  - **Reset User's Password:** `POST /api/users/{user_id}/reset-password`
  - **Lock/Unlock User Account:** `PATCH /api/users/{user_id}/lock-unlock`
  - **Change User Role:** `PATCH /api/users/{user_id}/change-role`

### 4. *Authentication and Authorization:*
  - **User Login:** `POST /api/auth/login`
  - **User Logout:** `POST /api/auth/logout`
  - **Refresh Access Token:** `POST /api/auth/refresh-token`
  - **Validate Token:** `POST /api/auth/validate-token`
  
### 5. *Audit Trail and Logs:*
  - **View Audit Trail for DTTOT Documents:** `GET /api/audit-trail/dttot-documents/`
  - **View Audit Trail for User Management Actions:** `GET /api/audit-trail/user-actions/`
  - **Download System Logs:** `GET /api/logs/download/`

### 6. *System Configuration:*
  - **Get System Configuration Settings:** `GET /api/system/config/`
  - **Update System Configuration Settings:** `PUT /api/system/config/`

### 7. *Notifications:*
  - **Send Notification to Users:** `POST /api/notifications/send/`
  - **View Notification History:** `GET /api/notifications/history/`

### 8. *Data Insights:*
  - **Retrieve Insights on DTTOT Data:** `GET /api/insights/dttot/`
  - **Retrieve User Activity Insights:** `GET /api/insights/user-activity/`

### 9. *Batch Operations:*
  - **Batch Upload DTTOT Documents:** `POST /api/batch/dttot-documents/`
  - **Batch Process DTTOT Documents:** `POST /api/batch/dttot-documents/process/`
  - **Monitor Batch Processing Status:** `GET /api/batch/status/`

### 10. *User Preferences:*
  - **Get User Preferences:** `GET /api/users/{user_id}/preferences/`
  - **Update User Preferences:** `PUT /api/users/{user_id}/preferences/`

