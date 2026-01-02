# API Documentation

## Get Users Paginated Endpoint

### Endpoint
`GET /admin/users`

### Description
Retrieve a paginated list of all users for admin purposes. Supports search functionality.

### Parameters
| Name       | Type   | Required | Description                                      |
|------------|--------|----------|--------------------------------------------------|
| `page`     | int    | No       | The page number to retrieve (default: 1).       |
| `limit`    | int    | No       | The number of users per page (default: 20).     |
| `search`   | string | No       | Search query to filter users by username, email, or phone. |

### Response
#### Success (200)
```json
{
  "users": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "phone": "1234567890",
      "created_at": "2023-01-01T12:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 20,
  "total_pages": 5
}
```

#### Error (400)
```json
{
  "detail": "Invalid page number."
}
```

---

## My Transactions Endpoint

### Endpoint
`GET /transactions/my-transactions`

### Description
Retrieve a list of transactions for the current authenticated user with pagination.

### Parameters
| Name     | Type | Required | Description                                      |
|----------|------|----------|--------------------------------------------------|
| `limit`  | int  | No       | The number of transactions to retrieve (default: 20). |
| `offset` | int  | No       | The offset for pagination (default: 0).         |

### Response
#### Success (200)
```json
[
  {
    "id": 1,
    "type": "deposit",
    "amount": 100.0,
    "status": "completed",
    "created_at": "2023-01-01T12:00:00Z",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com"
    }
  }
]
```

#### Error (404)
```json
{
  "detail": "No transactions found."
}
```

---

## Admin Transactions Endpoint

### Endpoint
`GET /admin/transactions`

### Description
Retrieve all transactions for admin with pagination. Supports filtering by status and type.

### Parameters
| Name     | Type   | Required | Description                                      |
|----------|--------|----------|--------------------------------------------------|
| `page`   | int    | No       | The page number to retrieve (default: 1).       |
| `limit`  | int    | No       | The number of transactions per page (default: 20). |
| `status` | string | No       | Filter transactions by status (e.g., `pending`, `completed`, `rejected`). |
| `type`   | string | No       | Filter transactions by type (e.g., `deposit`, `withdrawal`). |

### Response
#### Success (200)
```json
{
  "transactions": [
    {
      "id": 1,
      "type": "deposit",
      "amount": 100.0,
      "status": "completed",
      "crypto_network": "TRC20",
      "crypto_amount": "95.00",
      "created_at": "2023-01-01T12:00:00Z",
      "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "phone": "1234567890"
      }
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 20,
  "total_pages": 3
}
```

#### Error (400)
```json
{
  "detail": "Invalid parameters."
}
```

