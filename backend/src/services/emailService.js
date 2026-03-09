'use strict';

const sgMail = require('@sendgrid/mail');
const axios = require('axios');
const { client: redis } = require('../config/redis');
const logger = require('../config/logger') || console;

if (process.env.SENDGRID_API_KEY && !process.env.SENDGRID_API_KEY.startsWith('your-')) {
  sgMail.setApiKey(process.env.SENDGRID_API_KEY);
}

const FROM_EMAIL = process.env.FROM_EMAIL || 'noreply@echosmart.io';

async function sendViaSendGrid(msg) {
  await sgMail.send(msg);
}

async function sendViaWhatsApp(phoneNumber, body) {
  // `phoneNumber` must be in E.164 format, e.g. "+14155001234"
  const accountSid = process.env.TWILIO_ACCOUNT_SID;
  const authToken = process.env.TWILIO_AUTH_TOKEN;
  if (!accountSid || accountSid.startsWith('your-')) return;

  await axios.post(
    `https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Messages.json`,
    new URLSearchParams({
      From: 'whatsapp:+14155238886',
      To: `whatsapp:${phoneNumber}`,
      Body: body,
    }),
    { auth: { username: accountSid, password: authToken } }
  );
}

function buildFooter(emailSignatureHtml) {
  return emailSignatureHtml
    ? `<br/><hr/>${emailSignatureHtml}`
    : '<br/><hr/><p style="color:#666;font-size:12px">EchoSmart IoT Monitoring</p>';
}

async function sendWelcomeEmail(to, verificationUrl, tenantName, emailSignatureHtml = '') {
  const msg = {
    to,
    from: FROM_EMAIL,
    subject: `Welcome to EchoSmart – Verify your email`,
    html: `
      <h2>Welcome to EchoSmart, ${tenantName}!</h2>
      <p>Please verify your email address to get started.</p>
      <p><a href="${verificationUrl}" style="background:#22c55e;color:white;padding:10px 20px;border-radius:5px;text-decoration:none">Verify Email</a></p>
      <p>This link expires in 24 hours.</p>
      ${buildFooter(emailSignatureHtml)}
    `,
  };
  try {
    await sendViaSendGrid(msg);
  } catch (err) {
    logger.error && logger.error('SendGrid error:', err.message);
    await sendViaWhatsApp(to, `Welcome to EchoSmart! Verify your email: ${verificationUrl}`);
  }
}

async function sendCriticalAlert(to, sensorName, alertMessage, tenantSettings = {}) {
  const msg = {
    to,
    from: FROM_EMAIL,
    subject: `🚨 Critical Alert: ${sensorName}`,
    html: `
      <h2 style="color:#ef4444">Critical Alert from ${sensorName}</h2>
      <p>${alertMessage}</p>
      <p>Please check your EchoSmart dashboard immediately.</p>
      ${buildFooter(tenantSettings.email_signature_html)}
    `,
  };
  try {
    await sendViaSendGrid(msg);
  } catch (err) {
    logger.error && logger.error('SendGrid error:', err.message);
    await sendViaWhatsApp(to, `Critical Alert from ${sensorName}: ${alertMessage}`);
  }
}

async function sendReportReady(to, reportUrl) {
  const msg = {
    to,
    from: FROM_EMAIL,
    subject: 'Your EchoSmart Report is Ready',
    html: `
      <h2>Your report is ready</h2>
      <p><a href="${reportUrl}">Download Report</a></p>
      ${buildFooter('')}
    `,
  };
  try {
    await sendViaSendGrid(msg);
  } catch (err) {
    logger.error && logger.error('SendGrid error:', err.message);
  }
}

async function sendPasswordReset(to, resetUrl) {
  const msg = {
    to,
    from: FROM_EMAIL,
    subject: 'EchoSmart Password Reset',
    html: `
      <h2>Reset your password</h2>
      <p>Click the link below to reset your password. This link expires in 1 hour.</p>
      <p><a href="${resetUrl}" style="background:#22c55e;color:white;padding:10px 20px;border-radius:5px;text-decoration:none">Reset Password</a></p>
      <p>If you did not request this, ignore this email.</p>
      ${buildFooter('')}
    `,
  };
  try {
    await sendViaSendGrid(msg);
  } catch (err) {
    logger.error && logger.error('SendGrid error:', err.message);
  }
}

async function processEmailQueue() {
  while (true) {
    try {
      const item = await redis.brPop('email:queue', 5);
      if (!item) continue;
      const job = JSON.parse(item.element);
      switch (job.type) {
        case 'welcome':
          await sendWelcomeEmail(job.to, job.verificationUrl, job.tenantName || '', job.emailSignatureHtml);
          break;
        case 'critical_alert':
          await sendCriticalAlert(job.to, job.sensorName, job.alertMessage, job.tenantSettings);
          break;
        case 'report_ready':
          await sendReportReady(job.to, job.reportUrl);
          break;
        case 'password_reset':
          await sendPasswordReset(job.to, job.resetUrl);
          break;
        default:
          logger.warn && logger.warn('Unknown email job type:', job.type);
      }
    } catch (err) {
      if (err.message && err.message.includes('Connection is closed')) {
        await new Promise((r) => setTimeout(r, 1000));
      } else {
        logger.error && logger.error('Email queue error:', err.message);
      }
    }
  }
}

module.exports = { sendWelcomeEmail, sendCriticalAlert, sendReportReady, sendPasswordReset, processEmailQueue };
