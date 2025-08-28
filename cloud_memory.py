import os
import re
import json
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class CloudMemory:
    def __init__(self, auth_system):
        self.auth_system = auth_system
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        self.enabled = bool(self.supabase_url and self.supabase_key)
        self.supabase = None
        self.local_storage_dir = "local_storage_backup"
        
        os.makedirs(self.local_storage_dir, exist_ok=True)
        
        if self.enabled:
            try:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
                print("✅ Connected to Supabase successfully!")
                self._initialize_tables()
            except Exception as e:
                print(f"❌ Supabase connection failed: {e}")
                self.enabled = False
        else:
            print("⚠️  Supabase credentials not found. Using local storage only.")
    
    def _initialize_tables(self):
        """Initialize database tables if they don't exist"""
        if not self.enabled:
            return
            
        try:
            # Check if memories table exists, create if not
            # Note: In production, you should create these tables through Supabase dashboard
            # This is just for development convenience.... HAHA!!!!
            pass
        except Exception as e:
            print(f"Warning: Could not initialize tables: {e}")
    
    def _get_user_prefix(self):
        """Get user-specific prefix for data isolation"""
        if self.auth_system.is_authenticated():
            return f"user_{self.auth_system.get_user_id()}"
        return "anonymous"
    
    def store_memory(self, memory_type, data, importance_score=5):
        """Store any type of memory with user isolation"""
        user_prefix = self._get_user_prefix()
        memory_key = f"{user_prefix}_{memory_type}"
        
        local_success = self._store_local(memory_key, data)
        
        if not self.enabled or not self.auth_system.is_authenticated() or importance_score < 3:
            return local_success
        
        try:
            # Prepare data for Supabase with user reference
            supabase_data = {
                "type": memory_type,
                "data": data,
                "importance_score": importance_score,
                "created_at": datetime.now().isoformat(),
                "game_day": data.get('day', 1) if isinstance(data, dict) else 1,
                "user_id": self.auth_system.get_user_id() if self.auth_system.is_authenticated() else None
            }
            
            # Insert into Supabase
            response = self.supabase.table("memories").insert(supabase_data).execute()
            
            if hasattr(response, 'data') and response.data:
                print(f"✅ Your {memory_type} is stored in cloud, life paused to continue again.") # 
                return True
            else:
                raise Exception("No data returned from Supabase")
                
        except Exception as e:
            print(f"❌ Failed to store {memory_type} in cloud: {e}, using local backup")
            return local_success
    
    def get_memories(self, memory_type=None, limit=50, min_importance=0):
        """Retrieve user-specific memories"""
        user_prefix = self._get_user_prefix()
        
        if self.enabled and self.auth_system.is_authenticated():
            try:
                query = self.supabase.table("memories").select("*").eq(
                    "user_id", self.auth_system.get_user_id()
                )
                
                if memory_type:
                    query = query.eq("type", memory_type)
                
                if min_importance > 0:
                    query = query.gte("importance_score", min_importance)
                
                query = query.order("created_at", desc=True).limit(limit)
                response = query.execute()
                
                if hasattr(response, 'data'):
                    return response.data
                else:
                    raise Exception("No data returned from Supabase")
                    
            except Exception as e:
                print(f"❌ Failed to retrieve memories from cloud: {e}, using local backup")
        
        # Fallback to local storage with user prefix
        memory_key = f"{user_prefix}_{memory_type}" if memory_type else user_prefix
        return self._get_local_memories(memory_key, limit)
    
    def _store_local(self, memory_key, data):
        """Fallback to local storage with user-specific naming"""
        try:
            safe_name = re.sub(r'[^\w\s-]', '', memory_key.replace(' ', '_'))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.local_storage_dir}/{safe_name}_{timestamp}.json"
            
            serialized_data = self._make_json_serializable(data)
            
            with open(filename, 'w') as f:
                json.dump(serialized_data, f, indent=2)
            
            # print(f"💾 {memory_key} stored locally: {filename}")
            return True
        except Exception as e:
            print(f"❌ Local storage failed for {memory_key}: {e}")
            return False
    
    def _make_json_serializable(self, data):
        """Convert data to be JSON serializable"""
        if isinstance(data, dict):
            return {k: self._make_json_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._make_json_serializable(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        elif hasattr(data, '__dict__'):
            return self._make_json_serializable(data.__dict__)
        else:
            try:
                json.dumps(data)
                return data
            except:
                return str(data)
    
    def _get_local_memories(self, memory_key, limit=50):
        """Retrieve user-specific memories from local storage"""
        memories = []
        safe_prefix = re.sub(r'[^\w\s-]', '', memory_key.replace(' ', '_'))
        
        try:
            if not os.path.exists(self.local_storage_dir):
                return memories
                
            files = os.listdir(self.local_storage_dir)
            matching_files = []
            
            for filename in files:
                if filename.startswith(safe_prefix) and filename.endswith('.json'):
                    file_path = os.path.join(self.local_storage_dir, filename)
                    matching_files.append((file_path, os.path.getctime(file_path)))
            
            # Sort by creation time, newest first
            matching_files.sort(key=lambda x: x[1], reverse=True)
            
            for file_path, _ in matching_files[:limit]:
                try:
                    with open(file_path, 'r') as f:
                        memory_data = json.load(f)
                        memories.append({
                            "type": memory_key.split('_')[-1] if '_' in memory_key else memory_key,
                            "data": memory_data,
                            "created_at": os.path.getctime(file_path),
                            "importance_score": 3
                        })
                except Exception as e:
                    print(f"Failed to load local memory file {file_path}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Failed to retrieve local memories: {e}")
        
        return memories
    
    def is_connected(self):
        """Check if cloud storage is available"""
        return self.enabled and self.auth_system.is_authenticated()
    
    def sync_local_to_cloud(self):
        """Sync local memories to cloud when user signs in"""
        if not self.is_connected():
            return False
            
        try:
            local_memories = self._get_local_memories(self._get_user_prefix(), limit=100)
            synced_count = 0
            
            for memory in local_memories:
                try:
                    # Check if this memory already exists in cloud
                    existing = self.supabase.table("memories").select("id").eq(
                        "user_id", self.auth_system.get_user_id()
                    ).eq("type", memory["type"]).execute()
                    
                    # If not exists, sync it
                    if not (hasattr(existing, 'data') and existing.data):
                        supabase_data = {
                            "type": memory["type"],
                            "data": memory["data"],
                            "importance_score": memory["importance_score"],
                            "created_at": datetime.fromtimestamp(memory["created_at"]).isoformat(),
                            "user_id": self.auth_system.get_user_id()
                        }
                        
                        self.supabase.table("memories").insert(supabase_data).execute()
                        synced_count += 1
                        
                except Exception as e:
                    print(f"Failed to sync memory: {e}")
                    continue
            
            if synced_count > 0:
                print(f"Synced {synced_count} local memories to cloud")
            return True
            
        except Exception as e:
            print(f"Sync failed: {e}")
            return False