(function () {

    const acorn = require("acorn");
    const { ecmaVersion } = require("../util/config");
    const estraverse = require("estraverse");
    const escodegen = require("escodegen");
    const diffLib = require("diff");

    const blockLikeNodes = ["BlockStatement", "Program"]

    function parse(code) {
        return acorn.parse(code, { locations: false, ranges: false, ecmaVersion: ecmaVersion })
    }

    function toPatch(oldCode, newCode) {
        return diffLib.createPatch("", oldCode, newCode);
    }

    function removeSubexpression(origAST, origCode) {
        const result = [];

        let nodeCtr = 0;
        estraverse.traverse(origAST, {
            enter: function (node, parent) {
                nodeCtr++;
                // find relevant if conditions
                if (node.type == "IfStatement" && node.test.type == "LogicalExpression") {
                    const newAST = parse(origCode);
                    let newNodeCtr = 0;

                    // replace logical expression with its left side
                    estraverse.traverse(newAST, {
                        enter: function (newNode, parent) {
                            newNodeCtr++;
                            if (nodeCtr == newNodeCtr) {
                                newNode.test = newNode.test.left;
                                this.break();
                            }
                        }
                    });

                    const newCode = escodegen.generate(newAST);
                    const patch = toPatch(origCode, newCode);
                    result.push([patch, {
                        "kind": "removeSubexpression"
                    }]);
                }
            }
        });

        return result;
    }

    function moveStatements(oldParent, replacedNode, newParent) {
        const newStmts = [];
        for (let stmtIdx = 0; stmtIdx < newParent.body.length; stmtIdx++) {
            const stmt = newParent.body[stmtIdx];
            if (stmt == replacedNode) {
                for (let movingStmtIdx = 0; movingStmtIdx < oldParent.body.length; movingStmtIdx++) {
                    const movingStmt = oldParent.body[movingStmtIdx];
                    newStmts.push(movingStmt);
                }
            } else {
                newStmts.push(stmt);
            }
        }
        newParent.body = newStmts;
    }

    function removeThenBranch(origAST, origCode) {
        const result = [];

        let nodeCtr = 0;
        estraverse.traverse(origAST, {
            enter: function (node, parent) {
                nodeCtr++;
                // find relevant if conditions
                if (node.type == "IfStatement" && node.alternate != null) {
                    const newAST = parse(origCode);

                    // find node in new AST
                    let newNodeCtr = 0;
                    let newNode;
                    let newParentNode;
                    estraverse.traverse(newAST, {
                        enter: function (newNodeCandidate, parent) {
                            newNodeCtr++;
                            if (nodeCtr == newNodeCtr) {
                                newNode = newNodeCandidate;
                                newParentNode = parent;
                            }
                        }
                    });

                    // move statements from else branch into statements of parent node
                    if (blockLikeNodes.indexOf(newParentNode.type) != -1 && blockLikeNodes.indexOf(newNode.alternate.type) != -1) {
                        moveStatements(newNode.alternate, newNode, newParentNode);

                        const newCode = escodegen.generate(newAST);
                        const patch = toPatch(origCode, newCode);
                        result.push([patch, {
                            "kind": "removeThenBranch"
                        }]);
                    } else {
                        // ignore directly nested statements, e.g., "if (c) if (d) {} else foo()", as they are uncommon
                    }
                }
            }
        });

        return result;
    }

    function removeIfStmt(origAST, origCode) {
        const result = [];

        let nodeCtr = 0;
        estraverse.traverse(origAST, {
            enter: function (node, parent) {
                nodeCtr++;
                // find relevant if conditions
                if (node.type == "IfStatement" && node.alternate == null
                    && parent.body != undefined && parent.body.length > 1) {
                    const newAST = parse(origCode);

                    // remove if from tree
                    let newNodeCtr = 0;
                    estraverse.replace(newAST, {
                        enter: function (newNode, parent) {
                            newNodeCtr++;
                            if (nodeCtr == newNodeCtr) {
                                this.remove();
                            }
                        }
                    });

                    const newCode = escodegen.generate(newAST);
                    const patch = toPatch(origCode, newCode);
                    result.push([patch, {
                        "kind": "removeIfStmt"
                    }]);
                }
            }
        });

        return result;
    }

    function removeGuard(origAST, origCode) {
        const result = [];

        let nodeCtr = 0;
        estraverse.traverse(origAST, {
            enter: function (node, parent) {
                nodeCtr++;
                // find relevant if conditions
                if (node.type == "IfStatement" && node.alternate == null
                    && blockLikeNodes.indexOf(parent.type) != -1) {

                    const newAST = parse(origCode);
                    // find node in new AST
                    let newNodeCtr = 0;
                    let newNode;
                    let newParentNode;
                    estraverse.traverse(newAST, {
                        enter: function (newNodeCandidate, parent) {
                            newNodeCtr++;
                            if (nodeCtr == newNodeCtr) {
                                newNode = newNodeCandidate;
                                newParentNode = parent;
                            }
                        }
                    });

                    // move statements from then branch into statements of parent node
                    if (blockLikeNodes.indexOf(newParentNode.type) != -1 && blockLikeNodes.indexOf(newNode.consequent.type) != -1) {
                        moveStatements(newNode.consequent, newNode, newParentNode);

                        const newCode = escodegen.generate(newAST);
                        const patch = toPatch(origCode, newCode);
                        result.push([patch, {
                            "kind": "removeGuard"
                        }]);
                    } else {
                        // ignore directly nested statements, e.g., "if (c) if (d) {} else foo()", as they are uncommon
                    }
                }
            }
        });

        return result;
    }

    module.exports.transformers = [removeSubexpression, removeThenBranch, removeIfStmt, removeGuard];
    module.exports.removeSubexpression = removeSubexpression;
    module.exports.removeThenBranch = removeThenBranch;
    module.exports.removeIfStmt = removeIfStmt;
    module.exports.removeGuard = removeGuard;

})();