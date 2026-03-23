import { useEffect, useRef, useState } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import {
  Box, Typography, Card, CardContent, CircularProgress, Alert,
  Tabs, Tab, useMediaQuery, useTheme, Badge, Breadcrumbs,
  Link as MuiLink,
} from '@mui/material';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faPalette, faCouch, faLightbulb, faCheckCircle, faComments,
  faInfoCircle,
} from '@fortawesome/free-solid-svg-icons';
import { useDropzone } from 'react-dropzone';
import { useProjectStore, useChatStore } from '../store';
import { useSnackbar } from 'notistack';
import UploadZone from './ProjectView/UploadZone';
import StyleAnalysis from './ProjectView/StyleAnalysis';
import ChatPanel from './ProjectView/ChatPanel';

export default function ProjectView() {
  const { id } = useParams<{ id: string }>();
  const { currentProject, fetchProject, uploadSitePlan } = useProjectStore();
  const { messages, loading: chatLoading, sending, fetchMessages, sendMessage } = useChatStore();
  const [input, setInput] = useState('');
  const [uploading, setUploading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { enqueueSnackbar } = useSnackbar();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  useEffect(() => {
    if (id) {
      fetchProject(id);
      fetchMessages(id);
    }
  }, [id, fetchProject, fetchMessages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.webp'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
    onDrop: async (files) => {
      if (!id || files.length === 0) return;
      setUploading(true);
      try {
        await uploadSitePlan(id, files[0]);
        enqueueSnackbar('Site plan uploaded & analyzed!', { variant: 'success' });
        if (isMobile) setActiveTab(1);
      } catch {
        enqueueSnackbar('Upload failed', { variant: 'error' });
      } finally {
        setUploading(false);
      }
    },
  });

  const handleSend = async () => {
    if (!input.trim() || !id || sending) return;
    const msg = input;
    setInput('');
    await sendMessage(id, msg);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getCategoryIcon = (category: string) => {
    if (category.toLowerCase().includes('color')) return faPalette;
    if (category.toLowerCase().includes('furniture')) return faCouch;
    if (category.toLowerCase().includes('tip')) return faLightbulb;
    return faCheckCircle;
  };

  if (!currentProject) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  const leftPanel = (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, overflow: 'auto', height: '100%' }}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>{currentProject.name}</Typography>
          {currentProject.description && (
            <Typography variant="body2" color="text.secondary">{currentProject.description}</Typography>
          )}
        </CardContent>
      </Card>

      <UploadZone
        currentProject={currentProject}
        getRootProps={getRootProps}
        getInputProps={getInputProps}
        isDragActive={isDragActive}
        uploading={uploading}
      />

      {currentProject.detected_style && (
        <StyleAnalysis currentProject={currentProject} />
      )}

      {currentProject.site_plan_url && !isMobile && (
        <Alert severity="success" sx={{ borderRadius: 2 }}>
          Site plan analyzed! Use the <strong>Design Assistant</strong> on the right to get personalized recommendations.
        </Alert>
      )}
    </Box>
  );

  const chatPanel = (
    <ChatPanel
      currentProject={currentProject}
      messages={messages}
      chatLoading={chatLoading}
      sending={sending}
      input={input}
      setInput={setInput}
      handleSend={handleSend}
      handleKeyDown={handleKeyDown}
      getCategoryIcon={getCategoryIcon}
      messagesEndRef={messagesEndRef}
    />
  );

  return (
    <Box sx={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      <Breadcrumbs sx={{ mb: 2 }}>
        <MuiLink component={RouterLink} to="/" underline="hover" color="inherit">
          Dashboard
        </MuiLink>
        <Typography color="text.primary">{currentProject.name}</Typography>
      </Breadcrumbs>

      {isMobile ? (
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <Tabs
            value={activeTab}
            onChange={(_, v) => setActiveTab(v)}
            variant="fullWidth"
            sx={{ borderBottom: '1px solid #e2e8f0', mb: 1 }}
          >
            <Tab
              icon={<FontAwesomeIcon icon={faInfoCircle} />}
              iconPosition="start"
              label="Project"
            />
            <Tab
              icon={
                <Badge
                  color="primary"
                  variant="dot"
                  invisible={!currentProject.site_plan_url}
                >
                  <FontAwesomeIcon icon={faComments} />
                </Badge>
              }
              iconPosition="start"
              label="Assistant"
            />
          </Tabs>
          <Box sx={{ flex: 1, minHeight: 0, overflow: 'auto' }}>
            {activeTab === 0 ? leftPanel : chatPanel}
          </Box>
        </Box>
      ) : (
        <Box sx={{ flex: 1, display: 'flex', gap: 3, minHeight: 0 }}>
          <Box sx={{ width: 360, flexShrink: 0, overflow: 'auto' }}>
            {leftPanel}
          </Box>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            {chatPanel}
          </Box>
        </Box>
      )}
    </Box>
  );
}
