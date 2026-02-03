"""Unit tests for password hashing and verification."""
import pytest
from src.core.auth import hash_password, verify_password


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "testpassword123"
        result = hash_password(password)
        assert isinstance(result, str)

    def test_hash_password_creates_unique_hashes(self):
        """Test that same password creates different hashes (due to salt)."""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test that correct password verifies successfully."""
        password = "testpassword123"
        password_hash = hash_password(password)
        assert verify_password(password, password_hash) is True

    def test_verify_password_incorrect(self):
        """Test that incorrect password fails verification."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        password_hash = hash_password(password)
        assert verify_password(wrong_password, password_hash) is False

    def test_verify_password_with_custom_rounds(self):
        """Test password hashing with custom bcrypt rounds."""
        password = "testpassword123"
        rounds = 10
        password_hash = hash_password(password, rounds=rounds)
        assert verify_password(password, password_hash) is True

    def test_hash_password_minimum_length(self):
        """Test hashing works with minimum length password."""
        password = "a" * 1
        result = hash_password(password)
        assert verify_password(password, result) is True

    def test_hash_password_special_characters(self):
        """Test hashing works with special characters."""
        password = "p@ss!word#123$%"
        result = hash_password(password)
        assert verify_password(password, result) is True

    def test_hash_password_unicode(self):
        """Test hashing works with unicode characters."""
        password = "пароль密码🔐"
        result = hash_password(password)
        assert verify_password(password, result) is True
