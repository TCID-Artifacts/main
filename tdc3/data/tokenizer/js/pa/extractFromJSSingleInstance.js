(function () {

    const { ArgumentParser } = require('argparse');
    const fs = require("fs");
    const tokenExtraction = require("./tokenExtraction");
    const conditionalExtraction = require("./conditionalExtraction");

    const parser = new ArgumentParser({
        description: "Not intended for direct usage. Use extractFromJS.js instead."
    });
    parser.add_argument(
        "--what", { help: "Kind of data to extract", choices: ["tokens", "tokensPerFunction", "tokensPerFunctionMaskName", "conditionals"], required: true });
    parser.add_argument(
        "--files", { help: "List of JavaScript files", required: true, nargs: "+" });
    parser.add_argument(
        "--outfileprefix", { help: "Prefix for resulting JSON file", required: true });

    const args = parser.parse_args();
    const allResults = [];
    for (let fileIdx = 0; fileIdx < args.files.length; fileIdx++) {
        const file = args.files[fileIdx];
        try {
            if (fs.lstatSync(file).isDirectory()) {
                console.log("should not include a directory! " + file)
                continue
            }
            const code = fs.readFileSync(file, {encoding:"utf-8"});
            if (args.what == "tokens") {
                tokenExtraction.extractTokensFromFile(code, file, allResults);
            } else if (args.what == "tokensPerFunction") {
                tokenExtraction.extractTokensPerFunction(code, file, allResults, false);
            } else if (args.what == "tokensPerFunctionMaskName") {
                tokenExtraction.extractTokensPerFunction(code, file, allResults, true);
            } else if (args.what == "conditionals") {
                const examples = conditionalExtraction.extractExamples(code, file);
                allResults.push(...examples);
            }
            
        } catch (e) {
            console.log(e);
            console.log("Skipping file " + file);
            
        }
    }
    const timestamp = Date.now();
    const outfile = args.outfileprefix + "_"+ timestamp + ".json";
    fs.writeFileSync(outfile, JSON.stringify(allResults, null, 2), { flag: 'a+' });

})();