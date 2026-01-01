# Admin Dashboard Documentation

This document outlines the API endpoints and WebSocket features dedicated to the Admin Dashboard for the Dollar Pay backend.

## 1. Authentication

Admins must authenticate to access dashboard endpoints.

- **Login**: `POST /api/v1/auth/admin/login`
  - **Body**: `{"username": "admin", "password": "password"}`
  - **Response**: `{"access_token": "jwt_token", "token_type": "bearer"}`

All subsequent requests must include the header: `Authorization: Bearer <jwt_token>`

## 2. Dashboard Statistics

Endpoints for populating the main dashboard view.

### Get Overall Stats
- **Endpoint**: `GET /api/v1/dashboard/stats`
- **Description**: Returns aggregated statistics for users, transactions, volume, and revenue.
- **Response**:
  ```json
  {
    "users": {
      "total": 150,
      "active": 120
    },
    "transactions": {
      "total": 500,
      "pending": 5,
      "completed": 450
    },
    "volume": {
      "deposits": 50000.0,
      "withdrawals": 20000.0,
      "net": 30000.0
    },
    "revenue": {
      "platform_fees": 1500.0
    }
  }
  ```

### Get Transaction Charts
- **Endpoint**: `GET /api/v1/dashboard/transactions-chart`
- **Query Params**: `days` (default: 30)
- **Description**: Returns time-series data for transaction counts and volume over the specified period.
- **Response**:
  ```json
  {
    "daily_transactions": [
      {"date": "2024-01-15", "count": 25}
    ],
    "type_breakdown": [
      {"type": "crypto_deposit", "count": 100},
      {"type": "withdrawal", "count": 50}
    ],
    "status_breakdown": [
      {"status": "pending", "count": 5},
      {"status": "completed", "count": 145}
    ]
  }
  ```

### Get Users Chart
- **Endpoint**: `GET /api/v1/dashboard/users-chart`
- **Query Params**: `days` (default: 30)
- **Description**: Returns user registration data for charts.
- **Response**:
  ```json
  {
    "daily_registrations": [
      {"date": "2024-01-15", "count": 10}
    ],
    "cumulative_users": [
      {"date": "2024-01-15", "cumulative": 150}
    ]
  }
  ```

### Get Revenue Chart
- **Endpoint**: `GET /api/v1/dashboard/revenue-chart`
- **Query Params**: `days` (default: 30)
- **Description**: Returns revenue data (platform fees) for charts.
- **Response**:
  ```json
  {
    "daily_fees": [
      {"date": "2024-01-15", "fees": 150.0}
    ]
  }
  ```

### Get Recent Activity
- **Endpoint**: `GET /api/v1/dashboard/recent-activity`
- **Query Params**: `limit` (default: 10)
- **Description**: Returns recent transaction activity for the dashboard.
- **Response**:
  ```json
  [
    {
      "id": 123,
      "transaction_uid": "DEP12345678",
      "type": "crypto_deposit",
      "status": "pending",
      "amount": 100.0,
      "user_id": 456,
      "created_at": "2024-01-15T10:30:00"
    }
  ]
  ```

## 3. Transaction Management

Endpoints for reviewing and managing user transactions.

### Get Pending Transactions
- **Endpoint**: `GET /api/v1/transactions/admin/pending`
- **Description**: Returns a list of all transactions with status `pending` requiring admin action.

### Get All Transactions
- **Endpoint**: `GET /api/v1/transactions/admin/transactions`
- **Query Params**: 
  - `status` (optional): Filter by status (e.g., `pending`, `approved`, `rejected`)
  - `type` (optional): Filter by type (e.g., `crypto_deposit`, `withdrawal`)
  - `limit` (default: 20)
  - `offset` (default: 0)
- **Description**: Returns a paginated list of transactions with filtering options.

### Get Transaction Detail
- **Endpoint**: `GET /api/v1/transactions/admin/transactions/{transaction_id}`
- **Description**: Returns full details of a specific transaction, including user info and screenshot URL.

### Review Transaction (Approve/Reject)
- **Endpoint**: `PUT /api/v1/transactions/admin/transactions/{transaction_id}/review`
- **Body**:
  ```json
  {
    "status": "approved",  // or "rejected"
    "admin_notes": "Verified on blockchain",
    "rejection_reason": null,
    "payment_reference": "TX123456", // Optional, for withdrawals
    "transaction_fee": 0,
    "platform_fee": 10.0
  }
  ```
- **Description**: Approves or rejects a transaction. 
  - **Deposits**: Approving credits the user's wallet and calculates commissions.
  - **Withdrawals**: Approving marks it as completed (manual payout assumed).

## 4. Platform Settings

Endpoints for configuring global platform variables.

### Get Settings
- **Endpoint**: `GET /api/v1/transactions/admin/settings`
- **Description**: Returns all configurable platform settings (e.g., exchange rates, fees).
- **Response**:
  ```json
  [
    {
      "id": 1,
      "setting_key": "usdt_to_inr_rate",
      "setting_value": "92.5",
      "data_type": "float",
      "description": "Current USDT to INR exchange rate",
      "updated_by_admin_id": 1,
      "updated_at": "2024-01-15T10:30:00"
    }
  ]
  ```

### Update Setting
- **Endpoint**: `PUT /api/v1/transactions/admin/settings`
- **Body**:
  ```json
  {
    "setting_key": "usdt_to_inr_rate",
    "setting_value": "92.5",
    "data_type": "float",
    "description": "Current exchange rate"
  }
  ```
- **Description**: Updates a specific platform setting.

## 5. Real-time Notifications (WebSocket)

The admin dashboard uses WebSockets to receive real-time updates for new transactions.

### Connection
- **URL**: `ws://<host>/ws/{admin_id}?token=<jwt_token>`
- **Description**: Establishes a persistent connection. The `token` query parameter is required for authentication. 
  - For admins, use your admin ID as the `{admin_id}` parameter
  - The endpoint works for both users and admins based on the role in the JWT token
  - Admins will receive notifications for all new transactions
  - Regular users will only receive notifications for their own transactions

### Events
The server sends JSON messages when specific events occur.

#### New Transaction Alert
Triggered when a user creates a new deposit or withdrawal request.
```json
{
    "type": "new_transaction",
    "transaction_id": 123,
    "transaction_uid": "DEP12345678",
    "user_id": 456,
    "transaction_type": "crypto_deposit",
    "amount": 100.0,
    "network": "TRC20",
    "message": "New crypto deposit request from user 456"
}
```

## 6. User Management (Planned)

*Note: Dedicated admin endpoints for user management (blocking, viewing details) are currently under `app/api/v1/endpoints/user.py` or planned for future implementation.*
