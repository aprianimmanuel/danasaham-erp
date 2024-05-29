# API Documentation

## General Information

- **API Version:** 0.4.2
- **Base URL:** `http://localhost:8000/api`

## Authentication

This API uses several methods for authentication:
- **JWT Authentication (jwtAuth):** Users must provide a JSON Web Token (JWT) in the `Authorization` header as a bearer token.
- **Token Authentication (tokenAuth):** An API key must be provided in the `Authorization` header with the prefix "Token".
- **JWT Header Authentication (jwtHeaderAuth):** Similar to JWT Authentication, requires JWT in the `Authorization` header.
- **JWT Cookie Authentication (jwtCookieAuth):** JWTs are provided via cookies, primarily used for browser-based sessions.

## Endpoints

### Documents

#### List All Documents
- **GET /api/documents/**
- **Description:** Retrieves a list of all documents.
- **Security:** jwtAuth, tokenAuth, jwtHeaderAuth, jwtCookieAuth
- **Responses:**
  - `200 OK`: Returns an array of `Document` objects.

#### Retrieve a Document
- **GET /api/documents/{document_id}/**
- **Description:** Fetches a specific document using its unique identifier.
- **Parameters:**
  - `document_id`: Unique identifier of the document.
- **Security:** jwtAuth, tokenAuth, jwtHeaderAuth, jwtCookieAuth
- **Responses:**
  - `200 OK`: Returns a `Document` object.

#### Update a Document
- **PUT /api/documents/{document_id}/**
- **Description:** Completely replaces a document with a new one.
- **Parameters:**
  - `document_id`: Unique identifier of the document.
- **Request Body:** `Document` (JSON, Form URL-encoded, or Multipart Form Data)
- **Security:** jwtAuth, tokenAuth, jwtHeaderAuth, jwtCookieAuth
- **Responses:**
  - `200 OK`: Returns the updated `Document` object.

#### Partially Update a Document
- **PATCH /api/documents/{document_id}/**
- **Description:** Partially updates fields of a document.
- **Parameters:**
  - `document_id`: Unique identifier of the document.
- **Request Body:** `PatchedDocument` (JSON, Form URL-encoded, or Multipart Form Data)
- **Security:** jwtAuth, tokenAuth, jwtHeaderAuth, jwtCookieAuth
- **Responses:**
  - `200 OK`: Returns the updated `Document` object.

#### Delete a Document
- **DELETE /api/documents/{document_id}/**
- **Description:** Deletes a specific document.
- **Parameters:**
  - `document_id`: Unique identifier of the document.
- **Security:** jwtAuth, tokenAuth, jwtHeaderAuth, jwtCookieAuth
- **Responses:**
  - `204 No Content`: Document successfully deleted, no response body.

### User Registration

#### Register a New User
- **POST /api/registration/**
- **Description:** Registers a new user with the system.
- **Request Body:** `CustomRegister` (JSON, Form URL-encoded, or Multipart Form Data)
- **Security:** jwtAuth, tokenAuth, jwtHeaderAuth, jwtCookieAuth
- **Responses:**
  - `201 Created`: Returns a `CustomRegister` object with user details.

#### Resend Email Verification
- **POST /api/registration/user/resend-email/**
- **Description:** Resends the email verification link to the user.
- **Request Body:** `ResendEmailVerification` (JSON, Form URL-encoded, or Multipart Form Data)
- **Security:** jwtAuth, tokenAuth, jwtHeaderAuth, jwtCookieAuth
- **Responses:**
  - `201 Created`: Verification email resent, returns `RestAuthDetail` object.

#### Verify Email
- **POST /api/registration/user/verify-email/**
- **Description:** Verifies user's email with a verification token.
- **Request Body:** `VerifyEmail` (JSON, Form URL-encoded, or Multipart Form Data)
- **Security:** jwtAuth, tokenAuth, jwtHeaderAuth, jwtCookieAuth
- **Responses:**
  - `200 OK`: Email successfully verified, returns `RestAuthDetail` object.

### Security

#### Get API Schema
- **GET /api/schema/**
- **Description:** Retrieves the OpenAPI schema in various formats.
- **Parameters:**
  - `format`: The format of the schema, either `json` or `yaml`.
  - `lang`: Language code for localization (e.g., `en`, `fr`).
- **Security:** jwtAuth, tokenAuth, jwtHeaderAuth, jwtCookieAuth
- **Responses:**
  - `200 OK`: Returns the API schema in the requested format.
