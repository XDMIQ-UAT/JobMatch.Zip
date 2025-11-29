import { SESClient, SendEmailCommand } from '@aws-sdk/client-ses';
import { logger } from '../utils/logger';
import { getSecrets } from '../config/secrets';
import { redactEmail } from '../utils/piiRedaction';

export class EmailService {
  private sesClient: SESClient | null = null;

  /**
   * Initialize SES client with credentials from Secret Manager
   */
  private async initializeSESClient(): Promise<void> {
    if (this.sesClient) {
      logger.info('SES client already initialized');
      return;
    }
    
    try {
      logger.info('🔄 Initializing SES client...');
      
      // Load secrets from Google Secret Manager
      const secrets = await getSecrets();
      
      // Debug logging
      logger.info('🔍 AWS_ACCESS_KEY_ID length:', secrets.AWS_ACCESS_KEY_ID?.length);
      logger.info('🔍 AWS_SECRET_ACCESS_KEY length:', secrets.AWS_SECRET_ACCESS_KEY?.length);
      logger.info('🔍 AWS_ACCESS_KEY_ID first 10 chars:', secrets.AWS_ACCESS_KEY_ID?.substring(0, 10));
      logger.info('🔍 AWS_SECRET_ACCESS_KEY first 10 chars:', secrets.AWS_SECRET_ACCESS_KEY?.substring(0, 10));
      
      // Validate credentials
      if (!secrets.AWS_ACCESS_KEY_ID || !secrets.AWS_SECRET_ACCESS_KEY) {
        throw new Error('AWS credentials not found in secrets');
      }
      
      if (secrets.AWS_ACCESS_KEY_ID.length !== 20) {
        throw new Error(`Invalid AWS Access Key ID length: ${secrets.AWS_ACCESS_KEY_ID.length}`);
      }
      
      if (secrets.AWS_SECRET_ACCESS_KEY.length !== 40) {
        throw new Error(`Invalid AWS Secret Access Key length: ${secrets.AWS_SECRET_ACCESS_KEY.length}`);
      }
      
      // Create SES client
      this.sesClient = new SESClient({
        region: process.env.SES_REGION || 'us-west-2',
        credentials: {
          accessKeyId: secrets.AWS_ACCESS_KEY_ID,
          secretAccessKey: secrets.AWS_SECRET_ACCESS_KEY,
        },
      });
      
      logger.info('✅ SES client initialized successfully');
      
    } catch (error) {
      logger.error('❌ Failed to initialize SES client:', error);
      throw error;
    }
  }

  /**
   * Send magic link email
   */
  async sendMagicLink(email: string, magicLink: string): Promise<void> {
    try {
      logger.info(`📧 Sending magic link to ${redactEmail(email)}`);
      
      // Initialize SES client
      await this.initializeSESClient();
      
      if (!this.sesClient) {
        throw new Error('SES client not initialized');
      }
      
      const fromEmail = process.env.SES_FROM_EMAIL || 'admin@futurelink.zip';
      
      logger.info(`📧 From email: ${fromEmail}`);
      logger.info(`📧 Magic link: ${magicLink}`);
      
      const params = {
        Source: fromEmail,
        Destination: { 
          ToAddresses: [email] 
        },
        Message: {
          Subject: { 
            Data: 'Your JobMatch AI Login Link', 
            Charset: 'UTF-8' 
          },
          Body: {
            Html: {
              Data: this.generateMagicLinkEmailHTML(magicLink),
              Charset: 'UTF-8',
            },
            Text: {
              Data: this.generateMagicLinkEmailText(magicLink),
              Charset: 'UTF-8',
            },
          },
        },
      };

      const command = new SendEmailCommand(params);
      
      logger.info('📧 Sending email via SES...');
      const result = await this.sesClient.send(command);
      
      logger.info(`✅ Magic link email sent successfully to ${redactEmail(email)}`);
      logger.info(`📧 Message ID: ${result.MessageId}`);
      
    } catch (error: any) {
      logger.error(`❌ Failed to send magic link email to ${redactEmail(email)}:`, error);
      throw new Error(`Failed to send magic link email: ${error.message}`);
    }
  }

