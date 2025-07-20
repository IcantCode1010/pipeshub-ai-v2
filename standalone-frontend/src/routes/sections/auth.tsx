import { lazy, Suspense } from 'react';
import { Outlet } from 'react-router-dom';

import { AuthSplitLayout } from 'src/layouts/auth-split';

import { SplashScreen } from 'src/components/loading-screen';

import { GuestGuard } from 'src/auth/guard';


// ----------------------------------------------------------------------

/** **************************************
 * Jwt
 *************************************** */
const Jwt = {
  SignInPage: lazy(() => import('src/pages/auth/jwt/sign-in')),
  SignUpPage: lazy(() => import('src/pages/auth/jwt/sign-up')),
  AccountSetupPage: lazy(() => import('src/pages/auth/jwt/account-setup')),
  ResetPasswordPage: lazy(() => import('src/pages/auth/jwt/reset-password')),
  EmailVerificationPage: lazy(() => import('src/pages/auth/jwt/email-verification')),
  SamlSsoSuccess: lazy(() => import('src/auth/view/auth/saml-sso-success')),
  OAuthCallback: lazy(() => import('src/auth/view/auth/oauth-callback')),
};


const authJwt = {
  children: [
    {
      path: 'sign-in',
      element: (
        <GuestGuard>
          <AuthSplitLayout section={{ 
            title: 'Hi, Welcome',
            videoUrl: '/video/Cockpit_Boot_Up_Video_Creation.mp4'
          }}>
            <Jwt.SignInPage />
          </AuthSplitLayout>
        </GuestGuard>
      ),
    },
    {
      path: 'sign-in/samlSso/success',  
      element: (
        <GuestGuard>
          <AuthSplitLayout section={{ title: 'Processing authentication...' }}>
          <Jwt.SamlSsoSuccess />
          </AuthSplitLayout>
        </GuestGuard>
      ),
    },
    {
      path: 'oauth/callback',
      element: (
        <GuestGuard>
          <Jwt.OAuthCallback />
        </GuestGuard>
      ),
    },
    {
      path: 'sign-up',
      element: (
        <GuestGuard>
          <AuthSplitLayout section={{ 
            title: 'Welcome to PipesHub AI',
            videoUrl: '/video/Cockpit_Boot_Up_Video_Creation.mp4'
          }}>
            <Jwt.SignUpPage />
          </AuthSplitLayout>
        </GuestGuard>
      ),
    },
    {
      path: 'reset-password',
      element: (
        <GuestGuard>
          <AuthSplitLayout>
            <Jwt.ResetPasswordPage />
          </AuthSplitLayout>
        </GuestGuard>
      ),
    },
    {
      path: 'verify-email',
      element: (
        <GuestGuard>
          <AuthSplitLayout section={{ 
            title: 'Email Verification',
            videoUrl: '/video/Cockpit_Boot_Up_Video_Creation.mp4'
          }}>
            <Jwt.EmailVerificationPage />
          </AuthSplitLayout>
        </GuestGuard>
      ),
    },
    {
      path: 'account-setup',
      element: (
        <GuestGuard>
          <AuthSplitLayout section={{ 
            title: 'Account Setup',
            videoUrl: '/video/Cockpit_Boot_Up_Video_Creation.mp4'
          }}>
            <Jwt.AccountSetupPage />
          </AuthSplitLayout>
        </GuestGuard>
      ),
    },
  ],
};

// ----------------------------------------------------------------------

export const authRoutes = [
  {
    path: 'auth',
    element: (
      <Suspense fallback={<SplashScreen />}>
        <Outlet />
      </Suspense>
    ),
    children: [authJwt],
  },
];
