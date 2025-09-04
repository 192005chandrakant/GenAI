# Google OAuth Setup Guide

This guide will help you set up Google OAuth for the MisinfoGuard application.

## Prerequisites

- Google Cloud Console account
- MisinfoGuard project set up locally

## Steps to Set Up Google OAuth

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `misinfoguard-oauth`
4. Click "Create"

### 2. Enable Google+ API

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on it and press "Enable"

### 3. Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" user type
3. Fill in the required fields:
   - **App name**: MisinfoGuard
   - **User support email**: Your email
   - **Developer contact email**: Your email
4. Add scopes:
   - `../auth/userinfo.email`
   - `../auth/userinfo.profile`
5. Add test users (your email addresses for testing)
6. Save and continue

### 4. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Configure:
   - **Name**: MisinfoGuard Web Client
   - **Authorized JavaScript origins**: 
     - `http://localhost:3000` (for development)
     - `https://yourdomain.com` (for production)
   - **Authorized redirect URIs**:
     - `http://localhost:3000/api/auth/callback/google` (for development)
     - `https://yourdomain.com/api/auth/callback/google` (for production)
5. Click "Create"
6. Copy the **Client ID** and **Client Secret**

### 5. Update Environment Variables

1. Copy `.env.example` to `.env.local`
2. Update the following variables:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-random-secret-key-here
```

To generate a NEXTAUTH_SECRET, you can use:
```bash
openssl rand -base64 32
```

### 6. Install Required Dependencies

The required dependencies should already be installed, but verify these are in your `package.json`:

```json
{
  "dependencies": {
    "next-auth": "^4.24.11",
    "@next-auth/prisma-adapter": "^1.0.7" // if using Prisma
  }
}
```

### 7. Test the Integration

1. Start your development server:
   ```bash
   npm run dev
   ```

2. Navigate to `http://localhost:3000/auth/login`
3. Click "Continue with Google"
4. You should be redirected to Google's OAuth consent screen
5. After successful authentication, you'll be redirected back to your app

## Troubleshooting

### Common Issues

1. **"redirect_uri_mismatch" error**
   - Ensure your redirect URI in Google Cloud Console exactly matches your NextAuth callback URL
   - Check that you're using the correct protocol (http vs https)

2. **"unauthorized_client" error**
   - Verify your Client ID and Client Secret are correct
   - Make sure the OAuth consent screen is properly configured

3. **"access_denied" error**
   - Check if your test user is added to the OAuth consent screen
   - Ensure the required scopes are configured

### Development vs Production

For production deployment:

1. Update the OAuth consent screen to "In production"
2. Add your production domain to authorized origins and redirect URIs
3. Update environment variables with production values
4. Ensure HTTPS is enabled on your production domain

## Security Notes

- Never commit your `.env.local` file to version control
- Use strong, random values for `NEXTAUTH_SECRET`
- Regularly rotate your OAuth credentials
- Monitor OAuth usage in Google Cloud Console

## Additional Resources

- [NextAuth.js Google Provider Documentation](https://next-auth.js.org/providers/google)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
