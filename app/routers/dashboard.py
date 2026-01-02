from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.core.security import get_current_admin
from app.services.notification_service import notification_service

router = APIRouter()

@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """WebSocket for real-time notifications."""
    await notification_service.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        notification_service.disconnect(websocket)

@router.get("/dashboard/stats")
def get_dashboard_stats(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get overall dashboard statistics."""
    # User stats
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    
    # Transaction stats
    total_transactions = db.query(func.count(Transaction.id)).scalar()
    pending_transactions = db.query(func.count(Transaction.id)).filter(Transaction.status == 'pending').scalar()
    completed_transactions = db.query(func.count(Transaction.id)).filter(Transaction.status == 'completed').scalar()
    
    # Volume stats
    total_deposit_volume = db.query(func.sum(Transaction.net_inr_amount)).filter(
        Transaction.type == 'crypto_deposit', Transaction.status == 'approved'
    ).scalar() or 0
    
    total_withdrawal_volume = db.query(func.sum(Transaction.gross_inr_amount)).filter(
        Transaction.type == 'withdrawal', Transaction.status == 'completed'
    ).scalar() or 0
    
    # Revenue stats (platform fees)
    total_platform_fees = db.query(func.sum(Transaction.platform_fee_amount)).filter(
        Transaction.status.in_(['approved', 'completed'])
    ).scalar() or 0
    
    return {
        "users": {
            "total": total_users,
            "active": active_users
        },
        "transactions": {
            "total": total_transactions,
            "pending": pending_transactions,
            "completed": completed_transactions
        },
        "volume": {
            "deposits": float(total_deposit_volume),
            "withdrawals": float(total_withdrawal_volume),
            "net": float(total_deposit_volume - total_withdrawal_volume)
        },
        "revenue": {
            "platform_fees": float(total_platform_fees)
        }
    }

@router.get("/dashboard/transactions-chart")
def get_transactions_chart(
    days: int = 30,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get transaction data for charts (last N days)."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Daily transaction counts
    daily_transactions = db.query(
        func.date(Transaction.created_at).label('date'),
        func.count(Transaction.id).label('count')
    ).filter(
        Transaction.created_at >= start_date
    ).group_by(func.date(Transaction.created_at)).all()
    
    # Transaction types breakdown
    type_breakdown = db.query(
        Transaction.type,
        func.count(Transaction.id)
    ).filter(
        Transaction.created_at >= start_date
    ).group_by(Transaction.type).all()
    
    # Status breakdown
    status_breakdown = db.query(
        Transaction.status,
        func.count(Transaction.id)
    ).filter(
        Transaction.created_at >= start_date
    ).group_by(Transaction.status).all()
    
    return {
        "daily_transactions": [
            {"date": str(item.date), "count": item.count}
            for item in daily_transactions
        ],
        "type_breakdown": [
            {"type": item.type, "count": item[1]}
            for item in type_breakdown
        ],
        "status_breakdown": [
            {"status": item.status, "count": item[1]}
            for item in status_breakdown
        ]
    }

@router.get("/dashboard/users-chart")
def get_users_chart(
    days: int = 30,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get user registration data for charts."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Daily user registrations
    daily_users = db.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(
        User.created_at >= start_date
    ).group_by(func.date(User.created_at)).all()
    
    # Cumulative users
    cumulative_users = []
    total = 0
    for item in daily_users:
        total += item.count
        cumulative_users.append({
            "date": str(item.date),
            "cumulative": total
        })
    
    return {
        "daily_registrations": [
            {"date": str(item.date), "count": item.count}
            for item in daily_users
        ],
        "cumulative_users": cumulative_users
    }

@router.get("/dashboard/revenue-chart")
def get_revenue_chart(
    days: int = 30,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get revenue data for charts."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Daily platform fees
    daily_fees = db.query(
        func.date(Transaction.created_at).label('date'),
        func.sum(Transaction.platform_fee_amount).label('fees')
    ).filter(
        Transaction.created_at >= start_date,
        Transaction.status.in_(['approved', 'completed']),
        Transaction.platform_fee_amount > 0
    ).group_by(func.date(Transaction.created_at)).all()
    
    return {
        "daily_fees": [
            {"date": str(item.date), "fees": float(item.fees or 0)}
            for item in daily_fees
        ]
    }

@router.get("/dashboard/recent-activity")
def get_recent_activity(
    limit: int = 10,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get recent transaction activity."""
    recent_transactions = db.query(Transaction).order_by(Transaction.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": t.id,
            "transaction_uid": t.transaction_uid,
            "type": t.type,
            "status": t.status,
            "amount": float(t.net_inr_amount or t.gross_inr_amount or 0),
            "user_id": t.user_id,
            "created_at": t.created_at
        }
        for t in recent_transactions
    ]
