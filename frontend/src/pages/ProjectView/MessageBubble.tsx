import { Box, Typography, Paper } from '@mui/material';
import Grid from '@mui/material/Grid';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import ReactMarkdown from 'react-markdown';
import type { ChatMessage } from '../../types';
import type { IconDefinition } from '@fortawesome/fontawesome-svg-core';

interface MessageBubbleProps {
  msg: ChatMessage;
  getCategoryIcon: (c: string) => IconDefinition;
}

export default function MessageBubble({ msg, getCategoryIcon }: MessageBubbleProps) {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Paper
        sx={{
          p: 2,
          maxWidth: '80%',
          bgcolor: msg.role === 'user' ? 'primary.main' : '#f1f5f9',
          color: msg.role === 'user' ? 'white' : 'text.primary',
          borderRadius: msg.role === 'user'
            ? '16px 16px 4px 16px'
            : '16px 16px 16px 4px',
        }}
        elevation={0}
      >
        <ReactMarkdown
          components={{
            p: ({ children }) => (
              <Typography variant="body2" sx={{ mb: 1, '&:last-child': { mb: 0 } }}>
                {children}
              </Typography>
            ),
            strong: ({ children }) => (
              <Typography component="span" variant="body2" fontWeight={700}>
                {children}
              </Typography>
            ),
            li: ({ children }) => (
              <Typography variant="body2" component="li" sx={{ ml: 2 }}>
                {children}
              </Typography>
            ),
          }}
        >
          {msg.message}
        </ReactMarkdown>

        {msg.image_url && (
          <Box
            component="img"
            src={msg.image_url}
            alt="Generated design"
            sx={{ width: '100%', borderRadius: 2, mt: 2 }}
          />
        )}

        {msg.design_suggestions && msg.design_suggestions.length > 0 && (
          <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e2e8f0' }}>
            <Grid container spacing={1}>
              {msg.design_suggestions.map((sug, i) => (
                <Grid item xs={12} key={i}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                    <FontAwesomeIcon
                      icon={getCategoryIcon(sug.category)}
                      style={{ marginTop: 4, color: '#2563eb', fontSize: 12 }}
                    />
                    <Box>
                      <Typography variant="caption" fontWeight={600} color="primary">
                        {sug.category}
                      </Typography>
                      <Typography variant="caption" display="block" color="text.secondary">
                        {sug.suggestion}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Paper>
    </Box>
  );
}
