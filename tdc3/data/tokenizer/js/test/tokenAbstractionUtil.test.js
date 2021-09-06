(function () {

    const jsExtractionUtil = require("../pa/jsExtractionUtil");
    const abstraction = require("../pa/tokenAbstractionUtil");

    test("single sequence", () => {
        const code = "if ( c > 4 ) { bar ( c , 3 , 4 ) ; }";
        const expected = "if ( ID1 > LIT1 ) { ID2 ( ID1 , LIT2 , LIT1 ) ; }";
        const tokens = jsExtractionUtil.getTokens(code);
        abstraction.abstractIdsLits([tokens]);
        const abstractedCode = jsExtractionUtil.tokensToStrings(tokens).join(" ");
        expect(abstractedCode).toEqual(expected);
    });

    test("two sequences", () => {
        const code1 = "if ( c > 4 ) { bar ( c , 3 , 4 ) ; }";
        const code2 = "c !== 3";
        const expected1 = "if ( ID1 > LIT1 ) { ID2 ( ID1 , LIT2 , LIT1 ) ; }";
        const expected2 = "ID1 !== LIT2";
        const tokens1 = jsExtractionUtil.getTokens(code1);
        const tokens2 = jsExtractionUtil.getTokens(code2);
        abstraction.abstractIdsLits([tokens1, tokens2]);
        const abstractedCode1 = jsExtractionUtil.tokensToStrings(tokens1).join(" ");
        const abstractedCode2 = jsExtractionUtil.tokensToStrings(tokens2).join(" ");
        expect(abstractedCode1).toEqual(expected1);
        expect(abstractedCode2).toEqual(expected2);
    });

})();