/**
 * Chat Prompts Configuration
 * 
 * Edit these messages to customize the default chat experience.
 * Changes will be reflected after rebuilding the frontend.
 */

export const ChatPrompts = {
  // Welcome message for unauthenticated users
  welcomeUnauthenticated: `Hi! \ud83d\udc4b Welcome to JobMatch - AI job matching for LLC owners.

I can help you find opportunities that match your skills. To get started, [CREATE_YOUR_ACCOUNT] to unlock all features.

We protect your privacy with anonymous identity.`,

  // Welcome message for authenticated users
  welcomeAuthenticated: (providerName: string) => `Welcome back! 🎉 Great to see you again!

You're authenticated via ${providerName}, and your anonymous identity is secure. I'm here to help you discover job opportunities that match your AI capabilities.

What would you like to do today?
• Explore job matches
• Update your profile
• Add more authentication methods
• Start an assessment

Just let me know what you'd like to explore!`,

  // Email authentication prompts
  email: {
    prompt: `📧 **Email Authentication**

Great choice! I'll send you a magic link - no password needed.

**Please enter your email address in the chat below:**`,
    
    invalidFormat: `❌ That doesn't look like a valid email address. Please enter your email in the format: yourname@example.com`,
    
    acknowledge: (email: string) => `Got it! I'll send a magic link to **${email}**.`,
    
    sending: (email: string) => `⏳ Sending magic link to **${email}**...`,
    
    sent: (email: string) => `✅ **Magic link sent!**

I've sent a magic link to **${email}**.

**Next steps:**
1. Check your email inbox (and spam folder just in case)
2. Click the link in the email
3. You'll be redirected back here, authenticated and ready to go!

The link is valid for 24 hours. If you don't see the email within a few minutes, you can request a new one.`,
    
    error: (errorMessage: string) => `❌ **Unable to send magic link**

${errorMessage}

Please try again or choose a different authentication method.`
  },

  // SMS authentication prompts
  sms: {
    prompt: `📱 **SMS/VoIP Authentication**

Great choice! I'll send you a verification code via SMS.

**Please enter your phone number in the chat below (e.g., +1234567890):**`,
    
    invalidFormat: `❌ That doesn't look like a valid phone number. Please include the country code (e.g., +1 for US).`,
    
    sending: (phone: string) => `⏳ Sending verification code to **${phone}**...`,
    
    sent: (phone: string) => `✅ **Verification code sent!**

I've sent a 6-digit code to **${phone}**.

**Please enter the code in the chat below:**`,
    
    verifying: `⏳ Verifying your code...`,
    
    success: `✅ **Phone verified!**

Great! Your phone number has been verified. Setting up your anonymous identity...`,
    
    error: (errorMessage: string) => `❌ **Verification failed**

${errorMessage}

Please try again or request a new code.`
  },

  // Social provider redirect
  socialRedirect: (providerName: string) => `Great choice! Let's get you authenticated with ${providerName}. Redirecting you to the authentication page...`,

  // General errors
  errors: {
    networkError: `❌ **Connection Error**

Unable to connect to the server. Please check your internet connection and try again.`,
    
    genericError: `❌ **Something went wrong**

An unexpected error occurred. Please try again or contact support if the issue persists.`
  }
}

// Authentication providers configuration
export const AUTH_PROVIDERS = [
  { id: 'linkedin', name: 'LinkedIn', icon: '💼' },
  { id: 'microsoft', name: 'Microsoft', icon: '🪟' },
  { id: 'facebook', name: 'Facebook', icon: '📘' },
  { id: 'google', name: 'Google', icon: '🔍' },
  { id: 'apple', name: 'Apple', icon: '🍎' },
  { id: 'email', name: 'Email', icon: '📧' },
  { id: 'sms', name: 'SMS/VoIP', icon: '📱' }
]
