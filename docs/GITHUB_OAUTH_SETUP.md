# GitHub OAuth Setup Guide

This guide explains how to set up GitHub OAuth integration for the MisinfoGuard platform.

## 1. Create a GitHub OAuth App

1. Sign in to your GitHub account
2. Go to **Settings** > **Developer settings** > **OAuth Apps**
3. Click **New OAuth App**
4. Fill in the required details:
   - **Application name**: MisinfoGuard
   - **Homepage URL**: http://localhost:3001 (development) or your production URL
   - **Application description**: AI-powered misinformation detection platform
   - **Authorization callback URL**: http://localhost:3001/api/auth/callback/github (development) or your production URL

5. Click **Register application**
6. Once created, you'll see your **Client ID**
7. Click **Generate a new client secret** to get your **Client Secret**

## 2. Configure Environment Variables

### Frontend (.env.local)

Add these environment variables to your frontend `.env.local` file:

```
# GitHub OAuth Configuration
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

### Backend (.env)

Add these environment variables to your backend `.env` file:

```
# GitHub OAuth Configuration
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_CALLBACK_URL=http://localhost:3001/api/auth/callback/github
```

## 3. Testing the Integration

1. Start both your frontend and backend servers
2. Navigate to the login page
3. Click on the "Sign in with GitHub" button
4. You should be redirected to GitHub's authorization page
5. After authorizing, you should be redirected back to your application and logged in

## 4. Troubleshooting

### Common Issues

- **Callback URL mismatch**: Make sure the callback URL in your GitHub OAuth App settings exactly matches what's in your code/environment variables.
- **Scope issues**: If you're not getting user emails, make sure you're requesting the `user:email` scope.
- **CORS issues**: Check the backend CORS configuration to ensure it allows your frontend origin.
- **Redirect URI errors**: Verify that your Next.js configuration is correctly handling the callback route.

### Server Logs

Check the backend logs for any authentication errors. Look for:

```
[ERROR] GitHub OAuth failed: [error message]
```

### API Response Testing

You can test the GitHub OAuth endpoint directly:

```bash
curl -X POST http://localhost:8000/api/v1/auth/oauth/github \
  -H "Content-Type: application/json" \
  -d '{"accessToken": "your_github_access_token"}'
```

## 5. Security Considerations

- Never commit your GitHub Client Secret to version control
- Always use HTTPS in production
- Implement proper token validation and security headers
- Consider adding rate limiting to prevent abuse

## 6. Production Deployment

For production deployment, make sure to:

1. Update all URLs to use your production domain
2. Create a separate GitHub OAuth App for production
3. Use proper HTTPS for all communication
4. Set restrictive CORS policies
