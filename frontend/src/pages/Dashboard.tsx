import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Typography, Button, Card, CardContent, CardActions, Grid,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  IconButton, Chip, Skeleton, Breadcrumbs,
} from '@mui/material';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faPlus, faTrash, faArrowRight, faFolderOpen,
  faPaintBrush, faClock,
} from '@fortawesome/free-solid-svg-icons';
import { useProjectStore, useAuthStore } from '../store';
import { useSnackbar } from 'notistack';

export default function Dashboard() {
  const { projects, loading, fetchProjects, createProject, deleteProject } = useProjectStore();
  const user = useAuthStore((s) => s.user);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [creating, setCreating] = useState(false);
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    setCreating(true);
    try {
      const project = await createProject(newName.trim(), newDesc.trim() || undefined);
      setDialogOpen(false);
      setNewName('');
      setNewDesc('');
      enqueueSnackbar('Project created!', { variant: 'success' });
      navigate(`/project/${project.id}`);
    } catch {
      enqueueSnackbar('Failed to create project', { variant: 'error' });
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this project?')) return;
    try {
      await deleteProject(id);
      enqueueSnackbar('Project deleted', { variant: 'info' });
    } catch {
      enqueueSnackbar('Failed to delete project', { variant: 'error' });
    }
  };

  return (
    <Box>
      <Breadcrumbs sx={{ mb: 2 }}>
        <Typography color="text.primary">Dashboard</Typography>
      </Breadcrumbs>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4">
            Welcome back, {user?.name?.split(' ')[0]}
          </Typography>
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            Manage your interior design projects
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<FontAwesomeIcon icon={faPlus} />}
          onClick={() => setDialogOpen(true)}
        >
          New Project
        </Button>
      </Box>

      {loading ? (
        <Grid container spacing={3}>
          {[1, 2, 3].map((i) => (
            <Grid item xs={12} sm={6} md={4} key={i}>
              <Skeleton variant="rounded" height={200} />
            </Grid>
          ))}
        </Grid>
      ) : projects.length === 0 ? (
        <Card sx={{ textAlign: 'center', py: 8 }}>
          <CardContent>
            <FontAwesomeIcon icon={faFolderOpen} style={{ fontSize: 48, color: '#94a3b8', marginBottom: 16 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No projects yet
            </Typography>
            <Typography color="text.secondary" sx={{ mb: 3 }}>
              Create your first interior design project to get started
            </Typography>
            <Button variant="contained" startIcon={<FontAwesomeIcon icon={faPlus} />} onClick={() => setDialogOpen(true)}>
              Create Project
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {projects.map((project) => (
            <Grid item xs={12} sm={6} md={4} key={project.id}>
              <Card
                sx={{
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': { transform: 'translateY(-4px)', boxShadow: 4 },
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                }}
                onClick={() => navigate(`/project/${project.id}`)}
              >
                {project.site_plan_url ? (
                  <Box
                    sx={{
                      height: 160, backgroundImage: `url(${project.site_plan_url})`,
                      backgroundSize: 'cover', backgroundPosition: 'center',
                      borderBottom: '1px solid #e2e8f0',
                    }}
                  />
                ) : (
                  <Box sx={{
                    height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: 'linear-gradient(135deg, #e0e7ff, #c7d2fe)',
                  }}>
                    <FontAwesomeIcon icon={faPaintBrush} style={{ fontSize: 40, color: '#6366f1' }} />
                  </Box>
                )}
                <CardContent sx={{ flex: 1 }}>
                  <Typography variant="h6" noWrap>{project.name}</Typography>
                  {project.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }} noWrap>
                      {project.description}
                    </Typography>
                  )}
                  <Box sx={{ mt: 1.5, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {project.detected_style && (
                      <Chip
                        label={project.detected_style.replace(/-/g, ' ')}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    )}
                  </Box>
                </CardContent>
                <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    <FontAwesomeIcon icon={faClock} style={{ marginRight: 4 }} />
                    {new Date(project.updated_at).toLocaleDateString()}
                  </Typography>
                  <Box>
                    <IconButton size="small" onClick={(e) => handleDelete(project.id, e)} color="error">
                      <FontAwesomeIcon icon={faTrash} size="sm" />
                    </IconButton>
                    <IconButton size="small" color="primary">
                      <FontAwesomeIcon icon={faArrowRight} size="sm" />
                    </IconButton>
                  </Box>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create Project Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Project</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="Project Name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            margin="normal"
            placeholder="e.g., Living Room Redesign"
          />
          <TextField
            fullWidth
            label="Description (optional)"
            value={newDesc}
            onChange={(e) => setNewDesc(e.target.value)}
            margin="normal"
            multiline
            rows={3}
            placeholder="Brief description of your design project"
          />
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreate} disabled={!newName.trim() || creating}>
            {creating ? 'Creating...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
