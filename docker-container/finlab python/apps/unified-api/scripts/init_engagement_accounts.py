"""
Initialize Engagement Bot Accounts
Inserts 20 bot accounts into the engagement_accounts table
"""
import os
import sys
import psycopg2
from cryptography.fernet import Fernet
import base64
import hashlib

# Generate encryption key from a secret (should be in environment variable)
def get_encryption_key():
    """Generate Fernet key from environment secret"""
    secret = os.getenv('ENGAGEMENT_BOT_SECRET', 'cmoney-engagement-bot-secret-key-2025')
    # Create a valid Fernet key from secret
    key = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(key)

def encrypt_password(password: str) -> str:
    """Encrypt password using Fernet symmetric encryption"""
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(password.encode())
    return encrypted.decode()

def decrypt_password(encrypted_password: str) -> str:
    """Decrypt password"""
    f = Fernet(get_encryption_key())
    decrypted = f.decrypt(encrypted_password.encode())
    return decrypted.decode()

# Bot accounts data
BOT_ACCOUNTS = [
    {"email": "forum_150@cmoney.com.tw", "password": "p4F2rD5k", "nickname": "投資小白150"},
    {"email": "forum_151@cmoney.com.tw", "password": "K7w8dI2n", "nickname": "股市觀察151"},
    {"email": "forum_152@cmoney.com.tw", "password": "u5H7rP1m", "nickname": "理財達人152"},
    {"email": "forum_153@cmoney.com.tw", "password": "O2q6kF1x", "nickname": "投資筆記153"},
    {"email": "forum_154@cmoney.com.tw", "password": "m4A9lT1u", "nickname": "股市新手154"},
    {"email": "forum_155@cmoney.com.tw", "password": "Z3w7uL5f", "nickname": "財經關注155"},
    {"email": "forum_156@cmoney.com.tw", "password": "V9p1xT5c", "nickname": "市場分析156"},
    {"email": "forum_157@cmoney.com.tw", "password": "c4J9vF8r", "nickname": "投資學習157"},
    {"email": "forum_158@cmoney.com.tw", "password": "T7r3oF8t", "nickname": "股票研究158"},
    {"email": "forum_159@cmoney.com.tw", "password": "N5m7hZ4r", "nickname": "理財規劃159"},
    {"email": "forum_180@cmoney.com.tw", "password": "e5X3qK4n", "nickname": "投資追蹤180"},
    {"email": "forum_181@cmoney.com.tw", "password": "u1N8wA6t", "nickname": "股市記錄181"},
    {"email": "forum_182@cmoney.com.tw", "password": "G2p8xJ7k", "nickname": "財經筆記182"},
    {"email": "forum_183@cmoney.com.tw", "password": "v3A5dN9r", "nickname": "投資觀點183"},
    {"email": "forum_184@cmoney.com.tw", "password": "Q6u2pZ7n", "nickname": "市場觀察184"},
    {"email": "forum_185@cmoney.com.tw", "password": "M9h2kU8r", "nickname": "股票學習185"},
    {"email": "forum_186@cmoney.com.tw", "password": "t7L9uY0f", "nickname": "投資心得186"},
    {"email": "forum_187@cmoney.com.tw", "password": "a4E9jV8t", "nickname": "理財心得187"},
    {"email": "forum_188@cmoney.com.tw", "password": "z6G5wN2m", "nickname": "股市分享188"},
    {"email": "forum_189@cmoney.com.tw", "password": "c8L5nO3q", "nickname": "投資分享189"},
]

def init_accounts():
    """Initialize bot accounts in database"""
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable not set")
        sys.exit(1)

    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        print("🔄 Inserting bot accounts into database...")
        print(f"📊 Total accounts to insert: {len(BOT_ACCOUNTS)}")

        inserted_count = 0
        updated_count = 0

        for account in BOT_ACCOUNTS:
            email = account['email']
            password = account['password']
            nickname = account['nickname']

            # Encrypt password
            encrypted_pwd = encrypt_password(password)

            # Check if account already exists
            cur.execute(
                "SELECT account_id FROM engagement_accounts WHERE email = %s",
                (email,)
            )
            existing = cur.fetchone()

            if existing:
                # Update existing account
                cur.execute("""
                    UPDATE engagement_accounts
                    SET encrypted_password = %s,
                        nickname = %s,
                        status = 'active',
                        updated_at = NOW()
                    WHERE email = %s
                """, (encrypted_pwd, nickname, email))
                updated_count += 1
                print(f"   ✏️  Updated: {email} ({nickname})")
            else:
                # Insert new account
                cur.execute("""
                    INSERT INTO engagement_accounts (email, encrypted_password, nickname, status)
                    VALUES (%s, %s, %s, 'active')
                """, (email, encrypted_pwd, nickname))
                inserted_count += 1
                print(f"   ✅ Inserted: {email} ({nickname})")

        # Commit changes
        conn.commit()

        print(f"\n✅ Successfully initialized bot accounts!")
        print(f"   📥 Inserted: {inserted_count} accounts")
        print(f"   📝 Updated: {updated_count} accounts")
        print(f"   📊 Total: {inserted_count + updated_count} accounts")

        # Show summary
        cur.execute("SELECT COUNT(*) FROM engagement_accounts WHERE status = 'active'")
        active_count = cur.fetchone()[0]
        print(f"\n📈 Active bot accounts in database: {active_count}")

        # Close connection
        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Error initializing accounts: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_encryption():
    """Test encryption/decryption"""
    print("\n🔐 Testing encryption...")
    test_password = "test123"
    encrypted = encrypt_password(test_password)
    decrypted = decrypt_password(encrypted)

    print(f"   Original: {test_password}")
    print(f"   Encrypted: {encrypted[:50]}...")
    print(f"   Decrypted: {decrypted}")
    print(f"   ✅ Match: {test_password == decrypted}")

if __name__ == "__main__":
    print("=" * 60)
    print("Engagement Bot Account Initialization")
    print("=" * 60)

    # Test encryption first
    test_encryption()

    # Initialize accounts
    print()
    success = init_accounts()

    if success:
        print("\n" + "=" * 60)
        print("✅ Initialization completed successfully!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Initialization failed!")
        print("=" * 60)
        sys.exit(1)
