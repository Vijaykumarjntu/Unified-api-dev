// API configuration
const API_URL = 'http://localhost:8000/api/v1';

// Store tokens in memory (in production, use proper storage)
const tokens = {};

// DOM Elements
const connectBtns = document.querySelectorAll('.connect-btn');
const fetchBtns = document.querySelectorAll('.fetch-btn');
const outputEl = document.getElementById('output');
console.log(connectBtns);
console.log("connect b ut working");
// Helper: Log to output
function log(message, isError = false) {
    const timestamp = new Date().toLocaleTimeString();
    const prefix = isError ? '❌' : '✅';
    outputEl.textContent = `${prefix} [${timestamp}] ${message}\n${outputEl.textContent}`;
    if (isError) {
        console.error(message);
    } else {
        console.log(message);
    }
}

// Helper: Enable/disable fetch button
function setFetchEnabled(provider, enabled) {
    const btn = document.querySelector(`.fetch-btn[data-provider="${provider}"]`);
    if (btn) {
        btn.disabled = !enabled;
    }
}

// Step 1: Connect to provider (get OAuth URL)
async function connectProvider(provider) {
    try {
        log(`🔗 Connecting to ${provider}...`);
        const response = await fetch(`${API_URL}/auth/${provider}/login`);
        const data = await response.json();
        console.log("connection working");

        if (data.auth_url) {
            log(`📱 Opening ${provider} login page...`);
            // Store current provider in sessionStorage
            sessionStorage.setItem('oauth_provider', provider);
            // Redirect to OAuth page
            window.location.href = data.auth_url;
        } else {
            throw new Error('No auth URL received');
        }
    } catch (error) {
        log(`Failed to connect to ${provider}: ${error.message}`, true);
    }
}

// Step 2: Fetch contacts using stored token
async function fetchContacts(provider) {
    const token = tokens[provider];
    if (!token) {
        log(`🔐 Not connected to ${provider}. Click "Connect" first.`, true);
        return;
    }
    
    try {
        log(`📡 Fetching contacts from ${provider}...`);
        const response = await fetch(`${API_URL}/contacts?provider=${provider}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            log(`🎉 Got ${data.data?.length || 0} contacts from ${provider}`);
            outputEl.textContent = JSON.stringify(data.data, null, 2) + '\n\n' + outputEl.textContent;
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    } catch (error) {
        log(`Failed to fetch from ${provider}: ${error.message}`, true);
    }
}

// Handle OAuth callback (when redirected back)
async function handleOAuthCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('token');
    const provider = sessionStorage.getItem('oauth_provider');
    console.log("now we are inside the callback1");
    console.log(code);
    console.log(provider);
    log("now we are inside the call back call")
    log(provider)
    log(code)
    if (code && provider) {
        log(`🔄 Exchanging code for token with ${provider}...`);
        try {
            tokens[provider] = code;
            log(`🔐 Successfully connected to ${provider}!`);
            setFetchEnabled(provider, true);
            // Clean URL
            window.history.pushState({}, document.title, window.location.pathname);
        } catch (error) {
            log(`OAuth failed: ${error.message}`, true);
        }
        
        // sessionStorage.removeItem('oauth_provider');
    }
}

// Event listeners
connectBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const provider = btn.dataset.provider;
        connectProvider(provider);
    });
});

fetchBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const provider = btn.dataset.provider;
        fetchContacts(provider);
    });
});

// Check for OAuth callback on page load
handleOAuthCallback();

log('🚀 Unified API Demo Ready! Connect to a provider to start.');