# Dollar Pay Backend - API Endpoints

Base URL: `https://dollar-pay-backend.onrender.com`

---

## 🔐 Authentication Endpoints

### User Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/auth/register` | Register a new user with phone number, password, and optional referral code | No |
| `POST` | `/auth/login` | Login user and return JWT token | No |

### Admin Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/auth/admin/register` | Register a new admin (Super Admin only) | Yes (Super Admin) |
| `POST` | `/auth/admin/login` | Login admin and return JWT token | No |

---

## 👤 User Endpoints

### User Profile & Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/user/profile` | Get current user profile with wallet balance and team stats | Yes (User) |
| `GET` | `/user/team` | Get list of team members referred by the current user | Yes (User) |
| `GET` | `/user/commissions` | Get history of commissions earned | Yes (User) |
| `PUT` | `/user/bind-upi` | Bind UPI details to user account | Yes (User) |

### Admin User Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/admin/users` | Get all users with pagination and search | Yes (Admin) |

**Query Parameters for `/admin/users`:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `search` (string): Search by username, email, or phone

---

## 💰 Transaction Endpoints

### User Transactions
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/transactions/deposit` | Create a deposit transaction with screenshot URL | Yes (User) |
| `POST` | `/transactions/withdrawal` | Create a withdrawal request | Yes (User) |
| `GET` | `/transactions/my-transactions` | Get user's transactions with pagination | Yes (User) |
| `GET` | `/transactions/balance` | Get user's wallet balance and transaction summary | Yes (User) |
| `GET` | `/transactions/{transaction_id}` | Get specific transaction details | Yes (User) |

**Query Parameters for `/transactions/my-transactions`:**
- `limit` (int): Number of transactions (default: 20)
- `offset` (int): Offset for pagination (default: 0)

### Admin Transaction Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/admin/transactions` | Get all transactions with pagination and filters | Yes (Admin) |
| `GET` | `/admin/transactions/pending` | Get all pending transactions for review | Yes (Admin) |
| `GET` | `/admin/transactions/{transaction_id}` | Get specific transaction details | Yes (Admin) |
| `PUT` | `/admin/transactions/{transaction_id}/review` | Review transaction (approve or reject) | Yes (Admin) |

**Query Parameters for `/admin/transactions`:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `status` (string): Filter by status (pending, completed, rejected)
- `type` (string): Filter by type (deposit, withdrawal)

---

## ⚙️ Settings Endpoints

### Platform Settings (Admin Only)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/admin/settings` | Get all platform settings | Yes (Admin) |
| `PUT` | `/admin/settings` | Update platform setting | Yes (Admin) |

---

## 📊 Dashboard Endpoints

### Admin Dashboard
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/dashboard/stats` | Get overall dashboard statistics | Yes (Admin) |
| `GET` | `/dashboard/transactions-chart` | Get transaction data for charts | Yes (Admin) |
| `GET` | `/dashboard/users-chart` | Get user registration data for charts | Yes (Admin) |
| `GET` | `/dashboard/revenue-chart` | Get revenue data for charts | Yes (Admin) |
| `GET` | `/dashboard/recent-activity` | Get recent transaction activity | Yes (Admin) |

**Query Parameters for chart endpoints:**
- `days` (int): Number of days to include (default: 30)

**Query Parameters for `/dashboard/recent-activity`:**
- `limit` (int): Number of recent activities (default: 10)

---

## 🔔 WebSocket Endpoints

### Real-time Notifications
| Protocol | Endpoint | Description | Auth Required |
|----------|----------|-------------|---------------|
| `WS` | `/ws/{user_id}?token={jwt_token}` | WebSocket endpoint for real-time notifications | Yes (JWT in query param) |
| `WS` | `/ws/notifications` | WebSocket for admin notifications | Yes |

---

## 🏠 Utility Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | API root - health check message | No |
| `GET` | `/health` | Health check endpoint | No |

---

## 📝 Notes

### Authentication
- Most endpoints require JWT authentication via `Authorization: Bearer {token}` header
- User endpoints require user JWT token
- Admin endpoints require admin JWT token
- WebSocket requires JWT token as query parameter

### Response Format
All responses follow standard JSON format with appropriate HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

### Pagination
Paginated endpoints return:
```json
{
  "data": [...],
  "total": 100,
  "page": 1,
  "limit": 20,
  "total_pages": 5
}
```

---

**Last Updated:** January 3, 2026
