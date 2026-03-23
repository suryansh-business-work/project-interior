import { useEffect, useState } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Chip, CircularProgress, TextField,
  InputAdornment, Breadcrumbs, Link as MuiLink,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faPalette } from '@fortawesome/free-solid-svg-icons';
import api from '../api';
import type { StyleInfo } from '../types';

const STYLE_COLORS: Record<string, string> = {
  asian: '#d4a373',
  coastal: '#89c2d9',
  contemporary: '#6c757d',
  craftsman: '#8B4513',
  eclectic: '#e63946',
  farmhouse: '#a8dadc',
  'french-country': '#cdb4db',
  industrial: '#495057',
  mediterranean: '#e07a5f',
  'mid-century-modern': '#f4a261',
  modern: '#2b2d42',
  rustic: '#6b4226',
  scandinavian: '#e9ecef',
  'shabby-chic-style': '#ffb5c2',
  southwestern: '#d2691e',
  traditional: '#1b4332',
  transitional: '#adb5bd',
  tropical: '#2d6a4f',
  victorian: '#6a0572',
};

export default function StyleExplorer() {
  const [styles, setStyles] = useState<StyleInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api.get('/styles/').then(({ data }) => {
      setStyles(data.styles);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const filtered = styles.filter((s) =>
    s.display_name.toLowerCase().includes(search.toLowerCase()) ||
    s.description.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Breadcrumbs sx={{ mb: 2 }}>
        <MuiLink component={RouterLink} to="/" underline="hover" color="inherit">
          Dashboard
        </MuiLink>
        <Typography color="text.primary">Style Explorer</Typography>
      </Breadcrumbs>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4">
            <FontAwesomeIcon icon={faPalette} style={{ marginRight: 12 }} />
            Style Explorer
          </Typography>
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            Explore {styles.length} interior design styles
          </Typography>
        </Box>
        <TextField
          size="small"
          placeholder="Search styles..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <FontAwesomeIcon icon={faSearch} />
              </InputAdornment>
            ),
          }}
          sx={{ minWidth: 250 }}
        />
      </Box>

      <Grid container spacing={3}>
        {filtered.map((style) => (
          <Grid item xs={12} sm={6} md={4} key={style.name}>
            <Card sx={{
              height: '100%', transition: 'all 0.2s',
              '&:hover': { transform: 'translateY(-4px)', boxShadow: 4 },
            }}>
              <Box sx={{
                height: 8,
                bgcolor: STYLE_COLORS[style.name] || '#667eea',
              }} />
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {style.display_name}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 60 }}>
                  {style.description}
                </Typography>

                <Typography variant="caption" fontWeight={600} color="text.secondary">
                  Color Palette
                </Typography>
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5, mb: 1.5 }}>
                  {style.colors.map((color) => (
                    <Chip key={color} label={color} size="small" variant="outlined" />
                  ))}
                </Box>

                <Typography variant="caption" fontWeight={600} color="text.secondary">
                  Key Materials
                </Typography>
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5, mb: 1.5 }}>
                  {style.materials.slice(0, 3).map((mat) => (
                    <Chip key={mat} label={mat} size="small" color="primary" variant="outlined" />
                  ))}
                </Box>

                <Typography variant="caption" color="text.secondary" fontStyle="italic">
                  {style.preview_tip}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
