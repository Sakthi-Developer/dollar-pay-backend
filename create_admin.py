#!/usr/bin/env python3
"""
Script to create initial super admin user.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import get_db_context
from app.db.models import Admin
from app.routers.auth import hash_password

def create_super_admin():
    """Create initial super admin user."""
    if len(sys.argv) != 4:
        print("Usage: python create_admin.py <username> <email> <password>")
        return
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    with get_db_context() as db:
        # Check if any admin exists
        existing_admin = db.query(Admin).first()
        if existing_admin:
            print("Admin already exists. Use the registration endpoint for new admins.")
            return
        
        password_hash = hash_password(password)
        
        super_admin = Admin(
            username=username,
            email=email,
            password_hash=password_hash,
            role="super_admin"
        )
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        print(f"Super admin '{username}' created successfully!")
        print(f"ID: {super_admin.id}")
        print(f"Role: {super_admin.role}")

if __name__ == "__main__":
    create_super_admin()