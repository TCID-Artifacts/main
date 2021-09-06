(function () {

    const extractor = require("../pa/conditionalExtraction");

    function genericExtractorTest(code, expectedExamples) {
        const examples = extractor.extractExamples(code, "testFile.js");
        expect(expectedExamples.length).toEqual(examples.length);
        for (let expExIdx = 0; expExIdx < expectedExamples.length; expExIdx++) {
            const expEx = expectedExamples[expExIdx];
            const expExJSON = JSON.stringify(expEx);
            let found = false;
            for (let exIdx = 0; exIdx < examples.length; exIdx++) {
                const ex = examples[exIdx];
                const exJSON = JSON.stringify(ex);
                if (expExJSON === exJSON) {
                    found = true;
                    break;
                }
            }
            expect(found).toBeTruthy();
        }
    }

    test("simple condition", () => {
        const code = "if (c) { bar(); }";
        const examples = [
            {
                "consequent": "{ bar(); }",
                "condition": "c",
                "correctCondition": "c",
                "meta": {
                    "kind": "correctCondition",
                    "file": "testFile.js"
                }
            }
        ];
        genericExtractorTest(code, examples);
    });

    test("logical and", () => {
        const code = "if (c && d) { bar(); }";
        const examples = [
            {
                "consequent": "{ bar(); }",
                "condition": "c && d",
                "correctCondition": "c && d",
                "meta": {
                    "kind": "correctCondition",
                    "file": "testFile.js"
                }
            },
            {
                "consequent": "{ bar(); }",
                "condition": "c",
                "correctCondition": "c && d",
                "meta": {
                    "kind": "incompleteCondition",
                    "file": "testFile.js"
                }
            },
            {
                "consequent": "{ bar(); }",
                "condition": "d",
                "correctCondition": "c && d",
                "meta": {
                    "kind": "incompleteCondition",
                    "file": "testFile.js"
                }
            }
        ];
        genericExtractorTest(code, examples);
    });

})();