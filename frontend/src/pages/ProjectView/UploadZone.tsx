import { Box, Card, CardContent, Typography } from '@mui/material';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faImage, faCloudUploadAlt, faSpinner } from '@fortawesome/free-solid-svg-icons';
import type { Project } from '../../types';

interface UploadZoneProps {
  currentProject: Project;
  getRootProps: () => Record<string, unknown>;
  getInputProps: () => Record<string, unknown>;
  isDragActive: boolean;
  uploading: boolean;
}

export default function UploadZone({
  currentProject, getRootProps, getInputProps, isDragActive, uploading,
}: UploadZoneProps) {
  return (
    <Card>
      <CardContent>
        <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
          <FontAwesomeIcon icon={faImage} style={{ marginRight: 8 }} />
          Site Plan / Reference Image
        </Typography>

        {currentProject.site_plan_url ? (
          <Box>
            <Box
              component="img"
              src={currentProject.site_plan_url}
              alt="Site Plan"
              sx={{ width: '100%', borderRadius: 2, mb: 2 }}
            />
            <Box {...getRootProps()} sx={{ textAlign: 'center', cursor: 'pointer' }}>
              <input {...(getInputProps() as React.InputHTMLAttributes<HTMLInputElement>)} />
              <Typography variant="caption" color="primary">
                Click to replace image
              </Typography>
            </Box>
          </Box>
        ) : (
          <Box
            {...getRootProps()}
            sx={{
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : '#cbd5e1',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              bgcolor: isDragActive ? 'primary.50' : '#f8fafc',
              transition: 'all 0.2s',
              '&:hover': { borderColor: 'primary.main', bgcolor: '#f0f4ff' },
            }}
          >
            <input {...(getInputProps() as React.InputHTMLAttributes<HTMLInputElement>)} />
            {uploading ? (
              <FontAwesomeIcon icon={faSpinner} spin style={{ fontSize: 32, color: '#2563eb' }} />
            ) : (
              <>
                <FontAwesomeIcon icon={faCloudUploadAlt} style={{ fontSize: 32, color: '#94a3b8', marginBottom: 8 }} />
                <Typography variant="body2" color="text.secondary">
                  {isDragActive ? 'Drop image here' : 'Drag & drop or click to upload'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  JPG, PNG, WebP up to 10MB
                </Typography>
              </>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
