"""Tests for custom exceptions."""

import pytest

from mygh.exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    MyGHException,
    RateLimitError,
)


class TestMyGHException:
    """Test base MyGHException."""

    def test_base_exception(self):
        """Test base exception creation."""
        exc = MyGHException("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)

    def test_base_exception_inheritance(self):
        """Test that base exception is properly inherited."""
        exc = MyGHException("Test")
        assert isinstance(exc, MyGHException)
        assert isinstance(exc, Exception)


class TestAuthenticationError:
    """Test AuthenticationError."""

    def test_authentication_error(self):
        """Test authentication error creation."""
        exc = AuthenticationError("Invalid token")
        assert str(exc) == "Invalid token"
        assert isinstance(exc, AuthenticationError)
        assert isinstance(exc, MyGHException)

    def test_authentication_error_inheritance(self):
        """Test authentication error inheritance chain."""
        exc = AuthenticationError("Auth failed")
        assert isinstance(exc, AuthenticationError)
        assert isinstance(exc, MyGHException)
        assert isinstance(exc, Exception)


class TestAPIError:
    """Test APIError."""

    def test_api_error_basic(self):
        """Test basic API error creation."""
        exc = APIError("API request failed")
        assert str(exc) == "API request failed"
        assert isinstance(exc, APIError)
        assert isinstance(exc, MyGHException)
        assert exc.status_code is None

    def test_api_error_with_status_code(self):
        """Test API error with status code."""
        exc = APIError("Not found", status_code=404)
        assert str(exc) == "Not found"
        assert exc.status_code == 404
        assert isinstance(exc, APIError)
        assert isinstance(exc, MyGHException)

    def test_api_error_status_code_access(self):
        """Test accessing status code attribute."""
        exc = APIError("Server error", status_code=500)
        assert exc.status_code == 500

        exc_no_code = APIError("Generic error")
        assert exc_no_code.status_code is None

    def test_api_error_inheritance(self):
        """Test API error inheritance chain."""
        exc = APIError("API failed", status_code=400)
        assert isinstance(exc, APIError)
        assert isinstance(exc, MyGHException)
        assert isinstance(exc, Exception)


class TestRateLimitError:
    """Test RateLimitError."""

    def test_rate_limit_error(self):
        """Test rate limit error creation."""
        exc = RateLimitError("Rate limit exceeded")
        assert str(exc) == "Rate limit exceeded"
        assert isinstance(exc, RateLimitError)
        assert isinstance(exc, APIError)
        assert isinstance(exc, MyGHException)

    def test_rate_limit_error_with_status_code(self):
        """Test rate limit error with status code."""
        exc = RateLimitError("Rate limit exceeded", status_code=403)
        assert str(exc) == "Rate limit exceeded"
        assert exc.status_code == 403

    def test_rate_limit_error_inheritance(self):
        """Test rate limit error inheritance chain."""
        exc = RateLimitError("Too many requests")
        assert isinstance(exc, RateLimitError)
        assert isinstance(exc, APIError)
        assert isinstance(exc, MyGHException)
        assert isinstance(exc, Exception)


class TestConfigurationError:
    """Test ConfigurationError."""

    def test_configuration_error(self):
        """Test configuration error creation."""
        exc = ConfigurationError("Invalid configuration")
        assert str(exc) == "Invalid configuration"
        assert isinstance(exc, ConfigurationError)
        assert isinstance(exc, MyGHException)

    def test_configuration_error_inheritance(self):
        """Test configuration error inheritance chain."""
        exc = ConfigurationError("Config invalid")
        assert isinstance(exc, ConfigurationError)
        assert isinstance(exc, MyGHException)
        assert isinstance(exc, Exception)


class TestExceptionHierarchy:
    """Test exception hierarchy and relationships."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from MyGHException."""
        exceptions = [
            AuthenticationError("test"),
            APIError("test"),
            RateLimitError("test"),
            ConfigurationError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, MyGHException)
            assert isinstance(exc, Exception)

    def test_api_error_subclasses(self):
        """Test that API error subclasses work correctly."""
        rate_limit_exc = RateLimitError("Rate limit")

        # Should be catchable as APIError
        assert isinstance(rate_limit_exc, APIError)
        assert isinstance(rate_limit_exc, MyGHException)

    def test_exception_catching_hierarchy(self):
        """Test exception catching with inheritance hierarchy."""
        # Should be able to catch RateLimitError as APIError
        try:
            raise RateLimitError("Rate limit exceeded")
        except APIError as e:
            assert isinstance(e, RateLimitError)
            assert str(e) == "Rate limit exceeded"
        except Exception:
            pytest.fail("Should have been caught as APIError")

        # Should be able to catch any custom exception as MyGHException
        custom_exceptions = [
            AuthenticationError("auth"),
            APIError("api"),
            RateLimitError("rate"),
            ConfigurationError("config"),
        ]

        for exc in custom_exceptions:
            try:
                raise exc
            except MyGHException as e:
                assert isinstance(e, type(exc))
            except Exception:
                pytest.fail(f"Should have been caught as MyGHException: {type(exc)}")

    def test_exception_message_preservation(self):
        """Test that exception messages are preserved through inheritance."""
        message = "This is a test error message"

        exceptions = [
            MyGHException(message),
            AuthenticationError(message),
            APIError(message),
            RateLimitError(message),
            ConfigurationError(message),
        ]

        for exc in exceptions:
            assert str(exc) == message

    def test_api_error_status_code_in_subclasses(self):
        """Test that status code functionality works in API error subclasses."""
        rate_limit_exc = RateLimitError("Rate limit", status_code=429)
        assert rate_limit_exc.status_code == 429

        api_exc = APIError("Generic API error", status_code=500)
        assert api_exc.status_code == 500

    def test_exception_attributes_preservation(self):
        """Test that exception attributes are preserved."""
        # Test APIError with status code
        api_exc = APIError("Server error", status_code=500)

        try:
            raise api_exc
        except APIError as caught:
            assert caught.status_code == 500
            assert str(caught) == "Server error"

        # Test RateLimitError with status code (inherited from APIError)
        rate_exc = RateLimitError("Too many requests", status_code=429)

        try:
            raise rate_exc
        except RateLimitError as caught:
            assert caught.status_code == 429
            assert str(caught) == "Too many requests"

    def test_raising_and_catching_patterns(self):
        """Test common patterns of raising and catching exceptions."""
        # Pattern 1: Catch specific exception type
        with pytest.raises(AuthenticationError):
            raise AuthenticationError("Invalid credentials")

        # Pattern 2: Catch parent class
        with pytest.raises(APIError):
            raise RateLimitError("Rate limit exceeded")

        # Pattern 3: Catch base custom exception
        with pytest.raises(MyGHException):
            raise ConfigurationError("Invalid config")

        # Pattern 4: Check exception attributes
        with pytest.raises(APIError) as exc_info:
            raise APIError("Not found", status_code=404)

        assert exc_info.value.status_code == 404

    def test_exception_chaining(self):
        """Test exception chaining and cause preservation."""
        original_error = ValueError("Original error")

        try:
            raise original_error
        except ValueError as e:
            # Chain the exception
            new_error = APIError(f"API error caused by: {e}")
            new_error.__cause__ = e

            try:
                raise new_error
            except APIError as api_err:
                assert str(api_err) == "API error caused by: Original error"
                assert api_err.__cause__ is original_error

    def test_empty_message_handling(self):
        """Test exception creation with empty messages."""
        exceptions = [
            MyGHException(""),
            AuthenticationError(""),
            APIError(""),
            RateLimitError(""),
            ConfigurationError(""),
        ]

        for exc in exceptions:
            # Should not raise an error
            assert str(exc) == ""
            assert isinstance(exc, MyGHException)
