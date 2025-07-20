import { Helmet } from 'react-helmet-async';

import { EmailVerification } from 'src/auth/view/auth/email-verification';

// ----------------------------------------------------------------------

const metadata = { title: 'Email Verification' };

export default function Page() {
  return (
    <>
      <Helmet>
        <title> {metadata.title}</title>
      </Helmet>

      <EmailVerification />
    </>
  );
}