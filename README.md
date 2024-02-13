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
1. **Create a New User:**
   - **Endpoint:** `POST /api/users/`
   - **Request Method:** POST
   - **Request Body:** JSON object containing user information (e.g., email, username, password)
   - **Response:** JSON object containing the newly created user's details or an error message

2. **Get List of All Users:**
   - **Endpoint:** `GET /api/users/`
   - **Request Method:** GET
   - **Response:** JSON array containing details of all users or an error message

3. **Get Details of a Specific User:**
   - **Endpoint:** `GET /api/users/{user_id}`
   - **Request Method:** GET
   - **Response:** JSON object containing details of the specified user or an error message

4. **Update Details of a User:**
   - **Endpoint:** `PUT /api/users/{user_id}`
   - **Request Method:** PUT
   - **Request Body:** JSON object containing updated user information
   - **Response:** JSON object containing the updated user's details or an error message

5. **Delete a User:**
   - **Endpoint:** `DELETE /api/users/{user_id}`
   - **Request Method:** DELETE
   - **Response:** JSON object indicating success or failure of user deletion

6. **Search for Users by Name or Email:**
   - **Endpoint:** `GET /api/users/search/`
   - **Request Method:** GET
   - **Query Parameters:** `q` (search query)
   - **Response:** JSON array containing users matching the search query or an empty array

7. **Reset User's Password:**
   - **Endpoint:** `POST /api/users/{user_id}/reset-password`
   - **Request Method:** POST
   - **Request Body:** JSON object containing new password
   - **Response:** JSON object indicating success or failure of password reset

8. **Lock/Unlock User Account:**
   - **Endpoint:** `PATCH /api/users/{user_id}/lock-unlock`
   - **Request Method:** PATCH
   - **Request Body:** JSON object containing `is_locked` field
   - **Response:** JSON object indicating success or failure of account lock/unlock

9. **Change User Role:**
   - **Endpoint:** `PATCH /api/users/{user_id}/change-role`
   - **Request Method:** PATCH
   - **Request Body:** JSON object containing `role` field
   - **Response:** JSON object indicating success or failure of role change

### Authentication and Authorization:

1. **User Login:**
   - **Endpoint:** `POST /api/auth/login`
   - **Request Method:** POST
   - **Request Body:** JSON object containing email and password
   - **Response:** JSON object containing access token or an error message

2. **User Logout:**
   - **Endpoint:** `POST /api/auth/logout`
   - **Request Method:** POST
   - **Response:** JSON object indicating success or failure of logout

3. **Refresh Access Token:**
   - **Endpoint:** `POST /api/auth/refresh-token`
   - **Request Method:** POST
   - **Request Body:** JSON object containing refresh token
   - **Response:** JSON object containing new access token or an error message

4. **Validate Token:**
   - **Endpoint:** `POST /api/auth/validate-token`
   - **Request Method:** POST
   - **Request Body:** JSON object containing access token
   - **Response:** JSON object indicating validity of the token

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

