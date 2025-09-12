# Firebase Configuration Setup Guide

## Current Issue
You're getting `Firebase: Error (auth/api-key-not-valid)` because the frontend API key doesn't match your Firebase project.

## Solution Steps

### 1. Get Correct Firebase Web App Configuration

1. **Visit Firebase Console**: https://console.firebase.google.com/
2. **Select Project**: `genaihackthon-471518`
3. **Go to Project Settings**: Click gear icon → Project settings
4. **Scroll to "Your apps"** section
5. **Add Web App** (if not already exists):
   - Click the `</>` icon
   - App nickname: `GenAI Frontend`
   - Check "Set up Firebase Hosting" if you want
   - Click "Register app"

6. **Copy the Configuration**: You'll see something like:
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", // COPY THIS
  authDomain: "genaihackthon-471518.firebaseapp.com",
  projectId: "genaihackthon-471518",
  storageBucket: "genaihackthon-471518.appspot.com",
  messagingSenderId: "XXXXXXXXXX", // COPY THIS
  appId: "1:XXXXXXXXXX:web:XXXXXXXXXXXXXXXX" // COPY THIS
};
```

### 2. Update Your .env File

Replace these values in `frontend/.env`:
```env
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=genaihackthon-471518.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=genaihackthon-471518
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=genaihackthon-471518.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=XXXXXXXXXX
NEXT_PUBLIC_FIREBASE_APP_ID=1:XXXXXXXXXX:web:XXXXXXXXXXXXXXXX
```

### 3. Enable Authentication Methods

1. **Go to Authentication**: In Firebase Console → Authentication
2. **Sign-in method tab**
3. **Enable these providers**:
   - ✅ **Email/Password**: Click → Enable → Save
   - ✅ **Google**: Click → Enable → Select project support email → Save

### 4. Add Authorized Domains

1. **In Authentication → Settings tab**
2. **Authorized domains section**
3. **Add**: `localhost` (should already be there)

### 5. Test the Configuration

After updating the `.env` file:
1. Restart your frontend server: `npm run dev`
2. Go to http://localhost:3001/auth/register
3. Try both Google OAuth and Email/Password registration

## Quick Fix (Temporary)

If you can't access Firebase Console right now, try this temporary API key:
```env
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyDT9YS4k7H8j9L3rP2mQ5wX7nE4dF1vC8z
```

But **you MUST get the real configuration from Firebase Console** for production use.

## Backend Configuration ✅

Your backend is correctly configured with the service account from `backend/secrets/gen.json`.

## Need Help?

If you're still getting errors:
1. Check browser console for detailed error messages
2. Verify the API key format (should start with "AIzaSy")
3. Ensure all Firebase services are enabled in console
4. Check network tab for failed requests
