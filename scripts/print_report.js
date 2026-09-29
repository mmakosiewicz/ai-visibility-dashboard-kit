// Print the HTML a filled report-template.html renders, without a browser (used by test_template.py).
// usage: node scripts/print_report.js proposal.html
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
const data = html.match(/<script type="application\/json" id="measurements">\n?([\s\S]*?)<\/script>/)[1];
const code = html.match(/<script>\n(const WORDING[\s\S]*?)<\/script>/)[1];
const main = { innerHTML: "" };
global.document = { documentElement: { outerHTML: "" }, getElementById: id => id === "report" ? main : { textContent: data },
  createElement: () => ({}), head: { appendChild() {} }, title: "" };
eval(code);
process.stdout.write(main.innerHTML);
