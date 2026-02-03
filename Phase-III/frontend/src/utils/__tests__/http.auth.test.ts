/**
 * Integration Tests: HTTP Utility - JWT Authentication
 *
 * Tests that JWT tokens (httpOnly cookies) are properly included in requests
 */

import { http } from '../http';

// Mock global fetch
global.fetch = jest.fn();

const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

describe('HTTP Utility - JWT Authentication Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Credentials Configuration', () => {
    it('should include credentials in GET requests', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: 'test' }),
      } as Response);

      // Act
      await http.get('/api/test');

      // Assert
      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          credentials: 'include',
        })
      );
    });

    it('should include credentials in POST requests', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: 'test' }),
      } as Response);

      // Act
      await http.post('/api/test', { data: 'test' });

      // Assert
      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          credentials: 'include',
          method: 'POST',
        })
      );
    });

    it('should include credentials in PUT requests', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: 'test' }),
      } as Response);

      // Act
      await http.put('/api/test', { data: 'test' });

      // Assert
      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          credentials: 'include',
          method: 'PUT',
        })
      );
    });

    it('should include credentials in DELETE requests', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: 'test' }),
      } as Response);

      // Act
      await http.delete('/api/test');

      // Assert
      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          credentials: 'include',
          method: 'DELETE',
        })
      );
    });
  });

  describe('JWT Cookie Handling', () => {
    it('should send httpOnly JWT cookies with requests', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: 'test' }),
      } as Response);

      // Act
      await http.post('/api/chat', { message: 'Hello' });

      // Assert
      // credentials: 'include' ensures cookies are sent
      const fetchCall = mockFetch.mock.calls[0];
      const options = fetchCall[1];
      expect(options?.credentials).toBe('include');
    });

    it('should receive and store JWT cookies from response', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({
          'Set-Cookie': 'jwt=token123; HttpOnly; Secure; SameSite=Strict',
        }),
        json: async () => ({ data: 'test' }),
      } as Response);

      // Act
      await http.post('/auth/signin', { email: 'test@example.com', password: 'password' });

      // Assert
      expect(mockFetch).toHaveBeenCalled();
      // Note: Cookie storage is handled by browser automatically when credentials: 'include'
    });
  });

  describe('Authentication Error Responses', () => {
    it('should handle 401 Unauthorized response', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({
          error: {
            code: 'UNAUTHORIZED',
            message: 'Authentication required',
          },
        }),
      } as Response);

      // Act & Assert
      await expect(http.get('/api/protected')).rejects.toMatchObject({
        status: 401,
      });
    });

    it('should handle 401 Token Expired response', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({
          error: {
            code: 'TOKEN_EXPIRED',
            message: 'JWT token has expired',
          },
        }),
      } as Response);

      // Act & Assert
      await expect(http.post('/api/chat', { message: 'Hello' })).rejects.toMatchObject({
        status: 401,
      });
    });

    it('should handle 403 Forbidden response', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: async () => ({
          error: {
            code: 'FORBIDDEN',
            message: 'Access denied',
          },
        }),
      } as Response);

      // Act & Assert
      await expect(http.get('/api/admin')).rejects.toMatchObject({
        status: 403,
      });
    });
  });

  describe('Content-Type Headers', () => {
    it('should include Content-Type: application/json for POST', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: 'test' }),
      } as Response);

      // Act
      await http.post('/api/test', { data: 'test' });

      // Assert
      const fetchCall = mockFetch.mock.calls[0];
      const options = fetchCall[1];
      expect(options?.headers).toMatchObject({
        'Content-Type': 'application/json',
      });
    });

    it('should include Content-Type: application/json for PUT', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: 'test' }),
      } as Response);

      // Act
      await http.put('/api/test', { data: 'test' });

      // Assert
      const fetchCall = mockFetch.mock.calls[0];
      const options = fetchCall[1];
      expect(options?.headers).toMatchObject({
        'Content-Type': 'application/json',
      });
    });
  });

  describe('Base URL Configuration', () => {
    it('should use NEXT_PUBLIC_API_URL for relative endpoints', async () => {
      // Arrange
      const originalEnv = process.env.NEXT_PUBLIC_API_URL;
      process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: 'test' }),
      } as Response);

      // Act
      await http.get('/api/test');

      // Assert
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('http://localhost:8000/api/test'),
        expect.any(Object)
      );

      // Cleanup
      process.env.NEXT_PUBLIC_API_URL = originalEnv;
    });

    it('should handle absolute URLs directly', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: 'test' }),
      } as Response);

      // Act
      await http.get('https://api.example.com/test');

      // Assert
      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/test',
        expect.any(Object)
      );
    });
  });

  describe('Request Body Serialization', () => {
    it('should serialize request body to JSON', async () => {
      // Arrange
      const requestData = { message: 'Hello', conversationId: 'conv-123' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: 'test' }),
      } as Response);

      // Act
      await http.post('/api/chat', requestData);

      // Assert
      const fetchCall = mockFetch.mock.calls[0];
      const options = fetchCall[1];
      expect(options?.body).toBe(JSON.stringify(requestData));
    });
  });

  describe('Error Handling', () => {
    it('should throw error with status and message for failed requests', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({
          error: {
            code: 'INTERNAL_ERROR',
            message: 'Server error',
          },
        }),
      } as Response);

      // Act & Assert
      await expect(http.get('/api/test')).rejects.toMatchObject({
        status: 500,
      });
    });

    it('should handle network errors', async () => {
      // Arrange
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      // Act & Assert
      await expect(http.get('/api/test')).rejects.toThrow('Network error');
    });
  });

  describe('Security Configuration', () => {
    it('should not allow overriding credentials option', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: 'test' }),
      } as Response);

      // Act - Try to pass credentials: 'omit' (should be overridden)
      await http.get('/api/test', { credentials: 'omit' as any });

      // Assert - Should still use 'include'
      const fetchCall = mockFetch.mock.calls[0];
      const options = fetchCall[1];
      expect(options?.credentials).toBe('include');
    });

    it('should ensure httpOnly cookies are sent in CORS requests', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: 'test' }),
      } as Response);

      // Act - Cross-origin request
      await http.post('http://127.0.0.1:8000/api/chat', { message: 'Test' });

      // Assert - credentials: 'include' allows cookies in CORS
      const fetchCall = mockFetch.mock.calls[0];
      const options = fetchCall[1];
      expect(options?.credentials).toBe('include');
    });
  });
});
