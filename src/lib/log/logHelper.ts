import { Instant } from "@js-joda/core";

function escapeHtml(unsafe: string): string {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

export function formatMessage(message: string): string {
  const urlRegex = /(https?:\/\/[^\s'"]+)/g;
  // Refined regex for Windows paths and Unix paths
  // 1. Windows drive: \b[a-zA-Z]:\\...
  // 2. %USERPROFILE%: %USERPROFILE%\\...
  // 3. Unix home: ~/...
  const pathRegex =
    /(\b[a-zA-Z]:\\[\\\w\s\.\-!@#$%^&()]+|%USERPROFILE%\\[\\\w\s\.\-!@#$%^&()]+|~[\/\w\s\.\-!@#$%^&()]+)/g;

  return escapeHtml(message)
    .replace(urlRegex, '<a class="anchor" href="$1" target="_blank">$1</a>')
    .replace(pathRegex, (match) => {
      // If it looks like it's inside an HTML tag (already replaced by urlRegex), skip it
      if (match.includes("://")) return match;
      return `<span class="path-link cursor-pointer underline text-accent hover:text-accent-hi" data-path="${match}">${match}</span>`;
    })
    .replace(/\r?\n/g, "<br>");
}

export function getLogClass(message: string): string {
  if (message.includes("[DEBUG]")) return "text-primary-500";
  if (message.includes("[INFO]")) return "text-success-500";
  if (message.includes("[WARNING]")) return "text-warning-500";
  if (message.includes("[ERROR]")) return "text-error-500";
  if (message.includes("[FATAL]")) return "text-error-950";
  return "text-primary-50";
}

function sanitizeMessage(message: string): string {
  // Regex to match Windows user-profile path: C:\Users\username\
  const userPathRegex = /C:\\Users\\[^\\]+\\/gi;
  return message.replace(userPathRegex, "%USERPROFILE%\\");
}

export function logMessageToTextDisplayCardItem(
  logMessage: LogMessage,
): TextDisplayCardItem {
  const sanitized = sanitizeMessage(logMessage.message);
  const formatted = formatMessage(sanitized);
  const message = `[${logMessage.level}] ${formatted}`;

  return {
    message,
    timestamp: Instant.parse(logMessage.timestamp),
    html_class: logMessage.html_class ?? getLogClass(message),
  };
}

export type TextDisplayCardItem = {
  message: string;
  timestamp: Instant;
  html_class: string;
};
