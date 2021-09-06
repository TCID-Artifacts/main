(function () {

    const { ArgumentParser } = require('argparse');
    const os = require('os')

    const parallelization = require("../util/parallelization.js");
    const ioUtil = require("../util/ioUtil.js");

    const parser = new ArgumentParser({
        description: "Extract data from parsed JavaScript"
    });
    parser.add_argument(
        "--what", { help: "Kind of data to extract", choices: ["tokens", "tokensPerFunction", "tokensPerFunctionMaskName", "conditionals"], required: true });
    parser.add_argument(
        "--files", { help: "List of JavaScript files or .txt file with paths of JavaScript files", required: true, nargs: "+" });
    parser.add_argument(
        "--outdir", { help: "Directory for resulting JSON files", required: true });
    parser.add_argument(
        "--processes", { help: "Number of parallel processes (default: number of CPU cores)" });

    const args = parser.parse_args()
    const files = ioUtil.readFiles(args.files)
    const processes = args.processes == undefined ? os.cpus().length : Number(args.processes);

    console.log("Extracting from " + files.length + " file(s)");
    parallelization.spawnInstances(processes, files, args.outdir, args.what,
        ["--what", args.what], "main/extractFromJS.js", "pa/extractFromJSSingleInstance.js");

})();
