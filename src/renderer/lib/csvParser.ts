/**
 * CSV Parser Utility
 * ===================
 * Robust CSV parser that handles quoted fields with commas,
 * newlines inside quotes, and escaped quotes.
 */

export interface ParsedCSV {
  headers: string[];
  rows: Record<string, string>[];
}

/**
 * Parse a CSV string into an array of objects.
 * Handles quoted fields properly (important for columns like
 * Categorias and Topico which contain Python lists/dicts with commas).
 */
export function parseCSV(text: string): ParsedCSV {
  const rows: string[][] = [];
  let currentRow: string[] = [];
  let currentField = '';
  let inQuotes = false;
  let i = 0;

  while (i < text.length) {
    const char = text[i];
    const nextChar = text[i + 1];

    if (inQuotes) {
      if (char === '"' && nextChar === '"') {
        // Escaped quote
        currentField += '"';
        i += 2;
      } else if (char === '"') {
        // End of quoted field
        inQuotes = false;
        i++;
      } else {
        currentField += char;
        i++;
      }
    } else {
      if (char === '"' && currentField === '') {
        // Start of quoted field
        inQuotes = true;
        i++;
      } else if (char === ',') {
        currentRow.push(currentField);
        currentField = '';
        i++;
      } else if (char === '\n' || (char === '\r' && nextChar === '\n')) {
        currentRow.push(currentField);
        currentField = '';
        if (currentRow.some((f) => f.trim() !== '') || currentRow.length > 1) {
          rows.push(currentRow);
        }
        currentRow = [];
        i += char === '\r' ? 2 : 1;
      } else {
        currentField += char;
        i++;
      }
    }
  }

  // Handle last field/row
  if (currentField !== '' || currentRow.length > 0) {
    currentRow.push(currentField);
    if (currentRow.some((f) => f.trim() !== '') || currentRow.length > 1) {
      rows.push(currentRow);
    }
  }

  if (rows.length === 0) {
    return { headers: [], rows: [] };
  }

  const headers = rows[0].map((h) => h.trim());
  const dataRows = rows.slice(1).map((row) => {
    const obj: Record<string, string> = {};
    headers.forEach((header, idx) => {
      obj[header] = row[idx]?.trim() ?? '';
    });
    return obj;
  });

  return { headers, rows: dataRows };
}

/**
 * Parse a Python list string representation into a JavaScript array.
 * e.g. "['Transporte', 'Personal y servicio']" -> ["Transporte", "Personal y servicio"]
 */
export function parsePythonList(value: string): string[] {
  if (!value || value === '[]' || value === 'nan' || value === '') return [];

  // Remove outer brackets
  const inner = value.replace(/^\[|\]$/g, '').trim();
  if (!inner) return [];

  // Match quoted strings (single or double)
  const matches = inner.match(/(?:'([^']*)'|"([^"]*)")/g);
  if (!matches) return [];

  return matches.map((m) => m.replace(/^['"]|['"]$/g, '').trim()).filter(Boolean);
}

/**
 * Parse a Python dict string representation into a JavaScript object.
 * e.g. "{'Transporte': 'Servicio de ferry', 'Personal y servicio': 'Atención al cliente'}"
 * -> { "Transporte": "Servicio de ferry", "Personal y servicio": "Atención al cliente" }
 */
export function parsePythonDict(value: string): Record<string, string> {
  if (!value || value === '{}' || value === 'nan' || value === '') return {};

  const result: Record<string, string> = {};

  // Match key-value pairs, handling both properly formatted and malformed quote combinations
  // Handles: 'key': 'value', "key": "value", ""'key'"": 'value', etc.
  const pairRegex = /["']*['"]([^'"]+)['"]["']*\s*:\s*["']*['"]([^'"]+)['"]["']*/g;
  let match;
  while ((match = pairRegex.exec(value)) !== null) {
    // Clean the key and value by removing any remaining quotes and trimming
    const key = match[1]?.replace(/^["']+|["']+$/g, '').trim() ?? '';
    const val = match[2]?.replace(/^["']+|["']+$/g, '').trim() ?? '';
    if (key && val) result[key] = val;
  }

  return result;
}
