# Troubleshooting Standalone Frontend

## Current Status
- **Frontend Server**: Running on http://localhost:3001 ✅
- **Docker Services**: All running and healthy ✅
- **HTTP Response**: 200 OK ✅
- **CORS Configuration**: Fixed - backend allows standalone frontend ✅
- **API Connectivity**: All endpoints accessible ✅

## If Frontend Cannot Be Reached

### 1. Check Server Status
```bash
cd standalone-frontend
npm run dev
```
You should see:
```
➜ Local:   http://localhost:3001/
➜ Network: http://192.168.1.183:3001/
```

### 2. Test Connection
```bash
curl http://localhost:3001
```
Should return HTML content starting with `<!doctype html>`

### 3. Browser Access Issues

**Try these URLs:**
- http://localhost:3001
- http://127.0.0.1:3001
- Use the Network IP shown in the console (e.g., http://192.168.1.183:3001)

**Common Browser Issues:**
- Clear browser cache (Ctrl+F5 or Cmd+Shift+R)
- Try incognito/private browsing mode
- Check if browser is blocking localhost connections
- Disable browser extensions temporarily

### 4. Port Conflicts
Check if port 3001 is being used by another service:
```bash
# Windows
netstat -ano | findstr :3001

# Check if anything else is using the port
```

### 5. Firewall Issues
- Check Windows Firewall settings
- Temporarily disable antivirus software
- Check corporate firewall/proxy settings

### 6. Network Configuration
If accessing from another machine:
- Use the Network IP address shown in console
- Ensure firewall allows connections on port 3001
- Check if machine allows external connections

### 7. ESLint Errors (Non-blocking)
The ESLint errors shown are configuration issues but don't prevent the app from running. To fix:
```bash
# The .eslintrc.cjs has been copied but may need updates
cd standalone-frontend
# Edit .eslintrc.cjs if needed
```

### 8. Alternative Ports
If port 3001 is problematic, modify package.json:
```json
{
  "scripts": {
    "dev": "vite --port 3002"
  }
}
```

### 9. Check System Resources
```bash
# Check if system is low on memory
# Close other applications if needed
```

### 10. Development Server Logs
Look for error messages in the console where you ran `npm run dev`. Common issues:
- Permission errors
- Module not found errors
- Port binding failures

## Quick Test Commands

```bash
# 1. Check if server is running
curl -I http://localhost:3001

# 2. Check port usage
netstat -ano | findstr :3001

# 3. Test with different tool
wget http://localhost:3001 -O test.html

# 4. Check system connectivity
ping localhost
```

## Alternative Access Methods

1. **Use Network IP**: Check the console output for Network addresses
2. **Try different port**: Modify vite config to use port 3002
3. **Build and serve**: 
   ```bash
   npm run build
   npm run preview
   ```

## Status Check
Run this to verify all components:
```bash
# Check frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001
# Should return: 200

# Check backend services  
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health
# Should return: 200

curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health  
# Should return: 200
```

If all return 200, the services are running correctly and the issue is likely browser/network related.

## CORS Issues (RESOLVED)

The CORS (Cross-Origin Resource Sharing) issue has been resolved by:

1. **Created `.env` file** in `deployment/docker-compose/.env`:
   ```env
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3001
   ```

2. **Restarted Docker services** to pick up the configuration:
   ```bash
   cd deployment/docker-compose
   docker compose -f docker-compose.dev.yml -p pipeshub-ai down
   docker compose -f docker-compose.dev.yml -p pipeshub-ai up -d
   ```

3. **Verified CORS headers** are now present:
   - `Access-Control-Allow-Origin: http://localhost:3001`
   - `Access-Control-Allow-Credentials: true`

### Signs of CORS Issues:
- Browser console errors: "Access to XMLHttpRequest... has been blocked by CORS policy"
- Network tab shows preflight OPTIONS requests failing
- API calls return CORS-related error messages

### How to Fix CORS Issues:
1. Ensure the `.env` file exists in `deployment/docker-compose/`
2. Add your frontend URL to `ALLOWED_ORIGINS`
3. Restart the Docker services
4. Clear browser cache and try again