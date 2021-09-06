(function () {
    const acorn = require("acorn");
    const escodegen = require("escodegen");
    const transformersModule = require("../pa/bugSeedingTransformers");
    const { ecmaVersion } = require("../util/config");
    const diffLib = require("diff");

    function genericTransformerTest(beforeCode, expectedCodes, transformer) {
        const origAST = acorn.parse(beforeCode, { locations: false, ranges: false, ecmaVersion: ecmaVersion });
        const origCode = escodegen.generate(origAST); // pretty print again for compatible formatting
        
        const patchMetaPairs = transformer(origAST, origCode);

        const foundExpectedIndices = [];
        for (let expectedIdx = 0; expectedIdx < expectedCodes.length; expectedIdx++) {
            let expectedCode = expectedCodes[expectedIdx];
            const expectedAST = acorn.parse(expectedCode, { locations: false, ranges: false, ecmaVersion: ecmaVersion });
            expectedCode = escodegen.generate(expectedAST); // pretty print again for compatible formatting
            for (let pairIdx = 0; pairIdx < patchMetaPairs.length; pairIdx++) {
                const [patch, meta] = patchMetaPairs[pairIdx];
                const patchedCode = diffLib.applyPatch(origCode, patch);
                // console.log("\nExpected:\n" + expectedCode + "\nFound:\n" + patchedCode);
                if (expectedCode == patchedCode) {
                    foundExpectedIndices.push([expectedIdx]);
                    expect(meta.kind).toEqual(transformer.name);
                    break;
                }
            }
        }

        expect(foundExpectedIndices.length).toEqual(expectedCodes.length);
    }

    test("remove a single subexpression", () => {
        let before = "if (c1 && c2) { foo(); }";
        let after1 = "if (c1) { foo(); }";
        genericTransformerTest(before, [after1], transformersModule.removeSubexpression);
    });

    test("remove multiple subexpressions", () => {
        let before = "if (c1 && c2) { foo(); } else { bar(); } other(); if (c3 || c4 || c5) { baz(); }";
        let after1 = "if (c1)       { foo(); } else { bar(); } other(); if (c3 || c4 || c5) { baz(); }";
        let after2 = "if (c1 && c2) { foo(); } else { bar(); } other(); if (c3 || c4)       { baz(); }";
        genericTransformerTest(before, [after1, after2], transformersModule.removeSubexpression);
    });

    test("remove subexpression (nothing to do because no top-level logical subexpressions)", () => {
        let before = "if (bar(x && y)) { foo(); }";
        genericTransformerTest(before, [], transformersModule.removeSubexpression);
    });

    test("remove then branch", () => {
        let before = "if (c1 && c2) { foo(); } else { bar(); }";
        let after1 = "bar();";
        genericTransformerTest(before, [after1], transformersModule.removeThenBranch);
    });

    test("remove then branch (more complex example)", () => {
        let before = "more(); if (c1 && c2) { foo(); } else { bar(); } code();";
        let after1 = "more(); bar(); code();";
        genericTransformerTest(before, [after1], transformersModule.removeThenBranch);
    });

    test("remove then branch (multi-statement example)", () => {
        let before = "if (c1) { foo(); } else { while (x) bar(); baz(); } ";
        let after1 = "while (x) bar(); baz();";
        genericTransformerTest(before, [after1], transformersModule.removeThenBranch);
    });

    test("remove then branch (nothing to do because no else branch)", () => {
        let before = "if (c1 && c2) { foo(); }";
        genericTransformerTest(before, [], transformersModule.removeThenBranch);
    });

    test("remove then branch (nothing do to because of directly nested if)", () => {
        let before = "while (true) if (c) { foo(); } else { bar(); }";
        genericTransformerTest(before, [], transformersModule.removeThenBranch);
    });

    test("remove if statement", () => {
        let before = "more(); if (c1) { foo(); } code();";
        let after1 = "more(); code();";
        genericTransformerTest(before, [after1], transformersModule.removeIfStmt);
    });

    test("remove if statement (nothing to do because if has else branch)", () => {
        let before = "more(); if (c1) { foo(); } else { bar(); } code();";
        genericTransformerTest(before, [], transformersModule.removeIfStmt);
    });

    test("remove if statement (two ifs, but one ignored due to direct nesting)", () => {
        let before = "more(); if (c1) if (c1) { foo(); } code();";
        let after1 = "more(); code();";
        genericTransformerTest(before, [after1], transformersModule.removeIfStmt);
    });

    test("remove guard", () => {
        let before = "more(); if (c1) { foo(); } code();";
        let after1 = "more(); foo(); code();";
        genericTransformerTest(before, [after1], transformersModule.removeGuard);
    });

    test("remove guard (two nested cases)", () => {
        let before = "more(); if (c1) { foo(); if (c2) { bar(); } } code();";
        let after1 = "more(); foo(); if (c2) { bar(); } code();";
        let after2 = "more(); if (c1) { foo(); bar(); } code();";
        genericTransformerTest(before, [after1, after2], transformersModule.removeGuard);
    });

    test("remove guard (nothing to do because else branch", () => {
        let before = "more(); if (c1) { foo(); } else { bar(); } code();";
        genericTransformerTest(before, [], transformersModule.removeGuard);
    });

})();
