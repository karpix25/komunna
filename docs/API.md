# API Documentation

## Base URL
- Development: `http://localhost:8001`
- Production: `https://api.yourdomain.com`

## Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - User logout

### Users
- `GET /users/me` - Get current user info
- `PUT /users/me` - Update current user
- `GET /users/{user_id}` - Get user by ID (admin only)

### Health Check
- `GET /health` - Health check endpoint

## Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Success"
}
```

## Error Format
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```
