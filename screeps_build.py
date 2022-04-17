import os;

crate_name = 'screeps_arena_starter'
target_folder = 'point_game_here'

os.system('cargo build --release --target wasm32-unknown-unknown')
os.system('wasm-bindgen ./target/wasm32-unknown-unknown/release/'+ crate_name +'.wasm --out-dir ' + target_folder + ' --no-typescript --target web --omit-default-module-path')

wasm_path = target_folder + '/' + crate_name + '_bg.wasm'
bin_path = target_folder + '/' + crate_name + '_bg.wasm.bin'

if os.path.exists(bin_path):
    os.remove(bin_path)
os.rename(wasm_path, bin_path)

oldname = target_folder + '/' + crate_name + '.js'
newname = target_folder + '/temp'

headers = r'''
import WASM_U8 from "./''' + crate_name + '''_bg.wasm.bin"
import {utils, prototypes, constants} from '/game';
import { TextEncoder, TextDecoder } from "./text_encoding_shim";

import * as glob_import from "./imports.js"
for (let name in glob_import) {
    global[name] = glob_import[name];
}
'''

begin_del_1 = 'async function load(module, imports) {\n'
end_del_1 = 'async function init(input) {\n'
replace_1 = 'function init() {'

begin_del_2 = "    if (typeof input === 'string' || (typeof Request === 'function' && input instanceof Request) || (typeof URL === 'function' && input instanceof URL)) {\n"
end_del_2 = '    const { instance, module } = await load(await input, imports);\n'
replace_2 = r'''
    const module = new WebAssembly.Module(WASM_U8);
    const instance = new WebAssembly.Instance(module, imports);
'''

single_del_1 = 'let wasm;\n'
single_replace_1 = 'let wasm = init();\n'

single_del_2 = '    wasm = instance.exports;\n'
single_replace_2 = '    let wasm = instance.exports;\n'

single_del_3 = 'export default init;\n'
single_replace_3 = 'export default wasm;\n'

f = open(oldname,'r')
newf = open(newname, 'w')
lines = f.readlines()
newf.write(headers)
writing = True
for line in lines:
    if line == single_del_1:
        newf.write(single_replace_1);
        continue;
    if line == single_del_2:
        newf.write(single_replace_2);
        continue;
    if line == single_del_3:
        newf.write(single_replace_3);
        continue;

    if line == begin_del_1:
        newf.write(replace_1)
        writing = False
    if line == begin_del_2:
        newf.write(replace_2)
        writing = False

    if writing:
        newf.write(line)

    if line == end_del_1:
        writing = True
    if line == end_del_2:
        writing = True

newf.close()
f.close()
os.remove(oldname)
os.rename(newname, oldname)
