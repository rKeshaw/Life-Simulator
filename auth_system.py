# auth_system.py
import os
import jwt
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class AuthSystem:
    def __init__(self):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.current_user = None
        self.session = None
    
    def sign_up(self, email, password, username):
        """Register a new user"""
        try:
            # Create user in Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
            })
            
            if auth_response.user:
                # Create user profile in database
                profile_data = {
                    "user_id": auth_response.user.id,
                    "username": username,
                    "created_at": datetime.now().isoformat(),
                    "last_login": datetime.now().isoformat()
                }
                
                response = self.supabase.table("user_profiles").insert(profile_data).execute()
                
                if response.data:
                    print("✅ Account created successfully!")
                    return True
                
            return False
            
        except Exception as e:
            print(f"❌ Sign up failed: {e}")
            return False
    
    def sign_in(self, email, password):
        """Authenticate a user"""
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                self.current_user = auth_response.user
                self.session = auth_response.session
                
                # Update last login
                self.supabase.table("user_profiles").update({
                    "last_login": datetime.now().isoformat()
                }).eq("user_id", self.current_user.id).execute()
                
                print(f"✅ Welcome back, {self.current_user.email}!")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Sign in failed: {e}")
            return False
    
    def sign_out(self):
        """Sign out current user"""
        try:
            self.supabase.auth.sign_out()
            self.current_user = None
            self.session = None
            print("✅ Signed out successfully")
        except Exception as e:
            print(f"❌ Sign out failed: {e}")
    
    def get_user_id(self):
        """Get current user's ID"""
        return self.current_user.id if self.current_user else None
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.current_user is not None
    
    def get_user_profile(self):
        """Get user's profile data"""
        if not self.current_user:
            return None
        
        try:
            response = self.supabase.table("user_profiles").select("*").eq(
                "user_id", self.current_user.id
            ).execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"❌ Failed to get user profile: {e}")
            return None