const fs = require('fs');
const { JSDOM } = require('jsdom');
const builder = require('junit-report-builder');

const html = fs.readFileSync('/templates/index.html', 'utf8');
const dom = new JSDOM(html, { runScripts: "outside-only" });
const { window } = dom;
global.window = window;
global.document = window.document;

require('/tests/test.js');

setTimeout(() => {
    const results = window.testResults || [];
    const suite = builder.testSuite().name('Frontend Tests');

    results.forEach((test) => {
        const tc = suite.testCase().name(test.name);
        if (!test.passed) {
            tc.failure(`Expected "${test.expected}", got "${test.actual}"`);
        }
    });

    builder.writeTo('junit.xml');
    console.log('✅ Tests done. Report saved to junit.xml');
}, 1000);
