(function () {

    const { ArgumentParser } = require('argparse');
    const fs = require("fs");
    const acorn = require("acorn");
    const escodegen = require("escodegen");

    const bugSeedingTransformers = require("./bugSeedingTransformers");
    const { ecmaVersion } = require("../util/config");

    const parser = new ArgumentParser({
        description: "Not intended for direct usage. Use seedBugs.js instead."
    });
    parser.add_argument(
        "--kind", { help: "Kinds of bugs to seed: all, removeSubexpression, removeThenBranch, removeIfStmt, removeGuard", required: true, nargs: "+" });
    parser.add_argument(
        "--files", { help: "List of JavaScript files or .txt file with paths of JavaScript files", required: true, nargs: "+" });
    parser.add_argument(
        "--outfileprefix", { help: "Prefix for resulting bug seeding files", required: true });

    const args = parser.parse_args();
    const allTransformers = bugSeedingTransformers.transformers;
    let transformers;
    if (args.kind == "all") {
        transformers = allTransformers;
    } else {
        transformers = allTransformers.filter(t => args.kind.indexOf(t.name) != -1);
    }

    for (let fileIdx = 0; fileIdx < args.files.length; fileIdx++) {
        const file = args.files[fileIdx];
        const content = fs.readFileSync(file, { encoding: "utf8" });
        const origAST = acorn.parse(content, { locations: true, ranges: true, ecmaVersion: ecmaVersion });
        const outfileprefix = args.outfileprefix + "_" + fileIdx;

        // pretty-print original code into file
        const origCode = escodegen.generate(origAST);
        fs.writeFileSync(outfileprefix + "_orig.js", origCode);

        // create variants (each with exactly one bug) and pretty-print each into a file
        const metadataOfFile = [];
        for (let transformerIdx = 0; transformerIdx < transformers.length; transformerIdx++) {
            const transformer = transformers[transformerIdx];
            const patchMetadataPairs = transformer(origAST, origCode);
            for (let pairIdx = 0; pairIdx < patchMetadataPairs.length; pairIdx++) {
                const [patch, metadata] = patchMetadataPairs[pairIdx];
                const patchFile = outfileprefix + "_bug_" + transformerIdx + "_" + pairIdx + ".patch";
                fs.writeFileSync(patchFile, patch);
                metadata.filename = patchFile;
                metadataOfFile.push(metadata);
            }
        }

        // summarize created files in metadata file
        const metadataJSON = JSON.stringify(metadataOfFile, null, 2);
        fs.writeFileSync(outfileprefix + "_metadata.json", metadataJSON);
    }

    module.exports.ecmaVersion = ecmaVersion;

})();