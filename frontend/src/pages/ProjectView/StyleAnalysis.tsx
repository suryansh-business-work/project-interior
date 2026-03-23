import { Box, Card, CardContent, Typography, Chip, LinearProgress } from '@mui/material';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPalette } from '@fortawesome/free-solid-svg-icons';
import type { Project } from '../../types';

interface StyleAnalysisProps {
  currentProject: Project;
}

export default function StyleAnalysis({ currentProject }: StyleAnalysisProps) {
  if (!currentProject.detected_style) return null;

  return (
    <Card>
      <CardContent>
        <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
          <FontAwesomeIcon icon={faPalette} style={{ marginRight: 8 }} />
          Style Analysis
        </Typography>
        <Chip
          label={currentProject.detected_style.replace(/-/g, ' ').toUpperCase()}
          color="primary"
          sx={{ mb: 2, fontWeight: 600 }}
        />
        {currentProject.style_confidence !== null && (
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption">Confidence</Typography>
              <Typography variant="caption" fontWeight={600}>
                {currentProject.style_confidence.toFixed(1)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={Math.min(currentProject.style_confidence, 100)}
              sx={{ borderRadius: 4, height: 8 }}
            />
          </Box>
        )}
        {currentProject.style_probabilities && (
          <Box>
            <Typography variant="caption" color="text.secondary" fontWeight={600}>
              Top Styles:
            </Typography>
            {Object.entries(currentProject.style_probabilities)
              .sort(([, a], [, b]) => b - a)
              .slice(0, 5)
              .map(([style, conf]) => (
                <Box key={style} sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                  <Typography variant="caption" sx={{ flex: 1 }}>
                    {style.replace(/-/g, ' ')}
                  </Typography>
                  <Typography variant="caption" fontWeight={600}>
                    {(conf as number).toFixed(1)}%
                  </Typography>
                </Box>
              ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
