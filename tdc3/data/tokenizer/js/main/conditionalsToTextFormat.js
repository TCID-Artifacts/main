(function () {

    const { ArgumentParser } = require('argparse');
    const fs = require("fs");
    const jsExtractionUtil = require("../pa/jsExtractionUtil");
    const tokenAbstractionUtil = require("../pa/tokenAbstractionUtil");

    const parser = new ArgumentParser({
        description: "Transform JSON files with extracted conditionals into text format understood by OpenNMT"
    });
    parser.add_argument(
        "--conditionals", { help: "JSON files with extracted conditionals", required: true, nargs: "+" });
    parser.add_argument(
        "--abstract", { help: "Abstract identifiers and literals into ID1, ID2, LIT1, etc.", action: "store_true" });
    parser.add_argument(
        "--outfileprefix", { help: "Prefix for resulting .txt files", required: true });

    const args = parser.parse_args();

    const timestamp = Date.now();
    const sourceOutFile = args.outfileprefix + timestamp + "_source.txt"
    const targetOutFile = args.outfileprefix + timestamp + "_target.txt"

    const separator = "XX_SEP_XX";

    function replaceWhiteSpaces(tokens) {
        for (let tokenIdx = 0; tokenIdx < tokens.length; tokenIdx++) {
            const token = tokens[tokenIdx];
            tokens[tokenIdx] = token.replace(/\s/g, "_");
        }
    }

    let nextSourceLines = [];
    let nextTargetLines = [];
    for (let inFileIdx = 0; inFileIdx < args.conditionals.length; inFileIdx++) {
        const inFile = args.conditionals[inFileIdx];
        const rawInFile = fs.readFileSync(inFile, { "encoding": "utf8" });
        const inJSON = JSON.parse(rawInFile);

        for (let exampleIdx = 0; exampleIdx < inJSON.length; exampleIdx++) {
            const example = inJSON[exampleIdx];
            
            const conditionTokens = jsExtractionUtil.getTokens(example.condition);
            const consequentTokens = jsExtractionUtil.getTokens(example.consequent);
            const correctConditionTokens = jsExtractionUtil.getTokens(example.correctCondition);
            if (args.abstract) {
                tokenAbstractionUtil.abstractIdsLits([conditionTokens, consequentTokens, correctConditionTokens]);
            }
            
            const conditionTokenStrings = jsExtractionUtil.tokensToStrings(conditionTokens, true);
            const consequentTokenStrings = jsExtractionUtil.tokensToStrings(consequentTokens, true);
            const correctConditionTokenStrings = jsExtractionUtil.tokensToStrings(correctConditionTokens, true);

            const sourceTokens = conditionTokenStrings.concat([separator]).concat(consequentTokenStrings);
            const targetTokens = correctConditionTokenStrings;
            replaceWhiteSpaces(sourceTokens);
            replaceWhiteSpaces(targetTokens);

            nextSourceLines.push(sourceTokens.join(" "));
            nextTargetLines.push(targetTokens.join(" "));

            if (nextSourceLines.length >= 10000) {
                fs.writeFileSync(sourceOutFile, nextSourceLines.join("\n"), { flag: 'a' });
                fs.writeFileSync(targetOutFile, nextTargetLines.join("\n"), { flag: 'a' });

                nextSourceLines = [];
                nextTargetLines = [];
            }
        }
    }

    fs.writeFileSync(sourceOutFile, nextSourceLines.join("\n"), { flag: 'a' });
    fs.writeFileSync(targetOutFile, nextTargetLines.join("\n"), { flag: 'a' });

})();