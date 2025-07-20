import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Icon } from '@iconify/react';

import {
  Box,
  Card,
  Alert,
  Button,
  Typography,
  CardContent,
  CircularProgress,
} from '@mui/material';

import axios from 'src/utils/axios';
import { CONFIG } from 'src/config-global';

interface VerificationState {
  status: 'verifying' | 'success' | 'error' | 'expired';
  message: string;
}

export function EmailVerification() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [verification, setVerification] = useState<VerificationState>({
    status: 'verifying',
    message: 'Verifying your email address...',
  });
  const [isResending, setIsResending] = useState(false);

  const token = searchParams.get('token');
  const email = searchParams.get('email');

  useEffect(() => {
    const verifyEmail = async () => {
      if (!token) {
        setVerification({
          status: 'error',
          message: 'Invalid verification link. Please check your email for the correct link.',
        });
        return;
      }

      try {
        const response = await axios.post(`${CONFIG.authUrl}/api/v1/userAccount/verify`, {
          token,
          email,
        });

        if (response.data.success) {
          setVerification({
            status: 'success',
            message: 'Your email has been successfully verified! You can now sign in to your account.',
          });
        } else {
          setVerification({
            status: 'error',
            message: response.data.message || 'Email verification failed. Please try again.',
          });
        }
      } catch (error: any) {
        console.error('Email verification error:', error);
        
        if (error.response?.status === 410) {
          setVerification({
            status: 'expired',
            message: 'This verification link has expired. Please request a new verification email.',
          });
        } else if (error.response?.status === 400) {
          setVerification({
            status: 'error',
            message: 'Invalid verification token. Please check your email for the correct link.',
          });
        } else {
          setVerification({
            status: 'error',
            message: 'Email verification failed. Please try again or contact support.',
          });
        }
      }
    };

    verifyEmail();
  }, [token, email]);

  const handleResendEmail = async () => {
    if (!email) {
      setVerification({
        status: 'error',
        message: 'Email address not found. Please sign up again.',
      });
      return;
    }

    try {
      setIsResending(true);

      await axios.post(`${CONFIG.authUrl}/api/v1/userAccount/resend-verification`, {
        email,
      });

      setVerification({
        status: 'success',
        message: 'A new verification email has been sent. Please check your inbox.',
      });
    } catch (error: any) {
      console.error('Resend verification error:', error);
      setVerification({
        status: 'error',
        message: 'Failed to send verification email. Please try again later.',
      });
    } finally {
      setIsResending(false);
    }
  };

  const getIcon = () => {
    switch (verification.status) {
      case 'verifying':
        return <CircularProgress size={64} color="primary" />;
      case 'success':
        return (
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              bgcolor: 'success.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Icon icon="mdi:check" width={32} height={32} color="white" />
          </Box>
        );
      case 'expired':
        return (
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              bgcolor: 'warning.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Icon icon="mdi:clock-alert" width={32} height={32} color="white" />
          </Box>
        );
      case 'error':
      default:
        return (
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              bgcolor: 'error.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Icon icon="mdi:close" width={32} height={32} color="white" />
          </Box>
        );
    }
  };

  const getAlertSeverity = () => {
    switch (verification.status) {
      case 'success':
        return 'success';
      case 'expired':
        return 'warning';
      case 'error':
        return 'error';
      case 'verifying':
      default:
        return 'info';
    }
  };

  return (
    <Card sx={{ maxWidth: 500, mx: 'auto', mt: 8 }}>
      <CardContent sx={{ p: 5, textAlign: 'center' }}>
        <Box sx={{ mb: 3 }}>
          {getIcon()}
        </Box>

        <Typography variant="h4" sx={{ mb: 2, fontWeight: 600 }}>
          Email Verification
        </Typography>

        <Alert severity={getAlertSeverity()} sx={{ mb: 3, textAlign: 'left' }}>
          {verification.message}
        </Alert>

        {verification.status === 'success' && (
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/auth/sign-in', { 
              state: { message: 'Email verified successfully! You can now sign in.' }
            })}
            sx={{ mr: 2 }}
          >
            Sign In
          </Button>
        )}

        {verification.status === 'expired' && (
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="outlined"
              onClick={handleResendEmail}
              disabled={isResending}
            >
              {isResending ? 'Sending...' : 'Resend Verification Email'}
            </Button>
            <Button
              variant="contained"
              onClick={() => navigate('/auth/sign-up')}
            >
              Sign Up Again
            </Button>
          </Box>
        )}

        {verification.status === 'error' && (
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            {email && (
              <Button
                variant="outlined"
                onClick={handleResendEmail}
                disabled={isResending}
              >
                {isResending ? 'Sending...' : 'Resend Email'}
              </Button>
            )}
            <Button
              variant="contained"
              onClick={() => navigate('/auth/sign-up')}
            >
              Sign Up Again
            </Button>
          </Box>
        )}

        {verification.status === 'verifying' && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Please wait while we verify your email address...
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

export default EmailVerification;