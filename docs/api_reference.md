# API Reference

This document provides detailed information about the NFC Tool's API for developers.

## Table of Contents
- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Data Types](#data-types)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the `Authorization` header:

```http
Authorization: Bearer your_jwt_token_here
```

## Base URL

All API endpoints are relative to the base URL:

```
https://api.nfctool.example.com/v1
```

## Endpoints

### Authentication

#### Login

```http
POST /auth/login
```

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Tags

#### Read Tag

```http
GET /tags/read
```

**Response:**
```json
{
  "tag_id": "04:6A:3B:7C:1D:2E:4F",
  "tag_type": "NTAG215",
  "data": {
    "type": "text",
    "content": "Hello, NFC!"
  },
  "read_at": "2023-08-01T12:34:56Z"
}
```

#### Write to Tag

```http
POST /tags/write
```

**Request Body:**
```json
{
  "data": {
    "type": "url",
    "content": "https://example.com"
  },
  "lock": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Data written successfully",
  "tag_id": "04:6A:3B:7C:1D:2E:4F"
}
```

### Users

#### Get User Profile

```http
GET /users/me
```

**Response:**
```json
{
  "id": 123,
  "username": "user@example.com",
  "role": "admin",
  "created_at": "2023-01-01T00:00:00Z",
  "last_login": "2023-08-01T10:30:00Z"
}
```

## Data Types

### Tag Data

```typescript
interface TagData {
  tag_id: string;
  tag_type: string;
  data: {
    type: 'text' | 'url' | 'contact' | 'custom';
    content: any;
  };
  read_at: string; // ISO 8601 datetime
  write_protected: boolean;
}
```

### Error Response

```typescript
interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
  };
}
```

## Error Handling

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid request format |
| 401 | Unauthorized - Authentication failed |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Something went wrong |

## Rate Limiting

- 1000 requests per hour per user
- 100 requests per minute per user
- 10 requests per second per user

## Examples

### Python Example

```python
import requests

# Authenticate
response = requests.post(
    'https://api.nfctool.example.com/v1/auth/login',
    json={
        'username': 'user@example.com',
        'password': 'your_password'
    }
)
token = response.json()['access_token']

# Read tag
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
    'https://api.nfctool.example.com/v1/tags/read',
    headers=headers
)
print(response.json())
```

### cURL Example

```bash
# Get user profile
curl -X GET \
  https://api.nfctool.example.com/v1/users/me \
  -H 'Authorization: Bearer your_jwt_token_here'
```
