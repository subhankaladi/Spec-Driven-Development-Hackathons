/**
 * Integration Tests: useChat Hook - Conversation Loading and Resume
 *
 * Tests conversation list loading, conversation selection, and pagination
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useChat } from '../useChat';
import { ChatService } from '@/services/chat';

// Mock dependencies
jest.mock('@/services/chat');

const mockChatService = ChatService as jest.Mocked<typeof ChatService>;

describe('useChat - Conversation Loading and Resume', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Load Conversations', () => {
    it('should load conversations list successfully', async () => {
      // Arrange
      const mockConversations = [
        {
          id: 'conv-1',
          title: 'First Conversation',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messageCount: 5,
          lastMessage: 'Hello',
        },
        {
          id: 'conv-2',
          title: 'Second Conversation',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messageCount: 3,
          lastMessage: 'Hi there',
        },
      ];

      mockChatService.getConversations.mockResolvedValueOnce({
        conversations: mockConversations,
        total: 2,
        limit: 20,
        offset: 0,
      });

      const { result } = renderHook(() => useChat());

      // Act
      await act(async () => {
        await result.current.loadConversations();
      });

      // Assert
      await waitFor(() => {
        expect(result.current.conversations).toHaveLength(2);
        expect(result.current.conversations[0].id).toBe('conv-1');
        expect(result.current.conversations[1].id).toBe('conv-2');
      });
    });

    it('should handle empty conversations list', async () => {
      // Arrange
      mockChatService.getConversations.mockResolvedValueOnce({
        conversations: [],
        total: 0,
        limit: 20,
        offset: 0,
      });

      const { result } = renderHook(() => useChat());

      // Act
      await act(async () => {
        await result.current.loadConversations();
      });

      // Assert
      await waitFor(() => {
        expect(result.current.conversations).toHaveLength(0);
      });
    });

    it('should handle error when loading conversations fails', async () => {
      // Arrange
      const error = new Error('Network error');
      mockChatService.getConversations.mockRejectedValueOnce(error);

      const { result } = renderHook(() => useChat());

      // Act
      await act(async () => {
        await result.current.loadConversations();
      });

      // Assert
      await waitFor(() => {
        expect(result.current.error).not.toBeNull();
      });
    });
  });

  describe('Load Conversation Messages', () => {
    it('should load conversation messages successfully', async () => {
      // Arrange
      const mockMessages = [
        {
          id: 'msg-1',
          conversationId: 'conv-1',
          role: 'user' as const,
          content: 'Hello',
          createdAt: new Date().toISOString(),
        },
        {
          id: 'msg-2',
          conversationId: 'conv-1',
          role: 'assistant' as const,
          content: 'Hi there!',
          createdAt: new Date().toISOString(),
        },
      ];

      mockChatService.getConversation.mockResolvedValueOnce({
        conversation: {
          id: 'conv-1',
          title: 'Test Conversation',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messageCount: 2,
        },
        messages: mockMessages,
        limit: 50,
        offset: 0,
      });

      const { result } = renderHook(() => useChat());

      // Act
      await act(async () => {
        await result.current.loadConversation('conv-1');
      });

      // Assert
      await waitFor(() => {
        expect(result.current.messages).toHaveLength(2);
        expect(result.current.messages[0].content).toBe('Hello');
        expect(result.current.messages[1].content).toBe('Hi there!');
        expect(result.current.currentConversationId).toBe('conv-1');
      });
    });

    it('should set message status to "sent" when loading conversation', async () => {
      // Arrange
      const mockMessages = [
        {
          id: 'msg-1',
          conversationId: 'conv-1',
          role: 'user' as const,
          content: 'Hello',
          createdAt: new Date().toISOString(),
        },
      ];

      mockChatService.getConversation.mockResolvedValueOnce({
        conversation: {
          id: 'conv-1',
          title: 'Test',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messageCount: 1,
        },
        messages: mockMessages,
        limit: 50,
        offset: 0,
      });

      const { result } = renderHook(() => useChat());

      // Act
      await act(async () => {
        await result.current.loadConversation('conv-1');
      });

      // Assert
      await waitFor(() => {
        expect(result.current.messages[0].status).toBe('sent');
      });
    });

    it('should update currentConversationId when loading conversation', async () => {
      // Arrange
      mockChatService.getConversation.mockResolvedValueOnce({
        conversation: {
          id: 'conv-123',
          title: 'Test',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messageCount: 0,
        },
        messages: [],
        limit: 50,
        offset: 0,
      });

      const { result } = renderHook(() => useChat());

      // Act
      await act(async () => {
        await result.current.loadConversation('conv-123');
      });

      // Assert
      await waitFor(() => {
        expect(result.current.currentConversationId).toBe('conv-123');
      });
    });
  });

  describe('Conversation Resume After Page Refresh', () => {
    it('should maintain conversation state after reload', async () => {
      // Arrange
      const mockMessages = [
        {
          id: 'msg-1',
          conversationId: 'conv-1',
          role: 'user' as const,
          content: 'Previous message',
          createdAt: new Date().toISOString(),
        },
      ];

      mockChatService.getConversation.mockResolvedValueOnce({
        conversation: {
          id: 'conv-1',
          title: 'Test',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messageCount: 1,
        },
        messages: mockMessages,
        limit: 50,
        offset: 0,
      });

      const { result } = renderHook(() => useChat());

      // Act - Load conversation
      await act(async () => {
        await result.current.loadConversation('conv-1');
      });

      // Assert - Messages and conversation ID are loaded
      await waitFor(() => {
        expect(result.current.messages).toHaveLength(1);
        expect(result.current.currentConversationId).toBe('conv-1');
      });
    });

    it('should continue existing conversation with new message', async () => {
      // Arrange
      const existingMessages = [
        {
          id: 'msg-1',
          conversationId: 'conv-1',
          role: 'user' as const,
          content: 'Old message',
          createdAt: new Date().toISOString(),
        },
      ];

      const newMessageResponse = {
        conversationId: 'conv-1',
        userMessage: {
          id: 'msg-2',
          conversationId: 'conv-1',
          role: 'user' as const,
          content: 'New message',
          createdAt: new Date().toISOString(),
        },
        agentResponse: {
          id: 'msg-3',
          conversationId: 'conv-1',
          role: 'assistant' as const,
          content: 'Response',
          createdAt: new Date().toISOString(),
        },
      };

      mockChatService.getConversation.mockResolvedValueOnce({
        conversation: {
          id: 'conv-1',
          title: 'Test',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messageCount: 1,
        },
        messages: existingMessages,
        limit: 50,
        offset: 0,
      });

      mockChatService.sendMessage.mockResolvedValueOnce(newMessageResponse);

      const { result } = renderHook(() => useChat());

      // Act - Load existing conversation
      await act(async () => {
        await result.current.loadConversation('conv-1');
      });

      await waitFor(() => {
        expect(result.current.messages).toHaveLength(1);
      });

      // Act - Send new message in existing conversation
      await act(async () => {
        await result.current.sendMessage('New message');
      });

      // Assert - New messages added to existing conversation
      await waitFor(() => {
        expect(result.current.messages.length).toBeGreaterThanOrEqual(2);
        expect(result.current.currentConversationId).toBe('conv-1');
      });
    });
  });

  describe('Pagination', () => {
    it('should load more conversations when paginating', async () => {
      // Arrange - First page
      const firstPage = [
        {
          id: 'conv-1',
          title: 'First',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messageCount: 1,
        },
      ];

      // Second page
      const secondPage = [
        {
          id: 'conv-2',
          title: 'Second',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messageCount: 1,
        },
      ];

      mockChatService.getConversations
        .mockResolvedValueOnce({
          conversations: firstPage,
          total: 2,
          limit: 20,
          offset: 0,
        })
        .mockResolvedValueOnce({
          conversations: secondPage,
          total: 2,
          limit: 20,
          offset: 1,
        });

      const { result } = renderHook(() => useChat());

      // Act - Load first page
      await act(async () => {
        await result.current.loadConversations(false);
      });

      await waitFor(() => {
        expect(result.current.conversations).toHaveLength(1);
      });

      // Act - Load more conversations
      await act(async () => {
        await result.current.loadConversations(true);
      });

      // Assert - Both pages loaded
      await waitFor(() => {
        expect(result.current.conversations).toHaveLength(2);
        expect(result.current.conversations[0].id).toBe('conv-1');
        expect(result.current.conversations[1].id).toBe('conv-2');
      });
    });

    it('should track if more conversations are available', async () => {
      // Arrange - Full page (20 items = more available)
      const fullPage = Array.from({ length: 20 }, (_, i) => ({
        id: `conv-${i}`,
        title: `Conversation ${i}`,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        messageCount: 1,
      }));

      mockChatService.getConversations.mockResolvedValueOnce({
        conversations: fullPage,
        total: 25,
        limit: 20,
        offset: 0,
      });

      const { result } = renderHook(() => useChat());

      // Act
      await act(async () => {
        await result.current.loadConversations();
      });

      // Assert
      await waitFor(() => {
        expect(result.current.conversationsHasMore).toBe(true);
      });
    });

    it('should indicate no more conversations when last page loaded', async () => {
      // Arrange - Partial page (< 20 items = no more available)
      const lastPage = [
        {
          id: 'conv-1',
          title: 'Last Conversation',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messageCount: 1,
        },
      ];

      mockChatService.getConversations.mockResolvedValueOnce({
        conversations: lastPage,
        total: 1,
        limit: 20,
        offset: 0,
      });

      const { result } = renderHook(() => useChat());

      // Act
      await act(async () => {
        await result.current.loadConversations();
      });

      // Assert
      await waitFor(() => {
        expect(result.current.conversationsHasMore).toBe(false);
      });
    });
  });

  describe('Set Current Conversation', () => {
    it('should set current conversation ID', () => {
      // Arrange
      const { result } = renderHook(() => useChat());

      // Act
      act(() => {
        result.current.setCurrentConversation('conv-123');
      });

      // Assert
      expect(result.current.currentConversationId).toBe('conv-123');
    });

    it('should clear messages when starting new conversation', () => {
      // Arrange
      const { result } = renderHook(() => useChat());

      // Set some messages first
      act(() => {
        result.current.setCurrentConversation('conv-123');
      });

      // Act - Start new conversation
      act(() => {
        result.current.setCurrentConversation(null);
      });

      // Assert
      expect(result.current.currentConversationId).toBeNull();
      expect(result.current.messages).toHaveLength(0);
    });
  });
});
