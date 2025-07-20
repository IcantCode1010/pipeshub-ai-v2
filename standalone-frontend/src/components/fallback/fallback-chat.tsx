import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
  Button,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import { Icon } from '@iconify/react';
import robotIcon from '@iconify-icons/mdi/robot';
import alertCircleIcon from '@iconify-icons/mdi/alert-circle';
import refreshIcon from '@iconify-icons/mdi/refresh';
import checkCircleIcon from '@iconify-icons/mdi/check-circle';

interface FallbackChatProps {
  onRetry: () => void;
  isRetrying?: boolean;
}

export function FallbackChat({ onRetry, isRetrying = false }: FallbackChatProps) {
  const fallbackResponses = [
    'I apologize, but I&apos;m currently unable to access the knowledge base to provide you with accurate information.',
    'The AI services are temporarily unavailable. Please try again in a few moments.',
    'I&apos;m experiencing connectivity issues with the backend services. Please check your connection and try again.',
    'The system is currently in maintenance mode. Please try again later.',
  ];

  const troubleshootingSteps = [
    'Check if Docker services are running',
    'Verify network connectivity',
    'Ensure all required ports are accessible',
    'Wait a moment and try refreshing the page',
  ];

  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        p: 3,
      }}
    >
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Icon
              icon={robotIcon}
              style={{ fontSize: 32, marginRight: 12, color: '#1976d2' }}
            />
            <Typography variant="h6">Aerointel Solutions Agent</Typography>
          </Box>
          
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2">
              The AI agent is currently operating in offline mode. Some features are limited.
            </Typography>
          </Alert>

          <Typography variant="body1" sx={{ mb: 2 }}>
            Hello! I&apos;m currently unable to access the full knowledge base and AI services. 
            Here&apos;s what&apos;s happening:
          </Typography>

          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Fallback Responses Available:
            </Typography>
            <List dense>
              {fallbackResponses.map((response, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <Icon icon={alertCircleIcon} style={{ color: '#ff9800' }} />
                  </ListItemIcon>
                  <ListItemText primary={response} />
                </ListItem>
              ))}
            </List>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" gutterBottom>
            Troubleshooting Steps:
          </Typography>
          <List dense>
            {troubleshootingSteps.map((step, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <Icon icon={checkCircleIcon} style={{ color: '#4caf50' }} />
                </ListItemIcon>
                <ListItemText primary={step} />
              </ListItem>
            ))}
          </List>

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Button
              variant="contained"
              startIcon={<Icon icon={refreshIcon} />}
              onClick={onRetry}
              disabled={isRetrying}
            >
              {isRetrying ? 'Checking Services...' : 'Retry Connection'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ flexGrow: 1 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Limited Functionality Available
          </Typography>
          <Typography variant="body2" color="textSecondary">
            While services are unavailable, you can still:
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="• Browse previously loaded content" />
            </ListItem>
            <ListItem>
              <ListItemText primary="• Access account settings" />
            </ListItem>
            <ListItem>
              <ListItemText primary="• View system status" />
            </ListItem>
            <ListItem>
              <ListItemText primary="• Export/download existing data" />
            </ListItem>
          </List>
        </CardContent>
      </Card>
    </Box>
  );
}

export default FallbackChat;