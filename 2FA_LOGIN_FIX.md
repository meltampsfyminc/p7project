# 2FA Login Fix - Test Guide

## Issues Fixed

### Issue 1: Missing Password in 2FA Form
**Problem:** When user entered 2FA code, the password field was not being passed back to the login view, causing "Invalid credentials" error.

**Solution:** Updated `login_view` to pass both `username` and `password` back to the template in the context variable, so they can be sent as hidden fields when the user submits their 2FA code.

### Issue 2: TOTP Token Validation
**Problem:** Token verification was too strict and didn't handle whitespace or validate input format.

**Solution:** 
- Added whitespace stripping: `.strip().replace(' ', '')`
- Added format validation: Must be 6 digits
- Increased time window tolerance from 1 to 2 steps (allows ~60 seconds of drift instead of ~30)

### Issue 3: Backup Code Handling
**Problem:** Backup codes weren't properly normalized, causing false negatives on valid codes.

**Solution:**
- Strip whitespace from input codes
- Convert to uppercase
- Normalize stored codes to match format
- Properly save after using a backup code

## How 2FA Login Now Works

### Step 1: Initial Login
```
User enters:
  Username: john
  Password: secret123
```

The system validates credentials and checks if 2FA is enabled.

### Step 2: 2FA Challenge (if enabled)
```
System returns login form with:
  - Hidden field: username = "john"
  - Hidden field: password = "secret123"
  - Visible field: totp_code (input)
```

User enters 6-digit code from Google Authenticator.

### Step 3: Verify 2FA Code
```
System receives:
  username: john (from hidden field)
  password: secret123 (from hidden field)
  totp_code: 123456 (from user input)

Verification process:
  1. Authenticate user with username + password again
  2. Get user's profile and check if 2FA is enabled
  3. Verify TOTP token against stored secret
  4. If invalid, try backup codes
  5. If both fail, return to 2FA form with error
  6. If valid, log user in and redirect to dashboard
```

## Testing 2FA

### To Enable 2FA:
1. Go to Dashboard → Manage 2FA
2. Click "Generate Secret"
3. Scan QR code with Google Authenticator
4. Enter code from authenticator (6 digits)
5. If correct, 2FA is enabled and backup codes are shown
6. Save backup codes in safe place

### To Test Login with 2FA:
1. Logout
2. Login with username and password
3. When prompted for 2FA code, enter current code from authenticator
4. Should successfully log in

### To Test Backup Code:
1. Logout
2. Login with username and password
3. Instead of 6-digit code, enter a backup code (e.g., "ABC12345")
4. Should successfully log in
5. That backup code is now consumed and can't be used again

## Technical Details

**Files Modified:**
- `properties/views.py` - Updated `login_view()` function
- `properties/models.py` - Improved `verify_totp()` and `use_backup_code()` methods

**Dependencies:**
- pyotp >= 2.9.0 (for TOTP generation/verification)
- qrcode >= 8.2 (for QR code generation)
- Pillow >= 12.0.0 (for QR code image rendering)

**TOTP Configuration:**
- Algorithm: HMAC-SHA1 (RFC 6238 standard)
- Time Step: 30 seconds
- Digits: 6
- Valid Window: 2 (allows ~60 seconds of server time skew)

## Troubleshooting

### "Invalid 2FA code" Error
- Check system clock (TOTP is time-based)
- Ensure you're using the correct authenticator app secret
- Try the code immediately (don't wait, codes expire in 30 seconds)
- Try a backup code instead

### Can't Scan QR Code
- Manually enter the secret key shown under the QR code
- Secret is displayed in base32 format (e.g., "JBSWY3DPEBLW64TMMQ......")

### Lost All Backup Codes
- Need to disable and re-enable 2FA to get new codes
- Once 2FA is disabled, you can log in normally without 2FA
