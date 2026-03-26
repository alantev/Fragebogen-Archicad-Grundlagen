// ─── Configuration ───────────────────────────────────────────────────────────
// Run setupConfig() once from the Apps Script editor to store the Sheet ID
// in Script Properties. After that it is read automatically at runtime.

var SHEET_ID = '19TXZmPcFyCLwyVIAEnJqHMhaF542UYf-8VdqsVxyXAI';

/**
 * One-time setup: saves the Sheet ID into Script Properties.
 * Run this manually once from the Apps Script editor (Run → setupConfig).
 */
function setupConfig() {
  PropertiesService.getScriptProperties().setProperty('SHEET_ID', SHEET_ID);
  Logger.log('Config saved. SHEET_ID = ' + SHEET_ID);
}

/**
 * Returns the configured Google Sheet.
 * Reads SHEET_ID from Script Properties (set by setupConfig).
 */
function getSheet() {
  var sheetId = PropertiesService.getScriptProperties().getProperty('SHEET_ID');
  if (!sheetId) throw new Error('SHEET_ID not set. Run setupConfig() first.');
  return SpreadsheetApp.openById(sheetId).getActiveSheet();
}

// ─── Web App ─────────────────────────────────────────────────────────────────

/**
 * doGet: returns a simple health-check (the form itself is hosted on GitHub Pages).
 */
function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({ status: 'ok', message: 'Fragebogen API running' }))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * doPost: receives form submission from GitHub Pages form and writes to Google Sheet.
 *
 * Expected JSON body:
 * {
 *   respondent_name:  string,
 *   respondent_email: string,
 *   submitted_at:     ISO string,
 *   answers: [
 *     { id, category, L1, L3, items: [{ label, rating }] }
 *   ]
 * }
 *
 * Sheet columns:
 *   Timestamp | Name | E-Mail | Submitted At | Category | L1 | L3 | Item | Rating
 *   (one row per answered item)
 */
function doPost(e) {
  try {
    var sheet = getSheet();
    var raw   = e.postData.contents;
    // support both JSON body and form-encoded "payload=..."
    var data  = (e.postData.type === 'application/x-www-form-urlencoded')
                ? JSON.parse(decodeURIComponent(raw.replace(/^payload=/, '')))
                : JSON.parse(raw);

    var name        = data.respondent_name  || '';
    var email       = data.respondent_email || '';
    var submittedAt = data.submitted_at     || new Date().toISOString();
    var now         = new Date();

    // Ensure header row exists
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        'Timestamp', 'Name', 'E-Mail', 'Submitted At',
        'ID', 'Kategorie', 'L1', 'L3', 'Thema', 'Bewertung'
      ]);
    }

    // One row per item
    var rows = [];
    (data.answers || []).forEach(function(group) {
      (group.items || []).forEach(function(item) {
        rows.push([
          now,
          name,
          email,
          submittedAt,
          group.id       || '',
          group.category || '',
          group.L1       || '',
          group.L3       || '',
          item.label     || '',
          item.rating !== null && item.rating !== undefined ? item.rating : ''
        ]);
      });
    });

    if (rows.length > 0) {
      sheet.getRange(sheet.getLastRow() + 1, 1, rows.length, rows[0].length)
           .setValues(rows);
    }

    return ContentService
      .createTextOutput(JSON.stringify({ status: 'ok', rows_written: rows.length }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', error: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}