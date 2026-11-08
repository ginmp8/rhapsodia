import fs from 'node:fs';

// Source layouts centralize immutable notices; standalone ZIPs restore local
// copies at their original names to keep independent distributions complete.
const notices = [
  ['NOTICE', 'licenses/notices/archify.txt'],
  ['LICENSE', 'licenses/third-party/archify-apache-2.0.txt'],
  ['LICENSE-MIT', 'licenses/third-party/archify-historical-MIT.txt'],
  ['THIRD_PARTY_NOTICES.md', 'licenses/notices/archify-third-party.md'],
];
function readNotice(name, canonical) {
  const local = new URL('../../' + name, import.meta.url);
  const central = new URL('../../../../' + canonical, import.meta.url);
  const source = fs.existsSync(local) ? local : central;
  return name + '\n' + fs.readFileSync(source, 'utf8').trimEnd();
}
export const softwareNotices = notices.map(([name, canonical]) => readNotice(name, canonical)).join('\n\n');
// JSON data preserves the exact notice text without HTML/script delimiters.
export const softwareNoticesHtml = '<script type="application/json" id="archify-software-notices">' + JSON.stringify(softwareNotices).replace(/</g, '\\u003c') + '</script>';
