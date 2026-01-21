"""Test script to troubleshoot bcrypt issue."""

try:
    import bcrypt
    print("bcrypt imported successfully")
    print(f"bcrypt version: {getattr(bcrypt, '__version__', 'unknown')}")

    # Test basic bcrypt functionality
    password = "password123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    print("bcrypt hash successful")

    # Verify
    verified = bcrypt.checkpw(password.encode('utf-8'), hashed)
    print(f"bcrypt verify successful: {verified}")

except Exception as e:
    print(f"Error with bcrypt: {e}")
    import traceback
    traceback.print_exc()

try:
    from passlib.context import CryptContext
    from passlib.exc import MissingBackendError

    # Try to create context and force backend
    pwd_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
        bcrypt__rounds=12
    )

    # Try to hash a password
    password = "password123"
    hash_result = pwd_context.hash(password)
    print("Passlib hash successful")

    # Verify
    verify_result = pwd_context.verify(password, hash_result)
    print(f"Passlib verify successful: {verify_result}")

except Exception as e:
    print(f"Error with passlib: {e}")
    import traceback
    traceback.print_exc()