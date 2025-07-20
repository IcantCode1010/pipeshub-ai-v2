import { Helmet } from 'react-helmet-async';

import { UserRegistration } from 'src/auth/view/auth/user-registration';

// ----------------------------------------------------------------------

const metadata = { title: 'Sign up' };

export default function Page() {
  return (
    <>
      <Helmet>
        <title> {metadata.title}</title>
      </Helmet>

      <UserRegistration />
    </>
  );
}