  /**
   * Generate HTML email template for magic link
   */
  private generateMagicLinkEmailHTML(magicLink: string): string {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JobMatch AI Login</title>
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
          .container { max-width: 600px; margin: 0 auto; padding: 20px; }
          .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
          .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
          .button { display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
          .footer { text-align: center; margin-top: 20px; color: #666; font-size: 14px; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>🎯 JobMatch AI</h1>
            <p>Your AI-powered job matching assistant</p>
          </div>
          <div class="content">
            <h2>Welcome to JobMatch AI!</h2>
            <p>Click the button below to securely log in to your JobMatch AI account:</p>
            <a href="${magicLink}" class="button">🔗 Login to JobMatch AI</a>
            <p><strong>This link will expire in 15 minutes for security.</strong></p>
            <p>If you didn't request this login link, you can safely ignore this email.</p>
          </div>
          <div class="footer">
            <p>JobMatch AI - Making job matching smarter</p>
            <p>This is an automated message, please do not reply.</p>
          </div>
        </div>
      </body>
      </html>
    `;
  }

  /**
   * Generate plain text email template for magic link
   */
  private generateMagicLinkEmailText(magicLink: string): string {
    return `
JobMatch AI - Login Link

Welcome to JobMatch AI!

Click the link below to securely log in to your account:
${magicLink}

This link will expire in 15 minutes for security.

If you didn't request this login link, you can safely ignore this email.

---
JobMatch AI - Making job matching smarter
This is an automated message, please do not reply.
    `;
  }

  /**
   * Send welcome email after signup
   */
  async sendWelcomeEmail(email: string, anonymousId: string, assessmentUrl: string): Promise<void> {
    try {
      logger.info(`📧 Sending welcome email to ${redactEmail(email)}`);
      await this.initializeSESClient();
      
      if (!this.sesClient) {
        throw new Error('SES client not initialized');
      }
      
      const fromEmail = process.env.SES_FROM_EMAIL || 'admin@futurelink.zip';
      const baseUrl = process.env.FRONTEND_URL || 'https://jobmatch.zip';
      
      const params = {
        Source: fromEmail,
        Destination: { ToAddresses: [email] },
        Message: {
          Subject: { 
            Data: '👋 Welcome to JobMatch.zip - Let\'s Get Started!', 
            Charset: 'UTF-8' 
          },
          Body: {
            Html: {
              Data: this.generateWelcomeEmailHTML(anonymousId, assessmentUrl, baseUrl),
              Charset: 'UTF-8',
            },
            Text: {
              Data: this.generateWelcomeEmailText(anonymousId, assessmentUrl, baseUrl),
              Charset: 'UTF-8',
            },
          },
        },
      };

      const command = new SendEmailCommand(params);
      const result = await this.sesClient.send(command);
      
      logger.info(`✅ Welcome email sent successfully to ${redactEmail(email)}`);
      logger.info(`📧 Message ID: ${result.MessageId}`);
      
    } catch (error: any) {
      logger.error(`❌ Failed to send welcome email to ${redactEmail(email)}:`, error);
      throw new Error(`Failed to send welcome email: ${error.message}`);
    }
  }

  /**
   * Send assessment completion email
   */
  async sendAssessmentCompleteEmail(email: string, anonymousId: string, profileUrl: string): Promise<void> {
    try {
      logger.info(`📧 Sending assessment complete email to ${redactEmail(email)}`);
      await this.initializeSESClient();
      
      if (!this.sesClient) {
        throw new Error('SES client not initialized');
      }
      
      const fromEmail = process.env.SES_FROM_EMAIL || 'admin@futurelink.zip';
      const baseUrl = process.env.FRONTEND_URL || 'https://jobmatch.zip';
      
      const params = {
        Source: fromEmail,
        Destination: { ToAddresses: [email] },
        Message: {
          Subject: { 
            Data: '🎉 Assessment Complete - What Happens Next?', 
            Charset: 'UTF-8' 
          },
          Body: {
            Html: {
              Data: this.generateAssessmentCompleteEmailHTML(anonymousId, profileUrl, baseUrl),
              Charset: 'UTF-8',
            },
            Text: {
              Data: this.generateAssessmentCompleteEmailText(anonymousId, profileUrl, baseUrl),
              Charset: 'UTF-8',
            },
          },
        },
      };

      const command = new SendEmailCommand(params);
      const result = await this.sesClient.send(command);
      
      logger.info(`✅ Assessment complete email sent successfully to ${redactEmail(email)}`);
      logger.info(`📧 Message ID: ${result.MessageId}`);
      
    } catch (error: any) {
      logger.error(`❌ Failed to send assessment complete email to ${redactEmail(email)}:`, error);
      throw new Error(`Failed to send assessment complete email: ${error.message}`);
    }
  }

  /**
   * Send getting started reminder email
   */
  async sendGettingStartedReminder(email: string, anonymousId: string, assessmentUrl: string): Promise<void> {
    try {
      logger.info(`📧 Sending getting started reminder to ${redactEmail(email)}`);
      await this.initializeSESClient();
      
      if (!this.sesClient) {
        throw new Error('SES client not initialized');
      }
      
      const fromEmail = process.env.SES_FROM_EMAIL || 'admin@futurelink.zip';
      const baseUrl = process.env.FRONTEND_URL || 'https://jobmatch.zip';
      
      const params = {
        Source: fromEmail,
        Destination: { ToAddresses: [email] },
        Message: {
          Subject: { 
            Data: '💡 Quick Guide: Getting Started with JobMatch', 
            Charset: 'UTF-8' 
          },
          Body: {
            Html: {
              Data: this.generateGettingStartedEmailHTML(anonymousId, assessmentUrl, baseUrl),
              Charset: 'UTF-8',
            },
            Text: {
              Data: this.generateGettingStartedEmailText(anonymousId, assessmentUrl, baseUrl),
              Charset: 'UTF-8',
            },
          },
        },
      };

      const command = new SendEmailCommand(params);
      const result = await this.sesClient.send(command);
      
      logger.info(`✅ Getting started reminder sent successfully to ${redactEmail(email)}`);
      logger.info(`📧 Message ID: ${result.MessageId}`);
      
    } catch (error: any) {
      logger.error(`❌ Failed to send getting started reminder to ${redactEmail(email)}:`, error);
      throw new Error(`Failed to send getting started reminder: ${error.message}`);
    }
  }

  /**
   * Send assessment progress reminder
   */
  async sendAssessmentReminder(email: string, anonymousId: string, assessmentUrl: string): Promise<void> {
    try {
      logger.info(`📧 Sending assessment reminder to ${redactEmail(email)}`);
      await this.initializeSESClient();
      
      if (!this.sesClient) {
        throw new Error('SES client not initialized');
      }
      
      const fromEmail = process.env.SES_FROM_EMAIL || 'admin@futurelink.zip';
      const baseUrl = process.env.FRONTEND_URL || 'https://jobmatch.zip';
      
      const params = {
        Source: fromEmail,
        Destination: { ToAddresses: [email] },
        Message: {
          Subject: { 
            Data: '⏰ Finish Your Assessment - You\'re Almost There!', 
            Charset: 'UTF-8' 
          },
          Body: {
            Html: {
              Data: this.generateAssessmentReminderEmailHTML(anonymousId, assessmentUrl, baseUrl),
              Charset: 'UTF-8',
            },
            Text: {
              Data: this.generateAssessmentReminderEmailText(anonymousId, assessmentUrl, baseUrl),
              Charset: 'UTF-8',
            },
          },
        },
      };

      const command = new SendEmailCommand(params);
      const result = await this.sesClient.send(command);
      
      logger.info(`✅ Assessment reminder sent successfully to ${redactEmail(email)}`);
      logger.info(`📧 Message ID: ${result.MessageId}`);
      
    } catch (error: any) {
      logger.error(`❌ Failed to send assessment reminder to ${redactEmail(email)}:`, error);
      throw new Error(`Failed to send assessment reminder: ${error.message}`);
    }
  }

  /**
   * Send first match notification email
   */
  async sendFirstMatchEmail(email: string, anonymousId: string, matchUrl: string, matchDetails?: string): Promise<void> {
    try {
      logger.info(`📧 Sending first match notification to ${redactEmail(email)}`);
      await this.initializeSESClient();
      
      if (!this.sesClient) {
        throw new Error('SES client not initialized');
      }
      
      const fromEmail = process.env.SES_FROM_EMAIL || 'admin@futurelink.zip';
      const baseUrl = process.env.FRONTEND_URL || 'https://jobmatch.zip';
      
      const params = {
        Source: fromEmail,
        Destination: { ToAddresses: [email] },
        Message: {
          Subject: { 
            Data: '🎯 Great News - You Have a Match!', 
            Charset: 'UTF-8' 
          },
          Body: {
            Html: {
              Data: this.generateFirstMatchEmailHTML(anonymousId, matchUrl, matchDetails || '', baseUrl),
              Charset: 'UTF-8',
            },
            Text: {
              Data: this.generateFirstMatchEmailText(anonymousId, matchUrl, matchDetails || '', baseUrl),
              Charset: 'UTF-8',
            },
          },
        },
      };

      const command = new SendEmailCommand(params);
      const result = await this.sesClient.send(command);
      
      logger.info(`✅ First match email sent successfully to ${redactEmail(email)}`);
      logger.info(`📧 Message ID: ${result.MessageId}`);
      
    } catch (error: any) {
      logger.error(`❌ Failed to send first match email to ${redactEmail(email)}:`, error);
      throw new Error(`Failed to send first match email: ${error.message}`);
    }
  }

  /**
   * Generate HTML email template for welcome email
   */
  private generateWelcomeEmailHTML(anonymousId: string, assessmentUrl: string, baseUrl: string): string {
    const shortId = anonymousId.slice(0, 8);
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to JobMatch.zip</title>
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }
          .container { max-width: 600px; margin: 0 auto; padding: 20px; }
          .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
          .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
          .button { display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }
          .footer { text-align: center; margin-top: 20px; color: #666; font-size: 14px; }
          .highlight-box { background: #e8f4f8; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>👋 Welcome to JobMatch.zip!</h1>
            <p>Your AI-powered job matching assistant</p>
          </div>
          <div class="content">
            <h2>Hello! We're thrilled to have you here.</h2>
            <p>You've taken the first step toward finding opportunities that match your capabilities, not just your credentials.</p>
            
            <div class="highlight-box">
              <p><strong>🔒 Your Privacy Matters</strong></p>
              <p>Your anonymous ID: <code>${shortId}...</code></p>
              <p>We never reveal your real identity. Your capabilities speak for themselves.</p>
            </div>

            <h3>What Makes JobMatch Different?</h3>
            <ul>
              <li>✅ <strong>Capability-first matching</strong> - We focus on what you can do</li>
              <li>✅ <strong>Anonymous identity</strong> - Your privacy is protected</li>
              <li>✅ <strong>Human-reviewed matches</strong> - No automated spam</li>
              <li>✅ <strong>Direct connections</strong> - Talk to hiring managers directly</li>
            </ul>

            <h3>Next Steps</h3>
            <p>Complete your assessment to start receiving matches. It only takes a few minutes and helps us understand your capabilities better.</p>
            
            <div style="text-align: center;">
              <a href="${assessmentUrl}" class="button">🚀 Start Your Assessment</a>
            </div>

            <p style="margin-top: 30px; font-size: 14px; color: #666;">
              Questions? Text us at (626) 995-9974 or visit <a href="${baseUrl}/help">${baseUrl}/help</a>
            </p>
          </div>
          <div class="footer">
            <p>JobMatch.zip - Making job matching smarter</p>
            <p><a href="${baseUrl}/unsubscribe?email={{email}}">Unsubscribe</a> | <a href="${baseUrl}/privacy">Privacy Policy</a></p>
            <p style="font-size: 12px; color: #999;">This is an automated message, please do not reply.</p>
          </div>
        </div>
      </body>
      </html>
    `;
  }

  /**
   * Generate plain text email template for welcome email
   */
  private generateWelcomeEmailText(anonymousId: string, assessmentUrl: string, baseUrl: string): string {
    const shortId = anonymousId.slice(0, 8);
    return `
Welcome to JobMatch.zip!

Hello! We're thrilled to have you here.

You've taken the first step toward finding opportunities that match your capabilities, not just your credentials.

🔒 Your Privacy Matters
Your anonymous ID: ${shortId}...
We never reveal your real identity. Your capabilities speak for themselves.

What Makes JobMatch Different?
✅ Capability-first matching - We focus on what you can do
✅ Anonymous identity - Your privacy is protected
✅ Human-reviewed matches - No automated spam
✅ Direct connections - Talk to hiring managers directly

Next Steps
Complete your assessment to start receiving matches. It only takes a few minutes and helps us understand your capabilities better.

Start Your Assessment: ${assessmentUrl}

Questions? Text us at (626) 995-9974 or visit ${baseUrl}/help

---
JobMatch.zip - Making job matching smarter
Unsubscribe: ${baseUrl}/unsubscribe
Privacy Policy: ${baseUrl}/privacy

This is an automated message, please do not reply.
    `;
  }

  /**
   * Generate HTML email template for assessment complete email
   */
  private generateAssessmentCompleteEmailHTML(anonymousId: string, profileUrl: string, baseUrl: string): string {
    const shortId = anonymousId.slice(0, 8);
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Assessment Complete - JobMatch.zip</title>
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }
          .container { max-width: 600px; margin: 0 auto; padding: 20px; }
          .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
          .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
          .button { display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }
          .footer { text-align: center; margin-top: 20px; color: #666; font-size: 14px; }
          .success-box { background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>🎉 Congratulations!</h1>
            <p>Your Assessment is Complete</p>
          </div>
          <div class="content">
            <div class="success-box">
              <p><strong>Great job!</strong> You've completed your capability assessment.</p>
            </div>

            <h2>What Happens Next?</h2>
            <ol>
              <li><strong>AI Analysis</strong> - Our AI reviews your capabilities and preferences</li>
              <li><strong>Human Review</strong> - A real person validates potential matches (we never auto-match)</li>
              <li><strong>You Get Notified</strong> - When there's a good opportunity, we'll let you know</li>
            </ol>

            <h3>Timeline</h3>
            <p>You should start seeing matches within 24-48 hours. We take time to ensure quality matches, not quantity.</p>

            <h3>Enhance Your Profile</h3>
            <p>While you wait, consider adding more details to your profile:</p>
            <ul>
              <li>Link your portfolio or GitHub</li>
              <li>Add more projects you've worked on</li>
              <li>Update your work preferences</li>
            </ul>
            
            <div style="text-align: center;">
              <a href="${profileUrl}" class="button">✏️ Update Your Profile</a>
            </div>

            <p style="margin-top: 30px; font-size: 14px; color: #666;">
              Your anonymous ID: <code>${shortId}...</code> (save this to return later)
            </p>
          </div>
          <div class="footer">
            <p>JobMatch.zip - Making job matching smarter</p>
            <p><a href="${baseUrl}/unsubscribe?email={{email}}">Unsubscribe</a> | <a href="${baseUrl}/privacy">Privacy Policy</a></p>
            <p style="font-size: 12px; color: #999;">This is an automated message, please do not reply.</p>
          </div>
        </div>
      </body>
      </html>
    `;
  }

  /**
   * Generate plain text email template for assessment complete email
   */
  private generateAssessmentCompleteEmailText(anonymousId: string, profileUrl: string, baseUrl: string): string {
    const shortId = anonymousId.slice(0, 8);
    return `
🎉 Congratulations! Your Assessment is Complete

Great job! You've completed your capability assessment.

What Happens Next?
1. AI Analysis - Our AI reviews your capabilities and preferences
2. Human Review - A real person validates potential matches (we never auto-match)
3. You Get Notified - When there's a good opportunity, we'll let you know

Timeline
You should start seeing matches within 24-48 hours. We take time to ensure quality matches, not quantity.

Enhance Your Profile
While you wait, consider adding more details to your profile:
- Link your portfolio or GitHub
- Add more projects you've worked on
- Update your work preferences

Update Your Profile: ${profileUrl}

Your anonymous ID: ${shortId}... (save this to return later)

---
JobMatch.zip - Making job matching smarter
Unsubscribe: ${baseUrl}/unsubscribe
Privacy Policy: ${baseUrl}/privacy

This is an automated message, please do not reply.
    `;
  }

  /**
   * Generate HTML email template for getting started email
   */
  private generateGettingStartedEmailHTML(anonymousId: string, assessmentUrl: string, baseUrl: string): string {
    const shortId = anonymousId.slice(0, 8);
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Getting Started - JobMatch.zip</title>
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }
          .container { max-width: 600px; margin: 0 auto; padding: 20px; }
          .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
          .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
          .button { display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }
          .footer { text-align: center; margin-top: 20px; color: #666; font-size: 14px; }
          .tip-box { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>💡 Quick Guide</h1>
            <p>Getting Started with JobMatch.zip</p>
          </div>
          <div class="content">
            <h2>Hi there! 👋</h2>
            <p>We noticed you haven't started your assessment yet. Here's a quick guide to help you get started.</p>

            <h3>How It Works</h3>
            <ol>
              <li><strong>Complete Assessment</strong> - Tell us about your capabilities (5-10 minutes)</li>
              <li><strong>AI + Human Review</strong> - We analyze and validate matches</li>
              <li><strong>Get Matched</strong> - Receive quality opportunities</li>
            </ol>

            <div class="tip-box">
              <p><strong>💡 Pro Tip:</strong> The assessment focuses on what you CAN DO, not where you've worked or what degrees you have. Be honest about your capabilities!</p>
            </div>

            <h3>What We Ask</h3>
            <ul>
              <li>✅ Skills you have</li>
              <li>✅ Projects you've built</li>
              <li>✅ How you prefer to work</li>
            </ul>

            <h3>What We DON'T Ask</h3>
            <ul>
              <li>❌ Your name or personal info</li>
              <li>❌ Job history or company names</li>
              <li>❌ Degrees or certifications</li>
            </ul>
            
            <div style="text-align: center;">
              <a href="${assessmentUrl}" class="button">🚀 Start Assessment Now</a>
            </div>

            <p style="margin-top: 30px; font-size: 14px; color: #666;">
              Your anonymous ID: <code>${shortId}...</code>
            </p>
          </div>
          <div class="footer">
            <p>JobMatch.zip - Making job matching smarter</p>
            <p><a href="${baseUrl}/unsubscribe?email={{email}}">Unsubscribe</a> | <a href="${baseUrl}/privacy">Privacy Policy</a></p>
            <p style="font-size: 12px; color: #999;">This is an automated message, please do not reply.</p>
          </div>
        </div>
      </body>
      </html>
    `;
  }

  /**
   * Generate plain text email template for getting started email
   */
  private generateGettingStartedEmailText(anonymousId: string, assessmentUrl: string, baseUrl: string): string {
    const shortId = anonymousId.slice(0, 8);
    return `
Quick Guide: Getting Started with JobMatch.zip

Hi there! 👋

We noticed you haven't started your assessment yet. Here's a quick guide to help you get started.

How It Works
1. Complete Assessment - Tell us about your capabilities (5-10 minutes)
2. AI + Human Review - We analyze and validate matches
3. Get Matched - Receive quality opportunities

💡 Pro Tip: The assessment focuses on what you CAN DO, not where you've worked or what degrees you have. Be honest about your capabilities!

What We Ask
✅ Skills you have
✅ Projects you've built
✅ How you prefer to work

What We DON'T Ask
❌ Your name or personal info
❌ Job history or company names
❌ Degrees or certifications

Start Assessment Now: ${assessmentUrl}

Your anonymous ID: ${shortId}...

---
JobMatch.zip - Making job matching smarter
Unsubscribe: ${baseUrl}/unsubscribe
Privacy Policy: ${baseUrl}/privacy

This is an automated message, please do not reply.
    `;
  }

  /**
   * Generate HTML email template for assessment reminder email
   */
  private generateAssessmentReminderEmailHTML(anonymousId: string, assessmentUrl: string, baseUrl: string): string {
    const shortId = anonymousId.slice(0, 8);
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Finish Your Assessment - JobMatch.zip</title>
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }
          .container { max-width: 600px; margin: 0 auto; padding: 20px; }
          .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
          .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
          .button { display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }
          .footer { text-align: center; margin-top: 20px; color: #666; font-size: 14px; }
          .reminder-box { background: #e7f3ff; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>⏰ You're Almost There!</h1>
            <p>Finish Your Assessment</p>
          </div>
          <div class="content">
            <h2>Hi! 👋</h2>
            <p>We noticed you started your assessment but haven't finished yet. Don't worry - you're not alone! Many people start and come back to finish later.</p>

            <div class="reminder-box">
              <p><strong>Why complete your assessment?</strong></p>
              <ul>
                <li>🎯 Get matched with opportunities that fit your capabilities</li>
                <li>⏱️ Takes just 5-10 minutes to finish</li>
                <li>🔒 Your privacy is always protected</li>
                <li>✨ Better matches = better opportunities</li>
              </ul>
            </div>

            <h3>Common Concerns</h3>
            <p><strong>"I don't have time"</strong> - The rest takes less than 10 minutes!</p>
            <p><strong>"I'm not sure what to say"</strong> - Just be honest about what you can do. There are no wrong answers.</p>
            <p><strong>"Will my info be private?"</strong> - Yes! We use anonymous IDs and never reveal your real identity.</p>
            
            <div style="text-align: center;">
              <a href="${assessmentUrl}" class="button">🚀 Resume Assessment</a>
            </div>

            <p style="margin-top: 30px; font-size: 14px; color: #666;">
              Your progress is saved. Just click the button above to pick up where you left off.
            </p>
            <p style="font-size: 14px; color: #666;">
              Your anonymous ID: <code>${shortId}...</code>
            </p>
          </div>
          <div class="footer">
            <p>JobMatch.zip - Making job matching smarter</p>
            <p><a href="${baseUrl}/unsubscribe?email={{email}}">Unsubscribe</a> | <a href="${baseUrl}/privacy">Privacy Policy</a></p>
            <p style="font-size: 12px; color: #999;">This is an automated message, please do not reply.</p>
          </div>
        </div>
      </body>
      </html>
    `;
  }

  /**
   * Generate plain text email template for assessment reminder email
   */
  private generateAssessmentReminderEmailText(anonymousId: string, assessmentUrl: string, baseUrl: string): string {
    const shortId = anonymousId.slice(0, 8);
    return `
⏰ You're Almost There! Finish Your Assessment

Hi! 👋

We noticed you started your assessment but haven't finished yet. Don't worry - you're not alone! Many people start and come back to finish later.

Why complete your assessment?
🎯 Get matched with opportunities that fit your capabilities
⏱️ Takes just 5-10 minutes to finish
🔒 Your privacy is always protected
✨ Better matches = better opportunities

Common Concerns
"I don't have time" - The rest takes less than 10 minutes!
"I'm not sure what to say" - Just be honest about what you can do. There are no wrong answers.
"Will my info be private?" - Yes! We use anonymous IDs and never reveal your real identity.

Resume Assessment: ${assessmentUrl}

Your progress is saved. Just click the link above to pick up where you left off.

Your anonymous ID: ${shortId}...

---
JobMatch.zip - Making job matching smarter
Unsubscribe: ${baseUrl}/unsubscribe
Privacy Policy: ${baseUrl}/privacy

This is an automated message, please do not reply.
    `;
  }

  /**
   * Generate HTML email template for first match email
   */
  private generateFirstMatchEmailHTML(anonymousId: string, matchUrl: string, matchDetails: string, baseUrl: string): string {
    const shortId = anonymousId.slice(0, 8);
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>You Have a Match! - JobMatch.zip</title>
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }
          .container { max-width: 600px; margin: 0 auto; padding: 20px; }
          .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
          .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
          .button { display: inline-block; background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }
          .footer { text-align: center; margin-top: 20px; color: #666; font-size: 14px; }
          .match-box { background: #d4edda; border-left: 4px solid #28a745; padding: 20px; margin: 20px 0; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>🎯 Great News!</h1>
            <p>You Have Your First Match</p>
          </div>
          <div class="content">
            <div class="match-box">
              <h2 style="margin-top: 0;">🎉 Congratulations!</h2>
              <p>We found an opportunity that matches your capabilities!</p>
            </div>

            <h3>Why You Were Matched</h3>
            ${matchDetails ? `<p>${matchDetails}</p>` : '<p>Your capabilities align well with what this opportunity is looking for.</p>'}

            <h3>What Happens Next?</h3>
            <ol>
              <li><strong>Review the Match</strong> - Check out the details and see if it interests you</li>
              <li><strong>Respond Directly</strong> - Message the hiring manager through our platform</li>
              <li><strong>Stay Anonymous</strong> - Your identity remains protected until you choose to reveal it</li>
            </ol>

            <div style="text-align: center;">
              <a href="${matchUrl}" class="button">👀 View Match Details</a>
            </div>

            <p style="margin-top: 30px; font-size: 14px; color: #666;">
              <strong>Remember:</strong> This match was reviewed by a real person, not an algorithm. We only send you quality opportunities.
            </p>
            <p style="font-size: 14px; color: #666;">
              Your anonymous ID: <code>${shortId}...</code>
            </p>
          </div>
          <div class="footer">
            <p>JobMatch.zip - Making job matching smarter</p>
            <p><a href="${baseUrl}/unsubscribe?email={{email}}">Unsubscribe</a> | <a href="${baseUrl}/privacy">Privacy Policy</a></p>
            <p style="font-size: 12px; color: #999;">This is an automated message, please do not reply.</p>
          </div>
        </div>
      </body>
      </html>
    `;
  }

  /**
   * Generate plain text email template for first match email
   */
  private generateFirstMatchEmailText(anonymousId: string, matchUrl: string, matchDetails: string, baseUrl: string): string {
    const shortId = anonymousId.slice(0, 8);
    return `
🎯 Great News! You Have Your First Match

🎉 Congratulations!

We found an opportunity that matches your capabilities!

Why You Were Matched
${matchDetails || 'Your capabilities align well with what this opportunity is looking for.'}

What Happens Next?
1. Review the Match - Check out the details and see if it interests you
2. Respond Directly - Message the hiring manager through our platform
3. Stay Anonymous - Your identity remains protected until you choose to reveal it

View Match Details: ${matchUrl}

Remember: This match was reviewed by a real person, not an algorithm. We only send you quality opportunities.

Your anonymous ID: ${shortId}...

---
JobMatch.zip - Making job matching smarter
Unsubscribe: ${baseUrl}/unsubscribe
Privacy Policy: ${baseUrl}/privacy

This is an automated message, please do not reply.
    `;
  }

  /**
   * Generic email sender with custom content
   */
  async sendEmail(email: string, subject: string, htmlBody: string, textBody: string): Promise<void> {
    try {
      logger.info(`📧 Sending email to ${redactEmail(email)}: ${subject}`);
      await this.initializeSESClient();
      
      if (!this.sesClient) {
        throw new Error('SES client not initialized');
      }
      
      const fromEmail = process.env.SES_FROM_EMAIL || 'admin@futurelink.zip';
      
      const params = {
        Source: fromEmail,
        Destination: { ToAddresses: [email] },
        Message: {
          Subject: { Data: subject, Charset: 'UTF-8' },
          Body: {
            Html: { Data: htmlBody, Charset: 'UTF-8' },
            Text: { Data: textBody, Charset: 'UTF-8' },
          },
        },
      };

      const command = new SendEmailCommand(params);
      const result = await this.sesClient.send(command);
      
      logger.info(`✅ Email sent successfully to ${redactEmail(email)}`);
      logger.info(`📧 Message ID: ${result.MessageId}`);
      
    } catch (error: any) {
      logger.error(`❌ Failed to send email to ${redactEmail(email)}:`, error);
      throw new Error(`Failed to send email: ${error.message}`);
    }
  }

  /**
   * Test SES configuration
   */
  async testConfiguration(): Promise<boolean> {
    try {
      await this.initializeSESClient();
      
      if (!this.sesClient) {
        throw new Error('SES client not initialized');
      }
      
      const fromEmail = process.env.SES_FROM_EMAIL || 'admin@futurelink.zip';
      
      const params = {
        Source: fromEmail,
        Destination: { 
          ToAddresses: ['test@example.com'] 
        },
        Message: {
          Subject: { 
            Data: 'JobMatch AI - SES Test', 
            Charset: 'UTF-8' 
          },
          Body: {
            Text: {
              Data: 'This is a test email to verify SES configuration.',
              Charset: 'UTF-8',
            },
          },
        },
      };

      const command = new SendEmailCommand(params);
      await this.sesClient.send(command);
      
      logger.info('✅ SES configuration test successful');
      return true;
      
    } catch (error) {
      logger.error('❌ SES configuration test failed:', error);
      return false;
    }
  }
}