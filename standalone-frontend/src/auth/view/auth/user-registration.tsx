import type { AccountType } from 'src/pages/auth/jwt/account-setup';

import { z } from 'zod';
import { Icon } from '@iconify/react';
import { useState } from 'react';
import { useNavigate } from 'react-router';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

// Icons
import eyeIcon from '@iconify-icons/mdi/eye';
import lockIcon from '@iconify-icons/mdi/lock';
import emailIcon from '@iconify-icons/mdi/email';
import eyeOffIcon from '@iconify-icons/mdi/eye-off';
import accountIcon from '@iconify-icons/mdi/account';
import lockCheckIcon from '@iconify-icons/mdi/lock-check';
import accountCircleIcon from '@iconify-icons/mdi/account-circle';

import {
  Box,
  Grid,
  Card,
  alpha,
  Alert,
  Button,
  Divider,
  Checkbox,
  CardContent,
  TextField,
  IconButton,
  Typography,
  InputAdornment,
  CircularProgress,
  FormControlLabel,
  Link,
} from '@mui/material';

import { useAuthContext } from 'src/auth/hooks';

// Enhanced Registration Schema
const registrationSchema = z
  .object({
    firstName: z
      .string()
      .min(1, 'First name is required')
      .max(50, 'First name must be less than 50 characters'),
    lastName: z
      .string()
      .min(1, 'Last name is required')
      .max(50, 'Last name must be less than 50 characters'),
    email: z
      .string()
      .min(1, 'Email is required')
      .email('Please enter a valid email address'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number')
      .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),
    confirmPassword: z.string(),
    accountType: z.enum(['individual', 'business']),
    organizationName: z.string().optional(),
    termsAccepted: z.boolean().refine((val) => val === true, {
      message: 'You must accept the terms and conditions',
    }),
    marketingConsent: z.boolean().optional(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })
  .refine(
    (data) => {
      if (data.accountType === 'business') {
        return data.organizationName && data.organizationName.length > 0;
      }
      return true;
    },
    {
      message: 'Organization name is required for business accounts',
      path: ['organizationName'],
    }
  );

type RegistrationFormData = z.infer<typeof registrationSchema>;

interface UserRegistrationProps {
  defaultAccountType?: AccountType;
  onSuccess?: () => void;
  onAccountTypeChange?: (type: AccountType) => void;
}

export function UserRegistration({
  defaultAccountType = 'individual',
  onSuccess,
  onAccountTypeChange,
}: UserRegistrationProps) {
  const navigate = useNavigate();
  const { register } = useAuthContext();
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);

  const {
    control,
    handleSubmit,
    watch,
    formState: { errors, isValid },
    reset,
  } = useForm<RegistrationFormData>({
    resolver: zodResolver(registrationSchema),
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      confirmPassword: '',
      accountType: defaultAccountType,
      organizationName: '',
      termsAccepted: false,
      marketingConsent: false,
    },
    mode: 'onChange',
  });

  const accountType = watch('accountType');
  const password = watch('password');

  // Password strength indicator
  const getPasswordStrength = (pwd: string) => {
    let strength = 0;
    if (pwd.length >= 8) strength += 1;
    if (/[A-Z]/.test(pwd)) strength += 1;
    if (/[a-z]/.test(pwd)) strength += 1;
    if (/[0-9]/.test(pwd)) strength += 1;
    if (/[^A-Za-z0-9]/.test(pwd)) strength += 1;
    return strength;
  };

  const passwordStrength = getPasswordStrength(password || '');
  const strengthColors = ['error', 'error', 'warning', 'info', 'success'];
  const strengthLabels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];

  const handleAccountTypeChange = (type: AccountType) => {
    reset((formData) => ({
      ...formData,
      accountType: type,
      organizationName: type === 'business' ? formData.organizationName : '',
    }));
    onAccountTypeChange?.(type);
  };

  const onSubmit = async (data: RegistrationFormData) => {
    setLoading(true);
    setError('');

    try {
      // Prepare registration data
      const registrationData = {
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email,
        password: data.password,
        accountType: data.accountType,
        organizationName: data.organizationName,
        termsAccepted: data.termsAccepted,
        marketingConsent: data.marketingConsent,
      };

      // Call registration API
      await register?.(registrationData);

      // Show success message and redirect
      setCurrentStep(3);
      
      setTimeout(() => {
        onSuccess?.();
        navigate('/auth/sign-in', {
          state: { 
            message: 'Registration successful! Please check your email to verify your account.',
            email: data.email 
          }
        });
      }, 2000);

    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleNextStep = () => {
    setCurrentStep(2);
  };

  const handleBackStep = () => {
    setCurrentStep(1);
  };

  // Success step
  if (currentStep === 3) {
    return (
      <Card sx={{ maxWidth: 480, mx: 'auto', mt: 4 }}>
        <CardContent sx={{ p: 5, textAlign: 'center' }}>
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              bgcolor: 'success.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mx: 'auto',
              mb: 3,
            }}
          >
            <Icon icon="mdi:check" width={32} height={32} color="white" />
          </Box>
          
          <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
            Registration Successful!
          </Typography>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            We&apos;ve sent a verification email to your address. Please check your inbox and click 
            the verification link to activate your account.
          </Typography>
          
          <CircularProgress size={24} />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Redirecting to sign in...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ maxWidth: 480, mx: 'auto', mt: 4 }}>
      <CardContent sx={{ p: 5 }}>
        {/* Header */}
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h4" sx={{ mb: 1, fontWeight: 700 }}>
            Create Account
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {currentStep === 1 ? 'Choose your account type' : 'Enter your details'}
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          {/* Step 1: Account Type Selection */}
          {currentStep === 1 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 3, textAlign: 'center' }}>
                Select Account Type
              </Typography>
              
              <Grid container spacing={2} sx={{ mb: 4 }}>
                <Grid item xs={6}>
                  <Card
                    sx={{
                      cursor: 'pointer',
                      border: '2px solid',
                      borderColor: accountType === 'individual' ? 'primary.main' : 'divider',
                      bgcolor: accountType === 'individual' ? alpha('primary.main', 0.04) : 'background.paper',
                      '&:hover': {
                        borderColor: 'primary.main',
                      },
                    }}
                    onClick={() => handleAccountTypeChange('individual')}
                  >
                    <CardContent sx={{ textAlign: 'center', py: 3 }}>
                      <Icon icon={accountCircleIcon} width={40} height={40} />
                      <Typography variant="subtitle1" sx={{ mt: 1, fontWeight: 600 }}>
                        Individual
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Personal use
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={6}>
                  <Card
                    sx={{
                      cursor: 'pointer',
                      border: '2px solid',
                      borderColor: accountType === 'business' ? 'primary.main' : 'divider',
                      bgcolor: accountType === 'business' ? alpha('primary.main', 0.04) : 'background.paper',
                      '&:hover': {
                        borderColor: 'primary.main',
                      },
                    }}
                    onClick={() => handleAccountTypeChange('business')}
                  >
                    <CardContent sx={{ textAlign: 'center', py: 3 }}>
                      <Icon icon="mdi:domain" width={40} height={40} />
                      <Typography variant="subtitle1" sx={{ mt: 1, fontWeight: 600 }}>
                        Business
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Team/Company
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <Button
                fullWidth
                size="large"
                variant="contained"
                onClick={handleNextStep}
                sx={{ mt: 2 }}
              >
                Continue
              </Button>
            </Box>
          )}

          {/* Step 2: Registration Form */}
          {currentStep === 2 && (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Controller
                    name="firstName"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="First Name"
                        error={!!errors.firstName}
                        helperText={errors.firstName?.message}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Icon icon={accountIcon} width={20} />
                            </InputAdornment>
                          ),
                        }}
                      />
                    )}
                  />
                </Grid>
                
                <Grid item xs={6}>
                  <Controller
                    name="lastName"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        fullWidth
                        label="Last Name"
                        error={!!errors.lastName}
                        helperText={errors.lastName?.message}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Icon icon={accountIcon} width={20} />
                            </InputAdornment>
                          ),
                        }}
                      />
                    )}
                  />
                </Grid>
              </Grid>

              <Controller
                name="email"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Email Address"
                    type="email"
                    error={!!errors.email}
                    helperText={errors.email?.message}
                    sx={{ mt: 2 }}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Icon icon={emailIcon} width={20} />
                        </InputAdornment>
                      ),
                    }}
                  />
                )}
              />

              {accountType === 'business' && (
                <Controller
                  name="organizationName"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="Organization Name"
                      error={!!errors.organizationName}
                      helperText={errors.organizationName?.message}
                      sx={{ mt: 2 }}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Icon icon="mdi:domain" width={20} />
                          </InputAdornment>
                        ),
                      }}
                    />
                  )}
                />
              )}

              <Controller
                name="password"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Password"
                    type={showPassword ? 'text' : 'password'}
                    error={!!errors.password}
                    helperText={errors.password?.message}
                    sx={{ mt: 2 }}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Icon icon={lockIcon} width={20} />
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowPassword(!showPassword)}
                            edge="end"
                          >
                            <Icon icon={showPassword ? eyeOffIcon : eyeIcon} width={20} />
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />
                )}
              />

              {/* Password Strength Indicator */}
              {password && (
                <Box sx={{ mt: 1 }}>
                  <Box sx={{ display: 'flex', gap: 0.5, mb: 0.5 }}>
                    {[1, 2, 3, 4, 5].map((level) => (
                      <Box
                        key={level}
                        sx={{
                          flex: 1,
                          height: 4,
                          borderRadius: 2,
                          bgcolor: passwordStrength >= level ? `${strengthColors[passwordStrength - 1]}.main` : 'grey.300',
                        }}
                      />
                    ))}
                  </Box>
                  <Typography variant="caption" color={`${strengthColors[passwordStrength - 1]}.main`}>
                    Password strength: {strengthLabels[passwordStrength - 1]}
                  </Typography>
                </Box>
              )}

              <Controller
                name="confirmPassword"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Confirm Password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    error={!!errors.confirmPassword}
                    helperText={errors.confirmPassword?.message}
                    sx={{ mt: 2 }}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Icon icon={lockCheckIcon} width={20} />
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            edge="end"
                          >
                            <Icon icon={showConfirmPassword ? eyeOffIcon : eyeIcon} width={20} />
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />
                )}
              />

              <Divider sx={{ my: 3 }} />

              {/* Terms and Marketing Consent */}
              <Controller
                name="termsAccepted"
                control={control}
                render={({ field }) => (
                  <FormControlLabel
                    control={
                      <Checkbox
                        {...field}
                        checked={field.value}
                        color="primary"
                      />
                    }
                    label={
                      <Typography variant="body2">
                        I agree to the{' '}
                        <Link href="#" underline="hover">
                          Terms of Service
                        </Link>{' '}
                        and{' '}
                        <Link href="#" underline="hover">
                          Privacy Policy
                        </Link>
                      </Typography>
                    }
                  />
                )}
              />
              
              {errors.termsAccepted && (
                <Typography variant="caption" color="error" sx={{ display: 'block', mt: 0.5 }}>
                  {errors.termsAccepted.message}
                </Typography>
              )}

              <Controller
                name="marketingConsent"
                control={control}
                render={({ field }) => (
                  <FormControlLabel
                    control={
                      <Checkbox
                        {...field}
                        checked={field.value}
                        color="primary"
                      />
                    }
                    label={
                      <Typography variant="body2">
                        I would like to receive product updates and marketing communications
                      </Typography>
                    }
                    sx={{ mt: 1 }}
                  />
                )}
              />

              {/* Action Buttons */}
              <Box sx={{ display: 'flex', gap: 2, mt: 4 }}>
                <Button
                  variant="outlined"
                  onClick={handleBackStep}
                  sx={{ flex: 1 }}
                >
                  Back
                </Button>
                
                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading || !isValid}
                  sx={{ flex: 2 }}
                >
                  {loading ? (
                    <CircularProgress size={24} color="inherit" />
                  ) : (
                    'Create Account'
                  )}
                </Button>
              </Box>
            </Box>
          )}
        </form>

        {/* Sign In Link */}
        {currentStep === 2 && (
          <Box sx={{ textAlign: 'center', mt: 3 }}>
            <Typography variant="body2" color="text.secondary">
              Already have an account?{' '}
              <Link
                component="button"
                variant="body2"
                onClick={() => navigate('/auth/sign-in')}
                underline="hover"
              >
                Sign in
              </Link>
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

export default UserRegistration;