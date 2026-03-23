import type { RefObject } from 'react';
import {
  Box, Typography, TextField, IconButton, Chip, Card,
  CircularProgress, Alert,
} from '@mui/material';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faPaperPlane, faPalette, faCouch, faLightbulb,
  faCheckCircle, faSpinner, faImage,
} from '@fortawesome/free-solid-svg-icons';
import type { Project, ChatMessage } from '../../types';
import type { IconDefinition } from '@fortawesome/fontawesome-svg-core';
import MessageBubble from './MessageBubble';

interface ChatPanelProps {
  currentProject: Project;
  messages: ChatMessage[];
  chatLoading: boolean;
  sending: boolean;
  input: string;
  setInput: (v: string) => void;
  handleSend: () => void;
  handleKeyDown: (e: React.KeyboardEvent) => void;
  getCategoryIcon: (category: string) => IconDefinition;
  messagesEndRef: RefObject<HTMLDivElement>;
}

export default function ChatPanel({
  currentProject, messages, chatLoading, sending,
  input, setInput, handleSend, handleKeyDown, getCategoryIcon, messagesEndRef,
}: ChatPanelProps) {
  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <Box sx={{ p: 2, borderBottom: '1px solid #e2e8f0' }}>
        <Typography variant="h6">Design Assistant</Typography>
        <Typography variant="caption" color="text.secondary">
          Ask about colors, furniture, materials, or room-specific designs
        </Typography>
      </Box>

      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {chatLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={32} />
          </Box>
        ) : messages.length === 0 ? (
          <EmptyChat setInput={setInput} />
        ) : (
          messages.map((msg) => (
            <MessageBubble key={msg.id} msg={msg} getCategoryIcon={getCategoryIcon} />
          ))
        )}
        <div ref={messagesEndRef} />
      </Box>

      <Box sx={{ p: 2, borderTop: '1px solid #e2e8f0' }}>
        {!currentProject.site_plan_url && (
          <Alert severity="info" sx={{ mb: 1.5, borderRadius: 2 }}>
            Upload a site plan for personalized design recommendations
          </Alert>
        )}
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          <TextField
            fullWidth
            placeholder="Ask about design styles, colors, furniture... or ask to generate an image"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            multiline
            maxRows={3}
            size="small"
          />
          <IconButton
            color="primary"
            onClick={handleSend}
            disabled={!input.trim() || sending}
            sx={{
              bgcolor: 'primary.main', color: 'white', width: 48, height: 48,
              '&:hover': { bgcolor: 'primary.dark' },
              '&:disabled': { bgcolor: '#e2e8f0', color: '#94a3b8' },
            }}
          >
            {sending ? (
              <FontAwesomeIcon icon={faSpinner} spin />
            ) : (
              <FontAwesomeIcon icon={faPaperPlane} />
            )}
          </IconButton>
        </Box>
        <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
          <Chip
            label="Generate design image"
            size="small"
            variant="outlined"
            clickable
            icon={<FontAwesomeIcon icon={faImage} style={{ fontSize: 12 }} />}
            onClick={() => setInput('Generate an image of a beautiful ' +
              (currentProject.detected_style || 'modern') + ' style living room')}
            sx={{ borderRadius: 4, fontSize: '0.75rem' }}
          />
        </Box>
      </Box>
    </Card>
  );
}

function EmptyChat({ setInput }: { setInput: (v: string) => void }) {
  return (
    <Box sx={{ textAlign: 'center', py: 6 }}>
      <FontAwesomeIcon icon={faLightbulb} style={{ fontSize: 40, color: '#fbbf24', marginBottom: 16 }} />
      <Typography variant="h6" color="text.secondary" gutterBottom>
        Start a conversation
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 400, mx: 'auto' }}>
        Upload a site plan first, then ask me about design styles, color palettes,
        furniture recommendations, or room-specific ideas.
      </Typography>
      <Box sx={{ mt: 3, display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center' }}>
        {['What style is my space?', 'Suggest living room colors', 'Recommend furniture'].map((q) => (
          <Chip
            key={q}
            label={q}
            variant="outlined"
            clickable
            onClick={() => setInput(q)}
            sx={{ borderRadius: 6 }}
          />
        ))}
      </Box>
    </Box>
  );
}
