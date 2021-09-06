const acorn = require('acorn');
const jsx = require('acorn-jsx');
const fs = require('fs');

const jsParser = acorn.Parser.extend(jsx());

class Visitor {
	constructor() {
		this.describeDescription = "";
		this.describeVariables = "";
		this.describeSetup = "";
		this.describeTearDown = "";

		this.currentText = "";
		this.currentTest = "";
		this.pairs = new Array();
	}

	visitNodes(nodes) {
		for (const node of nodes) {
			this.visitNode(node)
		}
	}

	visitNode(node) {
		switch (node.type) {
			case "ExpressionStatement":
			    return this.visitCallExpression(node);
			case "CallExpression":
			    return this.visitCallExpression(node);
			case "VariableDeclaration":
			    return this.visitVariableDeclaration(node);
		}
	}

	visitExpressionStatement(node) {
		console.log(node.expression.callee.name);
	}

	visitCallExpression(node) {
		if (node.expression.type == "CallExpression") {
			switch (node.expression.callee.name) {
				case "describe":
				    // save the description of the currently viseted describe structure
				    this.describeDescription = node.expression.arguments[0].value;
				    // clear variables, setup, and teardown of previously visited describe structure
				    this.clearEnvironment();
				    // visite the nodes of the currently viseted describe structure
					this.visitNodes(node.expression.arguments[1].body.body);
					break;
				case "test":
				case "it":
				    this.currentText = this.describeDescription + '\n';
				    this.currentText += node.expression.arguments[0].value;

					var testCode=node.expression.arguments[1].body
		   			var starts = testCode.start + 1
					var ends = testCode.end - 1
				
					this.currentTest = this.describeSetup;
					this.currentTest += codeAsArray.slice(starts, ends).join("")+"\n";
					this.currentTest += this.describeTearDown;

					var pair = new Array();
					pair.push(this.currentText);
					pair.push(this.currentTest);
					this.pairs.push(pair);
					
					break;
				case "beforeAll":
				case "beforeEach":
				    var testNode = node.expression.arguments[0].body;
					var starts = testNode.start + 1;
				    var ends = testNode.end - 1;
					this.describeSetup += codeAsArray.slice(starts, ends).join("")+"\n";
					break;
				case "afterAll":
				case "afterEach":
				    var testNode = node.expression.arguments[0].body;
					var starts = testNode.start + 1;
					var ends = testNode.end - 1;
					this.describeTearDown += codeAsArray.slice(starts, ends).join("")+"\n";
  					break;
		    }
		}
    }

    visitVariableDeclaration(node) {
    	var testNode = node
		var starts = testNode.start
		var ends = testNode.end
		this.describeVariables += codeAsArray.slice(starts, ends).join("")
    }

    clearEnvironment() {
		this.describeVariables = "";
		this.describeSetup = "";
		this.describeTearDown = "";
    }

    savePairs() {
    	var file = "data.js";
    	var number = 1;
    	this.pairs.forEach(function(pair) {
    		file = "output/pair_" + Date.now() + number +".js"; 
    		fs.appendFileSync(file, "//text");
    		fs.appendFileSync(file, "\n");
    		fs.appendFileSync(file, pair[0]);
    		fs.appendFileSync(file, "\n");
    		fs.appendFileSync(file, "//test");
    		fs.appendFileSync(file, "\n");
    		fs.appendFileSync(file, pair[1]);

    		number += 1;
    	})
    	
    }

    run(nodes) {
		this.visitNodes(nodes)
		this.savePairs();
	}
}

var args = process.argv.slice(2);
const source = fs.readFileSync(args[0], 'utf8')
const parsed = jsParser.parse(source);

codeAsArray = Array.from(source)

JsVisitor = new Visitor();
JsVisitor.run(parsed.body);
