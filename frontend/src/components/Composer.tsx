import React, { useState, useRef, useEffect } from 'react';
import { Plus, Mic, ArrowUp } from 'lucide-react';

interface ComposerProps {
  onSendMessage: (text: string) => void;
  disabled?: boolean;
}

export const Composer: React.FC<ComposerProps> = ({ onSendMessage, disabled }) => {
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const toggleMic = () => {
    setIsListening((prev) => !prev);
  };

  return (
    <div className="composer-container">
      <form className="composer-pill" onSubmit={handleSubmit}>
        <button
          type="button"
          className="composer-action-btn attachment-btn"
          title="Add files or image (J10 Vision)"
        >
          <Plus size={20} />
        </button>

        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask JARVIS anything..."
          rows={1}
          disabled={disabled}
          className="composer-textarea"
        />

        <div className="composer-actions-right">
          <button
            type="button"
            className={`composer-action-btn mic-btn ${isListening ? 'listening' : ''}`}
            onClick={toggleMic}
            title={isListening ? 'Listening... (J4 Voice)' : 'Voice input (J4 Voice)'}
          >
            <Mic size={20} />
          </button>

          <button
            type="submit"
            className={`composer-action-btn send-btn ${input.trim() ? 'active' : ''}`}
            disabled={!input.trim() || disabled}
            title="Send message"
          >
            <ArrowUp size={20} />
          </button>
        </div>
      </form>
      <div className="composer-disclaimer">
        JARVIS can assist with system control, MCP tools, research, coding, and memory.
      </div>
    </div>
  );
};
