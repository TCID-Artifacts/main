(function () {

    const { ArgumentParser } = require("argparse");
    const os = require("os");

    const parallelization = require("../util/parallelization.js");
    const ioUtil = require("../util/ioUtil.js");

    const parser = new ArgumentParser({
        description: "Seed bugs into JavaScript code"
    });
    parser.add_argument(
        "--kind", { help: "Kinds of bugs to seed: all, removeSubexpression, removeThenBranch, removeIfStmt, removeGuard", required: true, nargs: "+" });
    parser.add_argument(
        "--files", { help: "List of JavaScript files or .txt file with paths of JavaScript files", required: true, nargs: "+" });
    parser.add_argument(
        "--outdir", { help: "Directory for resulting bug seeding files", required: true });
    parser.add_argument(
        "--processes", { help: "Number of parallel processes (default: number of CPU cores)" });

    const args = parser.parse_args()
    const files = ioUtil.readFiles(args.files)
    const processes = args.processes == undefined ? os.cpus().length : Number(args.processes);

    console.log("Seeding bugs into " + files.length + " file(s)");
    parallelization.spawnInstances(processes, files, args.outdir, "file",
        ["--kind"].concat(args.kind), "main/seedBugs.js", "pa/seedBugsSingleInstance.js");

})();