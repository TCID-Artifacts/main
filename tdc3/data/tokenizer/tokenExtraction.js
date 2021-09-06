(function () {

    const assert = require("assert");
    const util = require("./jsExtractionUtil");
    const estraverse = require("estraverse");

    function extractTokensFromFile(code, file, allResults) {
        const tokens = util.getTokens(code);
        if (tokens) {
            const tokensAsStrings = util.tokensToStrings(tokens);
            allResults.push({ data: tokensAsStrings, metadata: { file: file } });
        }
    }

    function extractTokensPerFunction(code, file, allResults, maskName) {
        const ast = util.getAST(code);
        estraverse.traverse(ast, {
            enter: function (node, parent) {
                if (node.type === "FunctionDeclaration" || node.type === "FunctionExpression") {
                    const functionName = util.getNameOfFunction(node, parent);
                    let functionCode = util.getCodeOfSubtree(node, code);
                    const functionTokens = util.getTokens(functionCode);
                    if (functionTokens) {
                        const tokensAsStrings = util.tokensToStrings(functionTokens);
                        if (maskName && node.id && node.id.name) {  // if there's a name and we should mask it
                            assert(tokensAsStrings[0] == "STD:function" && tokensAsStrings[2] == "STD:(")
                            tokensAsStrings[1] = "ID:MASKED";
                        }
                        allResults.push({ data: tokensAsStrings, metadata: { file: file, "name": functionName } });
                    }
                }
            }
        });
    }

    module.exports.extractTokensFromFile = extractTokensFromFile;
    module.exports.extractTokensPerFunction = extractTokensPerFunction;

})();