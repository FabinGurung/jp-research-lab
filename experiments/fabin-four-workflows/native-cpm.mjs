import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
const {scheduleNetwork}=await import(pathToFileURL(resolve(process.argv[2],'src/kernel/cpm.mjs')));
let input=''; for await(const s of process.stdin) input+=s;
process.stdout.write(JSON.stringify(scheduleNetwork(JSON.parse(input))));
