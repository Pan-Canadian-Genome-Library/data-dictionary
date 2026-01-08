const fs = require('fs');
const path = require('path');

// Paths (relative to repo root)
const lecternPath = path.join('../../../lectern/pcgl', 'pcgl_lectern.json');

// Fixed values
const studyId = 'TEST-CA';
const participantId = 'BH31D721AW';
const geographicLocation = 'Missing - Not collected';
const sociodemDataCollection = '2024-01-15';
const genderAnotherGender = 'N/A';
const sexAnotherCategory = 'N/A';

// Configuration
const exportFormat = 'json';
const createRecords = 20;

const [nodePath, scriptPath, ...args] = process.argv;

const schemaNameArg = args[0];

if (!schemaNameArg) {
	console.error('Usage: node init.js <schema-name>');
	process.exit(1);
}

const outFilePath = path.join(
	__dirname,
	'.',
	`${schemaNameArg}.${exportFormat}`
);

function readJson(p) {
	return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function findFirstCodeList(obj) {
	if (!obj || typeof obj !== 'object') return null;
	if (Array.isArray(obj)) {
		for (const el of obj) {
			const found = findFirstCodeList(el);
			if (found) return found;
		}
		return null;
	}
	if (obj.codeList && Array.isArray(obj.codeList) && obj.codeList.length > 0) {
		return obj.codeList;
	}
	// recurse into properties
	for (const k of Object.keys(obj)) {
		try {
			const found = findFirstCodeList(obj[k]);
			if (found) return found;
		} catch (e) {
			// ignore
		}
	}
	return null;
}

function escapeCsv(val) {
	if (val == null) return '';
	const s = String(val);
	if (s.includes('"')) {
		// double-up quotes
		return '"' + s.replace(/"/g, '""') + '"';
	}
	if (s.includes(',') || s.includes('\n') || s.includes('\r')) {
		return '"' + s + '"';
	}
	return s;
}

function pickRandom(arr) {
	if (!Array.isArray(arr) || arr.length === 0) return null;
	return arr[Math.floor(Math.random() * arr.length)];
}

function generateAlphanumericId(length = 8) {
	const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
	let result = '';
	for (let i = 0; i < length; i++) {
		result += chars.charAt(Math.floor(Math.random() * chars.length));
	}
	return result;
}

function main() {
	const data = readJson(lecternPath);

	const schemas = data.schemas || [];
	let schema = schemas.find(
		(s) => s.name === schemaNameArg || s.displayName === schemaNameArg
	);
	if (!schema) schema = schemas[0];
	if (!schema) {
		console.error('No schema found in lectern.json');
		process.exit(1);
	}

	const fields = Array.isArray(schema.fields) ? schema.fields : [];

	const headers = [];
	// const row = [];

	for (const f of fields) {
		if (!f || !f.name) continue; // skip empty entries
		headers.push(f.name);
	}

	// Generate multiple rows based on createRecords
	const rows = [];
	for (let i = 0; i < createRecords; i++) {
		const newRow = [];
		for (const f of fields) {
			if (!f || !f.name) continue;

			// Generate random ID for unique identifier fields
			if (
				f.name === 'submitter_sociodem_id' &&
				schemaNameArg === 'sociodemographic'
			) {
				newRow.push(generateAlphanumericId(12));
				continue;
			} else if (
				f.name === 'submitter_participant_id' &&
				schemaNameArg === 'participant'
			) {
				newRow.push(generateAlphanumericId(10));
				continue;
			}

			// fixed values for study and participant IDs
			if (f.name === 'study_id') {
				newRow.push(studyId);
				continue;
			} else if (f.name === 'submitter_participant_id') {
				newRow.push(participantId);
				continue;
			} else if (f.name === 'geographic_location') {
				newRow.push(geographicLocation);
				continue;
			} else if (f.name === 'sociodem_date_collection') {
				newRow.push(sociodemDataCollection);
				continue;
			} else if (f.name === 'gender_another_gender') {
				newRow.push(genderAnotherGender);
				continue;
			} else if (f.name === 'sex_another_category') {
				newRow.push(sexAnotherCategory);
				continue;
			}

			// is an integer value:
			if (f.valueType === 'integer') {
				const randomInt = Math.floor(Math.random() * 100);
				newRow.push(randomInt);
				continue;
			}

			// Search for codeList anywhere under the field
			const codeList = findFirstCodeList(f.restrictions || f);
			if (codeList) {
				newRow.push(pickRandom(codeList));
				continue;
			}

			// Fallback to examples under meta.examples
			const examples =
				f.meta && Array.isArray(f.meta.examples) ? f.meta.examples : null;
			if (examples && examples.length > 0) {
				newRow.push(pickRandom(examples));
				continue;
			}

			// As last resort, use displayName or empty
			newRow.push(f.displayName || '');
		}
		rows.push(newRow);
	}

	if (exportFormat === 'csv') {
		const csv =
			headers.map(escapeCsv).join(',') +
			'\n' +
			rows.map((row) => row.map(escapeCsv).join(',')).join('\n') +
			'\n';
		fs.writeFileSync(outFilePath, csv, 'utf8');
		console.log(
			`Wrote ${createRecords} records to ${schemaNameArg} CSV:`,
			outFilePath
		);
	} else if (exportFormat === 'json') {
		const jsonArray = rows.map((row) => {
			const obj = {};
			for (let i = 0; i < headers.length; i++) {
				if (
					headers[i] === 'duo_permission' &&
					row[i] !== 'DUO:0000007 (disease specific research)'
				) {
					obj['disease_specific_modifier'] = '';
				} else if (headers[i] === 'ethnicity' && row[i] !== 'Free text input') {
					obj['ethnicity_another_category'] = '';
				} else if (
					headers[i] === 'race' &&
					row[i] !== 'Another Racial Category'
				) {
					obj['race_another_racial_category'] = '';
				} else if (headers[i] === 'gender' && row[i] !== 'Another Gender') {
					obj['gender_another_gender'] = '';
				} else if (
					headers[i] === 'sociodem_question' &&
					row[i] !== 'PCGL reference question' &&
					row[i] !== 'Another question'
				) {
					obj['sociodem_question_detail'] = '';
				} else if (headers[i] === 'sex_at_birth' && row[i] !== 'Another Sex') {
					obj['sex_another_category'] = '';
				}

				obj[headers[i]] = row[i];
			}
			return obj;
		});
		fs.writeFileSync(outFilePath, JSON.stringify(jsonArray, null, 2), 'utf8');
		console.log(
			`Wrote ${createRecords} records to ${schemaNameArg} JSON:`,
			outFilePath
		);
	} else {
		console.error('Unsupported export format:', exportFormat);
	}
}

main();
