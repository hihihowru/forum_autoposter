#!/bin/bash
set -e

echo "🔐 VPN Entrypoint Script Starting..."

# Check if VPN is enabled
if [ "$OPENVPN_ENABLED" != "true" ]; then
    echo "⏭️  VPN disabled, starting app directly..."
    exec "$@"
fi

# Check for required environment variables
if [ -z "$OPENVPN_USERNAME" ] || [ -z "$OPENVPN_PASSWORD" ]; then
    echo "❌ Error: OPENVPN_USERNAME and OPENVPN_PASSWORD must be set"
    exit 1
fi

# Check if .ovpn file exists
OVPN_FILE="/app/cmoney.ovpn"
if [ ! -f "$OVPN_FILE" ]; then
    echo "❌ Error: VPN config file not found at $OVPN_FILE"
    exit 1
fi

echo "✅ Found VPN config file: $OVPN_FILE"

# Create auth credentials file
echo "$OPENVPN_USERNAME" > /tmp/vpn-auth.txt
echo "$OPENVPN_PASSWORD" >> /tmp/vpn-auth.txt
chmod 600 /tmp/vpn-auth.txt

echo "🔌 Connecting to VPN..."

# Start OpenVPN in background
openvpn --config "$OVPN_FILE" \
    --auth-user-pass /tmp/vpn-auth.txt \
    --daemon \
    --log /tmp/openvpn.log \
    --writepid /tmp/openvpn.pid

# Wait for VPN connection (check for tun0 interface)
echo "⏳ Waiting for VPN connection..."
MAX_WAIT=30
WAITED=0

while [ $WAITED -lt $MAX_WAIT ]; do
    if ip addr show tun0 &>/dev/null; then
        echo "✅ VPN connected successfully!"

        # Show VPN IP
        VPN_IP=$(ip addr show tun0 | grep 'inet ' | awk '{print $2}' | cut -d'/' -f1)
        echo "📍 VPN IP: $VPN_IP"

        # Test connection to CMoney
        echo "🧪 Testing connection to anya.cmoney.tw..."
        if ping -c 1 -W 2 anya.cmoney.tw &>/dev/null; then
            echo "✅ Can reach anya.cmoney.tw"
        else
            echo "⚠️  Cannot ping anya.cmoney.tw (might still work)"
        fi

        break
    fi

    sleep 1
    WAITED=$((WAITED + 1))
    echo "   Waiting... (${WAITED}/${MAX_WAIT}s)"
done

if [ $WAITED -eq $MAX_WAIT ]; then
    echo "❌ VPN connection timeout after ${MAX_WAIT}s"
    echo "📋 OpenVPN logs:"
    cat /tmp/openvpn.log
    exit 1
fi

# Cleanup auth file
rm -f /tmp/vpn-auth.txt

echo "🚀 Starting application..."
exec "$@"
