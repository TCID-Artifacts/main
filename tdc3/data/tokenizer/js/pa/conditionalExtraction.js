(function () {

    const acorn = require("acorn");
    const { ecmaVersion } = require("../util/config");
    const estraverse = require("estraverse");
    const util = require("./jsExtractionUtil");

    function parse(code) {
        return acorn.parse(code, { locations: false, ranges: true, ecmaVersion: ecmaVersion })
    }

    function extractExamples(code, file) {
        const examples = [];
        const ast = parse(code);
        estraverse.traverse(ast, {
            enter: function (node, parent) {
                if (node.type == "IfStatement") {
                    const conditionalCode = util.getCodeOfSubtree(node.test, code);
                    const consequentCode = util.getCodeOfSubtree(node.consequent, code);

                    // correct example
                    examples.push({
                        "consequent": consequentCode,
                        "condition": conditionalCode,
                        "correctCondition": conditionalCode,
                        "meta": {
                            "kind": "correctCondition",
                            "file": file
                        }
                    });

                    if (node.test.type == "LogicalExpression") {
                        // create negative example by keeping left check only
                        const leftConditionalCode = util.getCodeOfSubtree(node.test.left, code);
                        examples.push({
                            "consequent": consequentCode,
                            "condition": leftConditionalCode,
                            "correctCondition": conditionalCode,
                            "meta": {
                                "kind": "incompleteCondition",
                                "file": file
                            }
                        });

                        // create negative example by keeping right check only
                        const rightConditionalCode = util.getCodeOfSubtree(node.test.right, code);
                        examples.push({
                            "consequent": consequentCode,
                            "condition": rightConditionalCode,
                            "correctCondition": conditionalCode,
                            "meta": {
                                "kind": "incompleteCondition",
                                "file": file
                            }
                        });
                    }
                }
            }
        });
        return examples;
    }

    module.exports.extractExamples = extractExamples;

})();