# =============================================================================
# Environment Files Security Guide
# AI-Powered Misinformation Defense Platform
# =============================================================================

## 🚨 CRITICAL SECURITY NOTICE

**NEVER commit actual credentials to version control!**

The following files contain real credentials and should be added to .gitignore:
- `backend/.env`
- `frontend/.env.local`
- `frontend/.env`
- `backend/.env.development` (if contains real credentials)
- `frontend/.env.development` (if contains real credentials)

## 📂 Environment File Structure

```
backend/
├── .env.example          ✅ Safe to commit (template with placeholders)
├── .env.development      ⚠️  Contains real dev credentials - DO NOT COMMIT
├── .env                  ❌ Contains real credentials - DO NOT COMMIT
└── .env.production       ❌ Contains real prod credentials - DO NOT COMMIT

frontend/
├── .env.example          ✅ Safe to commit (template with placeholders)
├── .env.development      ⚠️  Contains real dev credentials - DO NOT COMMIT
├── .env.local            ❌ Contains real credentials - DO NOT COMMIT
└── .env                  ❌ Contains real credentials - DO NOT COMMIT
```

## 🔒 Credential Security Guidelines

### 1. **Backend Credentials**
```bash
# Move sensitive credentials to environment-specific files
cp backend/.env.development backend/.env        # For local development
```

### 2. **Frontend Credentials**
```bash
# Move sensitive credentials to environment-specific files
cp frontend/.env.development frontend/.env.local  # For local development
```

### 3. **Production Setup**
```bash
# Create production environment files (NEVER commit these)
cp backend/.env.example backend/.env.production
cp frontend/.env.example frontend/.env.production
# Edit with production values
```

## 🛡️ Security Best Practices

### Firebase Credentials
- **Backend**: Use service account JSON file in `backend/secrets/`
- **Frontend**: Use web app config keys (different from backend)
- **Never share**: Private keys, secrets, or service account files

### API Keys
- **Rotate regularly**: Update API keys every 90 days
- **Scope permissions**: Use least-privilege principle
- **Monitor usage**: Check for unauthorized access

### OAuth Credentials
- **Separate environments**: Use different OAuth apps for dev/prod
- **Restrict domains**: Configure authorized domains properly
- **Use secrets**: Never expose client secrets in frontend

## 📋 Setup Checklist

### For New Developers:
1. ✅ Copy `.env.example` files to create your local environment
2. ✅ Get credentials from team lead or secure vault
3. ✅ Verify `.env` files are in `.gitignore`
4. ✅ Test credentials work with mock services first
5. ✅ Enable real services only when needed

### For Production Deployment:
1. ✅ Use environment-specific credentials
2. ✅ Enable all security features (AUTH, HTTPS, CORS)
3. ✅ Rotate development credentials
4. ✅ Monitor for credential leaks
5. ✅ Set up proper backup and recovery

## 🔧 Environment Loading Order

### Backend (FastAPI)
1. `.env` (main environment file)
2. System environment variables (override .env)
3. Runtime configuration

### Frontend (Next.js)
1. `.env.local` (local development, highest priority)
2. `.env.development` (development environment)
3. `.env` (default)
4. System environment variables

## 🚨 Incident Response

### If Credentials Are Compromised:
1. **Immediately revoke** the compromised credentials
2. **Generate new** credentials
3. **Update all** environments with new credentials
4. **Audit logs** for unauthorized access
5. **Notify team** of the incident

### If Credentials Are Committed:
1. **Remove** from git history using `git-secrets` or similar
2. **Revoke** the exposed credentials
3. **Force push** cleaned history (if safe to do so)
4. **Generate new** credentials
5. **Audit** for potential misuse

## 📞 Support

If you need access to development credentials:
- Contact: Team Lead
- Secure sharing: Use encrypted vault or secure channel
- Documentation: Never share credentials via email or chat

---

**Remember: Security is everyone's responsibility!**