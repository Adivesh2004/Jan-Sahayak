# Telegram Bot Connection Timeout - Troubleshooting Guide

## Issue
```
telegram.error.TimedOut: Timed out
httpcore.ConnectTimeout
```

The bot cannot connect to Telegram's servers.

## Possible Causes & Solutions

### 1. **Firewall/Antivirus Blocking Connection**

**Check:**
- Windows Firewall might be blocking Python
- Antivirus might be blocking the connection

**Solution:**
```powershell
# Add Python to Windows Firewall (Run as Administrator)
netsh advfirewall firewall add rule name="Python" dir=in action=allow program="C:\Python314\python.exe" enable=yes
```

### 2. **VPN/Proxy Required**

If you're behind a corporate firewall or in a country where Telegram is blocked:

**Solution A - Use Proxy:**
Edit `src/telegram_bot.py`, add proxy configuration:

```python
from telegram.request import HTTPXRequest

# In main() function, before creating application:
request = HTTPXRequest(
    proxy_url="http://your-proxy-server:port",  # Your proxy
    connection_pool_size=8,
)

application = Application.builder().token(token).request(request).build()
```

**Solution B - Use VPN:**
- Connect to a VPN that allows Telegram access
- Try the bot again

### 3. **Network Connectivity**

**Test Telegram API connectivity:**
```powershell
# Test if you can reach Telegram
curl https://api.telegram.org

# Test with your bot token
curl "https://api.telegram.org/bot8432248120:AAHUO9PtBdVvaI6g7v-_GtsOx1rv_3IikBk/getMe"
```

If these fail, your network cannot reach Telegram servers.

### 4. **Increase Timeout**

Temporarily increase connection timeout to see if it's just slow:

Edit `src/telegram_bot.py`:

```python
from telegram.request import HTTPXRequest

# In main() function:
request = HTTPXRequest(
    connection_pool_size=8,
    connect_timeout=30.0,  # Increase from default 5s
    read_timeout=30.0
)

application = Application.builder().token(token).request(request).build()
```

### 5. **Check Internet Connection**

```powershell
# Test basic connectivity
ping 8.8.8.8
ping google.com
```

### 6. **Telegram Might Be Blocked**

If Telegram is blocked in your region/network:

**Option 1:** Use a different network (mobile hotspot, different WiFi)
**Option 2:** Use VPN
**Option 3:** Use proxy server

---

## Quick Fix to Try First

Try this modified bot code with longer timeouts:

```python
# Add this in main() function before Application.builder()
from telegram.request import HTTPXRequest

request = HTTPXRequest(
    connection_pool_size=8,
    connect_timeout=60.0,  # 60 seconds
    read_timeout=60.0,
    pool_timeout=60.0
)

application = Application.builder().token(token).request(request).build()
```

---

## Alternative: Webhook Mode (if polling fails)

If polling continues to fail, you can switch to webhook mode (requires public HTTPS URL).

---

## Verify Bot Token

Test your bot token manually:
```powershell
curl "https://api.telegram.org/bot8432248120:AAHUO9PtBdVvaI6g7v-_GtsOx1rv_3IikBk/getMe"
```

If you get a response, the token is valid. If timeout, it's a network issue.

---

## Most Likely Solution

Based on the error, this is most likely:
1. **Firewall blocking** - Allow Python through firewall
2. **VPN/Proxy needed** - Use VPN or configure proxy
3. **Telegram blocked** - Use different network or VPN

Try these in order!
