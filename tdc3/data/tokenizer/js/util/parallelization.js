(function () {

    const process = require("process");
    const { spawn } = require("child_process");

    function spawnSingleInstance(worklist, outfile, args, mainScript, singleInstanceScript) {
        console.log("Left in worklist: " + worklist.length + ". Spawning an instance.");
        const jsFiles = worklist.pop();
        if (jsFiles) {
            const scriptName = process.argv[1].replace(mainScript, singleInstanceScript);
            const argsToPass = [scriptName]
                .concat(args)
                .concat(["--files"])
                .concat(jsFiles)
                .concat(["--outfileprefix", outfile]);
            const cmd = spawn("node", argsToPass);
            cmd.on("close", (code) => {
                console.log("Instance has finished with exit code " + code);
                if (worklist.length > 0) {
                    spawnSingleInstance(worklist, outfile, args, mainScript, singleInstanceScript);
                }
            });
            cmd.stdout.on('data', (data) => {
                console.log(`${data}`);
            });
            cmd.stderr.on('data', (data) => {
                console.log(`${data}`);
            });
        }
    }

    const filesPerParallelInstance = 100;

    function spawnInstances(nbInstances, jsFiles, outdir, outname, args, mainScript, singleInstanceScript) {
        const worklist = [];
        for (let i = 0; i < jsFiles.length; i += filesPerParallelInstance) {
            const chunkOfJSFiles = jsFiles.slice(i, i + filesPerParallelInstance);
            worklist.push(chunkOfJSFiles);
        }

        for (let instance = 0; instance < nbInstances; instance++) {
            const outfile = outdir + "/" + outname + "_" + instance;
            spawnSingleInstance(worklist, outfile, args, mainScript, singleInstanceScript);
        }
    }

    module.exports.spawnInstances = spawnInstances;
})();