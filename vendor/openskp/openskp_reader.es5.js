/* __acad3dV163: the SketchUp reader. openskp 359d183 (github.com/iamahsanmehmood/openskp, MIT,
   Copyright (c) 2024-2026 Ahsan Mehmood), its TypeScript reader only, with fflate 0.8.3 (MIT,
   Copyright (c) 2026 Arjun Barrett) and earcut 3.2.4 (ISC, Copyright (c) 2026, Mapbox). Bundled by esbuild
   and compiled to ES5 syntax by TypeScript (tools/openskp/build_reader.mjs); it uses ES2015 built-ins
   (Map, Set, typed arrays, TextDecoder). The licences, which go with every copy of this page:

   openskp
   MIT License

   Copyright (c) 2024-2026 Ahsan Mehmood

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.

   fflate
   MIT License

   Copyright (c) 2026 Arjun Barrett

   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:

   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.

   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.

   earcut
   ISC License

   Copyright (c) 2026, Mapbox

   Permission to use, copy, modify, and/or distribute this software for any purpose
   with or without fee is hereby granted, provided that the above copyright notice
   and this permission notice appear in all copies.

   THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
   REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
   FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
   INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
   OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
   TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
   THIS SOFTWARE.
*/
var OpenSkp=(function(){
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
var __values = (this && this.__values) || function(o) {
    var s = typeof Symbol === "function" && Symbol.iterator, m = s && o[s], i = 0;
    if (m) return m.call(o);
    if (o && typeof o.length === "number") return {
        next: function () {
            if (o && i >= o.length) o = void 0;
            return { value: o && o[i++], done: !o };
        }
    };
    throw new TypeError(s ? "Object is not iterable." : "Symbol.iterator is not defined.");
};
var __read = (this && this.__read) || function (o, n) {
    var m = typeof Symbol === "function" && o[Symbol.iterator];
    if (!m) return o;
    var i = m.call(o), r, ar = [], e;
    try {
        while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
    }
    catch (error) { e = { error: error }; }
    finally {
        try {
            if (r && !r.done && (m = i["return"])) m.call(i);
        }
        finally { if (e) throw e.error; }
    }
    return ar;
};
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
var OpenSkp = (function () { var __defProp = Object.defineProperty; var __getOwnPropDesc = Object.getOwnPropertyDescriptor; var __getOwnPropNames = Object.getOwnPropertyNames, __getOwnPropSymbols = Object.getOwnPropertySymbols; var __hasOwnProp = Object.prototype.hasOwnProperty, __propIsEnum = Object.prototype.propertyIsEnumerable; var __defNormalProp = function (obj, key, value) { return key in obj ? __defProp(obj, key, { enumerable: !0, configurable: !0, writable: !0, value: value }) : obj[key] = value; }, __spreadValues = function (a, b) {
    var e_1, _j;
    for (var prop in b || (b = {}))
        __hasOwnProp.call(b, prop) && __defNormalProp(a, prop, b[prop]);
    if (__getOwnPropSymbols)
        try {
            for (var _k = __values(__getOwnPropSymbols(b)), _l = _k.next(); !_l.done; _l = _k.next()) {
                var prop = _l.value;
                __propIsEnum.call(b, prop) && __defNormalProp(a, prop, b[prop]);
            }
        }
        catch (e_1_1) { e_1 = { error: e_1_1 }; }
        finally {
            try {
                if (_l && !_l.done && (_j = _k.return)) _j.call(_k);
            }
            finally { if (e_1) throw e_1.error; }
        }
    return a;
}; var __export = function (target, all) { for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: !0 }); }, __copyProps = function (to, from, except, desc) {
    var e_2, _j;
    if (from && typeof from == "object" || typeof from == "function") {
        var _loop_1 = function (key) {
            !__hasOwnProp.call(to, key) && key !== except && __defProp(to, key, { get: function () { return from[key]; }, enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
        };
        try {
            for (var _k = __values(__getOwnPropNames(from)), _l = _k.next(); !_l.done; _l = _k.next()) {
                var key = _l.value;
                _loop_1(key);
            }
        }
        catch (e_2_1) { e_2 = { error: e_2_1 }; }
        finally {
            try {
                if (_l && !_l.done && (_j = _k.return)) _j.call(_k);
            }
            finally { if (e_2) throw e_2.error; }
        }
    }
    return to;
}; var __toCommonJS = function (mod) { return __copyProps(__defProp({}, "__esModule", { value: !0 }), mod); }; var entry_exports = {}; __export(entry_exports, { SkpParseError: function () { return SkpParseError; }, buildInstancedScene: function () { return buildInstancedScene; }, buildScene: function () { return buildScene; }, parseSkp: function () { return parseSkp; } }); var u8 = Uint8Array, u16 = Uint16Array, i32 = Int32Array, fleb = new u8([0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0, 0, 0, 0]), fdeb = new u8([0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 0, 0]), clim = new u8([16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]), freb = function (eb, start) { for (var b = new u16(31), i = 0; i < 31; ++i)
    b[i] = start += 1 << eb[i - 1]; for (var r = new i32(b[30]), i = 1; i < 30; ++i)
    for (var j = b[i]; j < b[i + 1]; ++j)
        r[j] = j - b[i] << 5 | i; return { b: b, r: r }; }, _a = freb(fleb, 2), fl = _a.b, revfl = _a.r; fl[28] = 258, revfl[258] = 28; var _b = freb(fdeb, 0), fd = _b.b, revfd = _b.r, rev = new u16(32768); for (i = 0; i < 32768; ++i)
    x = (i & 43690) >> 1 | (i & 21845) << 1, x = (x & 52428) >> 2 | (x & 13107) << 2, x = (x & 61680) >> 4 | (x & 3855) << 4, rev[i] = ((x & 65280) >> 8 | (x & 255) << 8) >> 1; var x, i, hMap = (function (cd, mb, r) { for (var s = cd.length, i = 0, l = new u16(mb); i < s; ++i)
    cd[i] && ++l[cd[i] - 1]; var le = new u16(mb); for (i = 1; i < mb; ++i)
    le[i] = le[i - 1] + l[i - 1] << 1; var co; if (r) {
    co = new u16(1 << mb);
    var rvb = 15 - mb;
    for (i = 0; i < s; ++i)
        if (cd[i])
            for (var sv = i << 4 | cd[i], r_1 = mb - cd[i], v = le[cd[i] - 1]++ << r_1, m = v | (1 << r_1) - 1; v <= m; ++v)
                co[rev[v] >> rvb] = sv;
}
else
    for (co = new u16(s), i = 0; i < s; ++i)
        cd[i] && (co[i] = rev[le[cd[i] - 1]++] >> 15 - cd[i]); return co; }), flt = new u8(288); for (i = 0; i < 144; ++i)
    flt[i] = 8; var i; for (i = 144; i < 256; ++i)
    flt[i] = 9; var i; for (i = 256; i < 280; ++i)
    flt[i] = 7; var i; for (i = 280; i < 288; ++i)
    flt[i] = 8; var i, fdt = new u8(32); for (i = 0; i < 32; ++i)
    fdt[i] = 5; var i; var flrm = hMap(flt, 9, 1); var fdrm = hMap(fdt, 5, 1), max = function (a) { for (var m = a[0], i = 1; i < a.length; ++i)
    a[i] > m && (m = a[i]); return m; }, bits = function (d, p, m) { var o = p / 8 | 0; return (d[o] | d[o + 1] << 8) >> (p & 7) & m; }, bits16 = function (d, p) { var o = p / 8 | 0; return (d[o] | d[o + 1] << 8 | d[o + 2] << 16) >> (p & 7); }, shft = function (p) { return (p + 7) / 8 | 0; }, slc = function (v, s, e) { return (s == null || s < 0) && (s = 0), (e == null || e > v.length) && (e = v.length), new u8(v.subarray(s, e)); }; var ec = ["unexpected EOF", "invalid block type", "invalid length/literal", "invalid distance", "stream finished", "no stream handler", , "no callback", "invalid UTF-8 data", "extra field too long", "date not in range 1980-2099", "filename too long", "stream finishing", "invalid zip data"], err = function (ind, msg, nt) { var e = new Error(msg || ec[ind]); if (e.code = ind, Error.captureStackTrace && Error.captureStackTrace(e, err), !nt)
    throw e; return e; }, inflt = function (dat, st, buf, dict) { var sl = dat.length, dl = dict ? dict.length : 0; if (!sl || st.f && !st.l)
    return buf || new u8(0); var noBuf = !buf, resize = noBuf || st.i != 2, noSt = st.i; noBuf && (buf = new u8(sl * 3)); var cbuf = function (l2) { var bl = buf.length; if (l2 > bl) {
    var nbuf = new u8(Math.max(bl * 2, l2));
    nbuf.set(buf), buf = nbuf;
} }, final = st.f || 0, pos = st.p || 0, bt = st.b || 0, lm = st.l, dm = st.d, lbt = st.m, dbt = st.n, tbts = sl * 8; do {
    if (!lm) {
        final = bits(dat, pos, 1);
        var type = bits(dat, pos + 1, 3);
        if (pos += 3, type)
            if (type == 1)
                lm = flrm, dm = fdrm, lbt = 9, dbt = 5;
            else if (type == 2) {
                var hLit = bits(dat, pos, 31) + 257, hcLen = bits(dat, pos + 10, 15) + 4, tl = hLit + bits(dat, pos + 5, 31) + 1;
                pos += 14;
                for (var ldt = new u8(tl), clt = new u8(19), i = 0; i < hcLen; ++i)
                    clt[clim[i]] = bits(dat, pos + i * 3, 7);
                pos += hcLen * 3;
                for (var clb = max(clt), clbmsk = (1 << clb) - 1, clm = hMap(clt, clb, 1), i = 0; i < tl;) {
                    var r = clm[bits(dat, pos, clbmsk)];
                    pos += r & 15;
                    var s = r >> 4;
                    if (s < 16)
                        ldt[i++] = s;
                    else {
                        var c = 0, n = 0;
                        for (s == 16 ? (n = 3 + bits(dat, pos, 3), pos += 2, c = ldt[i - 1]) : s == 17 ? (n = 3 + bits(dat, pos, 7), pos += 3) : s == 18 && (n = 11 + bits(dat, pos, 127), pos += 7); n--;)
                            ldt[i++] = c;
                    }
                }
                var lt = ldt.subarray(0, hLit), dt = ldt.subarray(hLit);
                lbt = max(lt), dbt = max(dt), lm = hMap(lt, lbt, 1), dm = hMap(dt, dbt, 1);
            }
            else
                err(1);
        else {
            var s = shft(pos) + 4, l = dat[s - 4] | dat[s - 3] << 8, t = s + l;
            if (t > sl) {
                noSt && err(0);
                break;
            }
            resize && cbuf(bt + l), buf.set(dat.subarray(s, t), bt), st.b = bt += l, st.p = pos = t * 8, st.f = final;
            continue;
        }
        if (pos > tbts) {
            noSt && err(0);
            break;
        }
    }
    resize && cbuf(bt + 131072);
    for (var lms = (1 << lbt) - 1, dms = (1 << dbt) - 1, lpos = pos;; lpos = pos) {
        var c = lm[bits16(dat, pos) & lms], sym = c >> 4;
        if (pos += c & 15, pos > tbts) {
            noSt && err(0);
            break;
        }
        if (c || err(2), sym < 256)
            buf[bt++] = sym;
        else if (sym == 256) {
            lpos = pos, lm = null;
            break;
        }
        else {
            var add = sym - 254;
            if (sym > 264) {
                var i = sym - 257, b = fleb[i];
                add = bits(dat, pos, (1 << b) - 1) + fl[i], pos += b;
            }
            var d = dm[bits16(dat, pos) & dms], dsym = d >> 4;
            d || err(3), pos += d & 15;
            var dt = fd[dsym];
            if (dsym > 3) {
                var b = fdeb[dsym];
                dt += bits16(dat, pos) & (1 << b) - 1, pos += b;
            }
            if (pos > tbts) {
                noSt && err(0);
                break;
            }
            resize && cbuf(bt + 131072);
            var end = bt + add;
            if (bt < dt) {
                var shift = dl - dt, dend = Math.min(dt, end);
                for (shift + bt < 0 && err(3); bt < dend; ++bt)
                    buf[bt] = dict[shift + bt];
            }
            for (; bt < end; ++bt)
                buf[bt] = buf[bt - dt];
        }
    }
    st.l = lm, st.p = lpos, st.b = bt, st.f = final, lm && (final = 1, st.m = lbt, st.d = dm, st.n = dbt);
} while (!final); return bt != buf.length && noBuf ? slc(buf, 0, bt) : buf.subarray(0, bt); }; var et = new u8(0); var b2 = function (d, b) { return d[b] | d[b + 1] << 8; }, b4 = function (d, b) { return (d[b] | d[b + 1] << 8 | d[b + 2] << 16 | d[b + 3] << 24) >>> 0; }, b8 = function (d, b) { return b4(d, b) + b4(d, b + 4) * 4294967296; }; function inflateSync(data, opts) { return inflt(data, { i: 2 }, opts && opts.out, opts && opts.dictionary); } var td = typeof TextDecoder != "undefined" && new TextDecoder, tds = 0; try {
    td.decode(et, { stream: !0 }), tds = 1;
}
catch (e) { } var dutf8 = function (d) { for (var r = "", i = 0;;) {
    var c = d[i++], eb = (c > 127) + (c > 223) + (c > 239);
    if (i + eb > d.length)
        return { s: r, r: slc(d, i - 1) };
    eb ? eb == 3 ? (c = ((c & 15) << 18 | (d[i++] & 63) << 12 | (d[i++] & 63) << 6 | d[i++] & 63) - 65536, r += String.fromCharCode(55296 | c >> 10, 56320 | c & 1023)) : eb & 1 ? r += String.fromCharCode((c & 31) << 6 | d[i++] & 63) : r += String.fromCharCode((c & 15) << 12 | (d[i++] & 63) << 6 | d[i++] & 63) : r += String.fromCharCode(c);
} }; function strFromU8(dat, latin1) { if (latin1) {
    for (var r = "", i = 0; i < dat.length; i += 16384)
        r += String.fromCharCode.apply(null, dat.subarray(i, i + 16384));
    return r;
}
else {
    if (td)
        return td.decode(dat);
    var _a2 = dutf8(dat), s = _a2.s, r = _a2.r;
    return r.length && err(8), s;
} } var slzh = function (d, b) { return b + 30 + b2(d, b + 26) + b2(d, b + 28); }, zh = function (d, b, z) { var fnl = b2(d, b + 28), efl = b2(d, b + 30), fn = strFromU8(d.subarray(b + 46, b + 46 + fnl), !(b2(d, b + 8) & 2048)), es = b + 46 + fnl, _a2 = z64hs(d, es, efl, z, b4(d, b + 20), b4(d, b + 24), b4(d, b + 42)), sc = _a2[0], su = _a2[1], off = _a2[2]; return [b2(d, b + 10), sc, su, fn, es + efl + b2(d, b + 32), off]; }, z64hs = function (d, b, l, z, sc, su, off) { var nsc = sc == 4294967295, nsu = su == 4294967295, noff = off == 4294967295, e = b + l, nf = nsc + nsu + noff; if (z && nf) {
    for (; b + 4 < e; b += 4 + b2(d, b + 2))
        if (b2(d, b) == 1)
            return [nsc ? b8(d, b + 4 + 8 * nsu) : sc, nsu ? b8(d, b + 4) : su, noff ? b8(d, b + 4 + 8 * (nsu + nsc)) : off, 1];
    z < 2 && err(13);
} return [sc, su, off, 0]; }; function unzipSync(data, opts) { for (var files = {}, e = data.length - 22; b4(data, e) != 101010256; --e)
    (!e || data.length - e > 65558) && err(13); var c = b2(data, e + 8); if (!c)
    return {}; var o = b4(data, e + 16), z = b4(data, e - 20) == 117853008; if (z) {
    var ze = b4(data, e - 12);
    z = b4(data, ze) == 101075792, z && (c = b4(data, ze + 32), o = b4(data, ze + 48));
} for (var fltr = opts && opts.filter, i = 0; i < c; ++i) {
    var _a2 = zh(data, o, z), c_2 = _a2[0], sc = _a2[1], su = _a2[2], fn = _a2[3], no = _a2[4], off = _a2[5], b = slzh(data, off);
    o = no, (!fltr || fltr({ name: fn, size: sc, originalSize: su, compression: c_2 })) && (c_2 ? c_2 == 8 ? files[fn] = inflateSync(data.subarray(b, b + sc), { out: new u8(su) }) : err(14, "unknown compression type " + c_2) : files[fn] = slc(data, b, b + sc));
} return files; } function emitLog(options, level, message) { var _a2; (_a2 = options == null ? void 0 : options.onLog) == null || _a2.call(options, level, message); } function emitProgress(options, stage, current, total) { var _a2; (_a2 = options == null ? void 0 : options.onProgress) == null || _a2.call(options, { stage: stage, current: current, total: total }); } var VFF_MAGIC = [255, 254, 255, 14], ZIP_LOCAL_HEADER = [80, 75, 3, 4]; function findSequence(data, sequence, startOffset) {
    if (startOffset === void 0) { startOffset = 0; }
    var seqLen = sequence.length;
    if (seqLen === 0)
        return -1;
    var limit = data.length - seqLen;
    for (var i_1 = startOffset; i_1 <= limit; i_1++) {
        var match = !0;
        for (var j = 0; j < seqLen; j++)
            if (data[i_1 + j] !== sequence[j]) {
                match = !1;
                break;
            }
        if (match)
            return i_1;
    }
    return -1;
} function decodeEntryName(entry) { if (!/[\u0080-\u00ff]/.test(entry))
    return entry; var bytes = new Uint8Array(entry.length); for (var i_2 = 0; i_2 < entry.length; i_2++) {
    var code = entry.charCodeAt(i_2);
    if (code > 255)
        return entry;
    bytes[i_2] = code;
} try {
    return new TextDecoder("utf-8", { fatal: !0 }).decode(bytes);
}
catch (e) {
    return entry;
} } function validateHeader(data) { return data.length < 4 ? !1 : data[0] === VFF_MAGIC[0] && data[1] === VFF_MAGIC[1] && data[2] === VFF_MAGIC[2] && data[3] === VFF_MAGIC[3]; } function readVersion(data, options) { if (data.length < 16)
    return "unknown"; var secondMarker = findSequence(data, [255, 254, 255], 4); if (secondMarker > 0) {
    var verStart = secondMarker + 4, verBytes = data.subarray(verStart, Math.min(verStart + 200, data.length));
    try {
        var verText = new TextDecoder("utf-16le").decode(verBytes), braceStart = verText.indexOf("{");
        if (braceStart >= 0) {
            var braceEnd = verText.indexOf("}", braceStart);
            if (braceEnd > braceStart)
                return verText.slice(braceStart, braceEnd + 1);
        }
    }
    catch (e) {
        emitLog(options, "debug", "Failed to decode version string: ".concat(e.message));
    }
} return "unknown"; } function findZipOffset(data) { var offset = findSequence(data, ZIP_LOCAL_HEADER); if (offset < 0)
    throw new Error("No embedded ZIP archive found in the file"); return offset; } var META_WRAPPER_TAG = [100, 0], META_UNITS_TAG = [109, 0]; function readMetaUnits(metaBytes) { var view = new DataView(metaBytes.buffer, metaBytes.byteOffset, metaBytes.byteLength), pos = 0; for (; pos + 6 <= metaBytes.length;) {
    var tag = [metaBytes[pos], metaBytes[pos + 1]], size = view.getUint32(pos + 2, !0);
    if (pos + 6 + size > metaBytes.length)
        break;
    if (tag[0] === META_WRAPPER_TAG[0] && tag[1] === META_WRAPPER_TAG[1])
        return readMetaUnits(metaBytes.subarray(pos + 6, pos + 6 + size));
    if (tag[0] === META_UNITS_TAG[0] && tag[1] === META_UNITS_TAG[1])
        return new TextDecoder("utf-8").decode(metaBytes.subarray(pos + 6, pos + 6 + size));
    pos += 6 + size;
} return null; } var MAX_UNCOMPRESSED_ENTRY_BYTES = 16 * 1024 * 1024 * 1024, MAX_COMPRESSION_RATIO = 1e3, RATIO_CHECK_THRESHOLD_BYTES = 1024 * 1024; function validateEntrySize(file) { var declared = file.originalSize; if (!(declared <= 0)) {
    if (declared > MAX_UNCOMPRESSED_ENTRY_BYTES)
        throw new Error("ZIP entry '".concat(file.name, "' declares ").concat(declared, " bytes uncompressed, exceeding the ").concat(MAX_UNCOMPRESSED_ENTRY_BYTES, "-byte safety ceiling"));
    if (declared >= RATIO_CHECK_THRESHOLD_BYTES) {
        var compressed = file.size;
        if (compressed <= 0 || declared / compressed > MAX_COMPRESSION_RATIO)
            throw new Error("ZIP entry '".concat(file.name, "' declares an implausible compression ratio (").concat(declared, " bytes from ").concat(compressed, " bytes compressed) - likely a decompression bomb"));
    }
} } function extractSkpContents(data, options) {
    var e_3, _j;
    if (!validateHeader(data) && !(findSequence(data.subarray(0, Math.min(64, data.length)), ZIP_LOCAL_HEADER) >= 0))
        throw new Error("Not a valid SketchUp (.skp) file");
    var version = readVersion(data, options), zipOffset = findZipOffset(data), zipBytes = data.subarray(zipOffset), wanted = function (file) { var lower = file.name.toLowerCase(), isWanted = lower === "model.dat" || lower.endsWith("/model.dat") || lower === "meta/meta.dat" || lower.endsWith(".xml") || lower.endsWith(".png") || lower.endsWith(".jpg") || lower.endsWith(".jpeg") || lower.includes("material"); return isWanted && validateEntrySize(file), isWanted; }, unzipped;
    try {
        unzipped = unzipSync(zipBytes, { filter: wanted });
    }
    catch (e) {
        var wrapped = new Error("Failed to decompress ZIP archive: " + e.message);
        throw wrapped.cause = e, wrapped;
    }
    var modelData = null, metaData = null, materialFiles = {};
    try {
        for (var _k = __values(Object.keys(unzipped)), _l = _k.next(); !_l.done; _l = _k.next()) {
            var rawEntry = _l.value;
            var entry = decodeEntryName(rawEntry), lower = entry.toLowerCase();
            lower === "model.dat" || lower.endsWith("/model.dat") ? modelData = unzipped[rawEntry] : lower === "meta/meta.dat" ? metaData = unzipped[rawEntry] : (lower.endsWith(".xml") || lower.endsWith(".png") || lower.endsWith(".jpg") || lower.endsWith(".jpeg") || lower.includes("material")) && (materialFiles[entry] = unzipped[rawEntry]);
        }
    }
    catch (e_3_1) { e_3 = { error: e_3_1 }; }
    finally {
        try {
            if (_l && !_l.done && (_j = _k.return)) _j.call(_k);
        }
        finally { if (e_3) throw e_3.error; }
    }
    if (!modelData)
        throw new Error("ZIP archive found but does not contain a model.dat entry");
    return { version: version, modelData: modelData, materialFiles: materialFiles, metaData: metaData };
} var CONTAINER_TAGS = new Set(["F401", "F701", "D430", "D530", "C832", "7C15", "8813", "8913", "8A13", "8B13", "8C13", "8D13", "4C1D", "6419", "F901", "7017", "7117", "D007", "C409", "9411", "9511", "0F01", "384A", "B80B", "9713", "2C4C", "AC0D", "AE0D", "F601", "F801", "983A", "993A", "8C3C", "8D3C", "9013", "401F"]); function readU32(data, offset) { if (offset + 4 > data.length)
    throw new Error("Out of bounds readU32"); return new DataView(data.buffer, data.byteOffset + offset, 4).getUint32(0, !0); } function readF64(data, offset) { if (offset + 8 > data.length)
    throw new Error("Out of bounds readF64"); return new DataView(data.buffer, data.byteOffset + offset, 8).getFloat64(0, !0); } function readI32(data, offset) { if (offset + 4 > data.length)
    throw new Error("Out of bounds readI32"); return new DataView(data.buffer, data.byteOffset + offset, 4).getInt32(0, !0); } function parseVarInt(data, offset, length) { var val = 0; for (var i_3 = 0; i_3 < length; i_3++)
    val += data[offset + i_3] * Math.pow(256, i_3); return val; } function parseTlvRecursive(data, start, end, containerTags, depth) {
    if (containerTags === void 0) { containerTags = CONTAINER_TAGS; }
    if (depth === void 0) { depth = 0; }
    var pos = start, elements = [];
    for (; pos <= end - 6;) {
        var tagBytes = data.subarray(pos, pos + 2), size = readU32(data, pos + 2);
        if (pos + 6 + size > end)
            break;
        var tagHex = "";
        for (var i_4 = 0; i_4 < 2; i_4++) {
            var hex = tagBytes[i_4].toString(16).toUpperCase();
            tagHex += hex.length === 1 ? "0" + hex : hex;
        }
        var children = [];
        containerTags.has(tagHex) && size > 0 && (children = parseTlvRecursive(data, pos + 6, pos + 6 + size, containerTags, depth + 1));
        var payload = children.length > 0 ? new Uint8Array(0) : data.subarray(pos + 6, pos + 6 + size);
        elements.push({ offset: pos, tag: tagHex, size: size, children: children, payload: payload }), pos += 6 + size;
    }
    return elements;
} function flatHeaders(data, start, end) { var headers = [], pos = start; for (; pos <= end - 6;) {
    var tagBytes = data.subarray(pos, pos + 2), size = readU32(data, pos + 2);
    if (pos + 6 + size > end)
        break;
    var tagHex = "";
    for (var i_5 = 0; i_5 < 2; i_5++) {
        var hex = tagBytes[i_5].toString(16).toUpperCase();
        tagHex += hex.length === 1 ? "0" + hex : hex;
    }
    headers.push([tagHex, pos, size]), pos += 6 + size;
} return headers; } var PASS_THROUGH_WRAPPERS = new Set(["F901", "7017", "7117"]); function expandWrappers(data, headers, containerTags) {
    var e_4, _j;
    var out = [];
    try {
        for (var headers_1 = __values(headers), headers_1_1 = headers_1.next(); !headers_1_1.done; headers_1_1 = headers_1.next()) {
            var header = headers_1_1.value;
            var _k = __read(header, 3), tag = _k[0], offset = _k[1], size = _k[2];
            PASS_THROUGH_WRAPPERS.has(tag) && containerTags.has(tag) ? out.push.apply(out, __spreadArray([], __read(expandWrappers(data, flatHeaders(data, offset + 6, offset + 6 + size), containerTags)), false)) : out.push(header);
        }
    }
    catch (e_4_1) { e_4 = { error: e_4_1 }; }
    finally {
        try {
            if (headers_1_1 && !headers_1_1.done && (_j = headers_1.return)) _j.call(headers_1);
        }
        finally { if (e_4) throw e_4.error; }
    }
    return out;
} function iterTopLevelLazy(data, start, end, containerTags) {
    var headers, _j, f401Offset, f401Size, total, index, headers_2, headers_2_1, _k, offset, size, recordEnd, nodes, _l, e_5_1;
    var e_5, _m;
    if (containerTags === void 0) { containerTags = CONTAINER_TAGS; }
    return __generator(this, function (_o) {
        switch (_o.label) {
            case 0:
                headers = flatHeaders(data, start, end);
                if (headers.length === 1 && headers[0][0] === "F401") {
                    _j = __read(headers[0], 3), f401Offset = _j[1], f401Size = _j[2];
                    headers = flatHeaders(data, f401Offset + 6, f401Offset + 6 + f401Size);
                }
                headers = expandWrappers(data, headers, containerTags);
                total = headers.length, index = 0;
                _o.label = 1;
            case 1:
                _o.trys.push([1, 7, 8, 9]);
                headers_2 = __values(headers), headers_2_1 = headers_2.next();
                _o.label = 2;
            case 2:
                if (!!headers_2_1.done) return [3, 6];
                _k = __read(headers_2_1.value, 3), offset = _k[1], size = _k[2];
                recordEnd = offset + 6 + size, nodes = parseTlvRecursive(data, offset, recordEnd, containerTags);
                _l = nodes.length > 0;
                if (!_l) return [3, 4];
                return [4, { index: index, total: total, node: nodes[0] }];
            case 3:
                _l = (_o.sent());
                _o.label = 4;
            case 4:
                _l, index++;
                _o.label = 5;
            case 5:
                headers_2_1 = headers_2.next();
                return [3, 2];
            case 6: return [3, 9];
            case 7:
                e_5_1 = _o.sent();
                e_5 = { error: e_5_1 };
                return [3, 9];
            case 8:
                try {
                    if (headers_2_1 && !headers_2_1.done && (_m = headers_2.return)) _m.call(headers_2);
                }
                finally { if (e_5) throw e_5.error; }
                return [7];
            case 9: return [2];
        }
    });
} var SkpParseError = (function (_super) {
    __extends(_SkpParseError, _super);
    function _SkpParseError(message, context) {
        if (context === void 0) { context = {}; }
        var _this = this;
        var parts = [message];
        context.stage !== void 0 && parts.push("stage=".concat(context.stage)), context.recordIndex !== void 0 && context.totalRecords !== void 0 && parts.push("record=".concat(context.recordIndex, "/").concat(context.totalRecords)), context.tag !== void 0 && parts.push("tag=".concat(context.tag)), context.offset !== void 0 && parts.push("offset=0x".concat(context.offset.toString(16).toUpperCase())), context.definitionId !== void 0 && parts.push("definitionId=".concat(context.definitionId)), _this = _super.call(this, parts.join(" | ")) || this, _this.name = "SkpParseError", _this.stage = context.stage, _this.recordIndex = context.recordIndex, _this.totalRecords = context.totalRecords, _this.tag = context.tag, _this.offset = context.offset, _this.definitionId = context.definitionId, _this.cause = context.cause, Object.setPrototypeOf(_this, _SkpParseError.prototype);
        return _this;
    }
    return _SkpParseError;
}(Error)); var EdgeFlagStore = (function () {
    function EdgeFlagStore() {
        this.flags = new Uint8Array(0);
        this.present = new Uint8Array(0);
        this.baseId = 0;
        this.initialized = !1;
        this.count = 0;
        this.highSlot = 0;
    }
    Object.defineProperty(EdgeFlagStore.prototype, "size", {
        get: function () { return this.count; },
        enumerable: false,
        configurable: true
    });
    EdgeFlagStore.prototype.slotFor = function (id) { return id - this.baseId; };
    EdgeFlagStore.prototype.ensureSlot = function (id) { if (!this.initialized)
        return this.baseId = id, this.flags = new Uint8Array(64), this.present = new Uint8Array(8), this.initialized = !0, 0; if (id < this.baseId) {
        var used = this.highSlot + 1, gap = this.baseId - id, headroom = Math.max(64, used), shift = gap + headroom, nextLength = shift + used, nextFlags = new Uint8Array(nextLength);
        nextFlags.set(this.flags.subarray(0, used), shift);
        var nextPresent = new Uint8Array(Math.ceil(nextLength / 8));
        for (var slot2 = 0; slot2 < used; slot2++)
            if ((this.present[slot2 >> 3] & 1 << (slot2 & 7)) !== 0) {
                var moved = slot2 + shift;
                nextPresent[moved >> 3] |= 1 << (moved & 7);
            }
        return this.flags = nextFlags, this.present = nextPresent, this.baseId -= shift, this.highSlot += shift, headroom;
    } var slot = this.slotFor(id); if (slot >= this.flags.length) {
        var nextLength = Math.max(slot + 1, this.flags.length * 2), nextFlags = new Uint8Array(nextLength);
        nextFlags.set(this.flags), this.flags = nextFlags;
        var nextPresent = new Uint8Array(Math.ceil(nextLength / 8));
        nextPresent.set(this.present), this.present = nextPresent;
    } return slot > this.highSlot && (this.highSlot = slot), slot; };
    EdgeFlagStore.prototype.set = function (id, flags) { var slot = this.ensureSlot(id); (this.present[slot >> 3] & 1 << (slot & 7)) === 0 && (this.present[slot >> 3] |= 1 << (slot & 7), this.count++), this.flags[slot] = flags & 255; };
    EdgeFlagStore.prototype.get = function (id) { if (!this.initialized)
        return; var slot = this.slotFor(id); if (!(slot < 0 || slot >= this.flags.length) && (this.present[slot >> 3] & 1 << (slot & 7)) !== 0)
        return this.flags[slot]; };
    EdgeFlagStore.prototype.has = function (id) { return this.get(id) !== void 0; };
    return EdgeFlagStore;
}()); var BaseVertexStore = (function () {
    function BaseVertexStore() {
        this.coords = new Float64Array(256 * 3);
        this.idList = new Uint32Array(256);
        this.count = 0;
    }
    Object.defineProperty(BaseVertexStore.prototype, "size", {
        get: function () { return this.count; },
        enumerable: false,
        configurable: true
    });
    BaseVertexStore.prototype.grow = function () { if (this.count < this.idList.length)
        return; var nextCapacity = this.idList.length * 2, nextCoords = new Float64Array(nextCapacity * 3); nextCoords.set(this.coords), this.coords = nextCoords; var nextIds = new Uint32Array(nextCapacity); nextIds.set(this.idList), this.idList = nextIds; };
    BaseVertexStore.prototype.set = function (id, xyz) { var existing = this.slotOf(id), slot = existing >= 0 ? existing : this.count; existing < 0 && (this.grow(), this.idList[slot] = id, this.count++, this.remember(id, slot)), this.coords[slot * 3] = xyz[0], this.coords[slot * 3 + 1] = xyz[1], this.coords[slot * 3 + 2] = xyz[2]; };
    BaseVertexStore.prototype.get = function (id) { var slot = this.slotOf(id); if (!(slot < 0))
        return [this.coords[slot * 3], this.coords[slot * 3 + 1], this.coords[slot * 3 + 2]]; };
    BaseVertexStore.prototype.has = function (id) { return this.slotOf(id) >= 0; };
    BaseVertexStore.prototype.entries = function () { var i_6; return __generator(this, function (_j) {
        switch (_j.label) {
            case 0:
                i_6 = 0;
                _j.label = 1;
            case 1:
                if (!(i_6 < this.count)) return [3, 4];
                return [4, [this.idList[i_6], [this.coords[i_6 * 3], this.coords[i_6 * 3 + 1], this.coords[i_6 * 3 + 2]]]];
            case 2:
                _j.sent();
                _j.label = 3;
            case 3:
                i_6++;
                return [3, 1];
            case 4: return [2];
        }
    }); };
    BaseVertexStore.prototype.ids = function () { var i_7; return __generator(this, function (_j) {
        switch (_j.label) {
            case 0:
                i_7 = 0;
                _j.label = 1;
            case 1:
                if (!(i_7 < this.count)) return [3, 4];
                return [4, this.idList[i_7]];
            case 2:
                _j.sent();
                _j.label = 3;
            case 3:
                i_7++;
                return [3, 1];
            case 4: return [2];
        }
    }); };
    return BaseVertexStore;
}()), MapVertexStore = (function (_super) {
    __extends(MapVertexStore, _super);
    function MapVertexStore() {
        var _this = _super.apply(this, __spreadArray([], __read(arguments), false)) || this;
        _this.index = new Map;
        return _this;
    }
    MapVertexStore.prototype.slotOf = function (id) { var slot = this.index.get(id); return slot === void 0 ? -1 : slot; };
    MapVertexStore.prototype.remember = function (id, slot) { this.index.set(id, slot); };
    return MapVertexStore;
}(BaseVertexStore)); var DefaultVertexStore = MapVertexStore; var GeometryBuilder = (function () {
    function GeometryBuilder() {
        this.vertices = new DefaultVertexStore;
        this.edges = new Map;
        this.edgeFlags = new EdgeFlagStore;
        this.faces = new Map;
        this.instances = [];
        this.sectionPlanes = [];
        this.texts = [];
        this.dimensions = [];
        this.constructionLines = [];
        this.constructionPoints = [];
    }
    return GeometryBuilder;
}()); function findChildTag(nodes, target) {
    var e_6, _j;
    try {
        for (var nodes_1 = __values(nodes), nodes_1_1 = nodes_1.next(); !nodes_1_1.done; nodes_1_1 = nodes_1.next()) {
            var n = nodes_1_1.value;
            if (n.tag === target)
                return n;
            var res = findChildTag(n.children, target);
            if (res)
                return res;
        }
    }
    catch (e_6_1) { e_6 = { error: e_6_1 }; }
    finally {
        try {
            if (nodes_1_1 && !nodes_1_1.done && (_j = nodes_1.return)) _j.call(nodes_1);
        }
        finally { if (e_6) throw e_6.error; }
    }
    return null;
} function findAllNodesRec(nodes, targetTag, results) {
    var e_7, _j;
    try {
        for (var nodes_2 = __values(nodes), nodes_2_1 = nodes_2.next(); !nodes_2_1.done; nodes_2_1 = nodes_2.next()) {
            var n = nodes_2_1.value;
            n.tag === targetTag && results.push(n), findAllNodesRec(n.children, targetTag, results);
        }
    }
    catch (e_7_1) { e_7 = { error: e_7_1 }; }
    finally {
        try {
            if (nodes_2_1 && !nodes_2_1.done && (_j = nodes_2.return)) _j.call(nodes_2);
        }
        finally { if (e_7) throw e_7.error; }
    }
} function extractEntityId(node) {
    var e_8, _j, e_9, _k;
    try {
        for (var _l = __values(node.children), _m = _l.next(); !_m.done; _m = _l.next()) {
            var child = _m.value;
            if (child.tag === "DE05")
                return parseVarInt(child.payload, 0, child.payload.length);
            if (child.tag === "DC05") {
                var payload = child.payload;
                if (payload.length >= 6 && payload[0] === 222 && payload[1] === 5) {
                    var de05Len = readU32(payload, 2);
                    return parseVarInt(payload, 6, de05Len);
                }
                else
                    return parseVarInt(payload, 0, payload.length);
            }
        }
    }
    catch (e_8_1) { e_8 = { error: e_8_1 }; }
    finally {
        try {
            if (_m && !_m.done && (_j = _l.return)) _j.call(_l);
        }
        finally { if (e_8) throw e_8.error; }
    }
    try {
        for (var _o = __values(node.children), _p = _o.next(); !_p.done; _p = _o.next()) {
            var child = _p.value;
            var res = extractEntityId(child);
            if (res !== null)
                return res;
        }
    }
    catch (e_9_1) { e_9 = { error: e_9_1 }; }
    finally {
        try {
            if (_p && !_p.done && (_k = _o.return)) _k.call(_o);
        }
        finally { if (e_9) throw e_9.error; }
    }
    return null;
} function tlvFlat(payload) { var pos = 0, out = []; for (; pos <= payload.length - 6;) {
    var tagBytes = payload.subarray(pos, pos + 2), tagHex = "";
    for (var i_8 = 0; i_8 < 2; i_8++) {
        var h = tagBytes[i_8].toString(16).toUpperCase();
        tagHex += h.length === 1 ? "0" + h : h;
    }
    var size = readU32(payload, pos + 2);
    if (pos + 6 + size > payload.length)
        break;
    out.push([tagHex, payload.subarray(pos + 6, pos + 6 + size)]), pos += 6 + size;
} return out; } function findFlat(seq, tag) {
    var e_10, _j;
    try {
        for (var seq_1 = __values(seq), seq_1_1 = seq_1.next(); !seq_1_1.done; seq_1_1 = seq_1.next()) {
            var _k = __read(seq_1_1.value, 2), t = _k[0], body = _k[1];
            if (t === tag)
                return body;
        }
    }
    catch (e_10_1) { e_10 = { error: e_10_1 }; }
    finally {
        try {
            if (seq_1_1 && !seq_1_1.done && (_j = seq_1.return)) _j.call(seq_1);
        }
        finally { if (e_10) throw e_10.error; }
    }
    return null;
} function extractUvTransforms(dc05Payload) {
    var e_11, _j;
    var dd05 = findFlat(tlvFlat(dc05Payload), "DD05");
    if (dd05 === null)
        return [null, null];
    var b136 = findFlat(tlvFlat(dd05), "B136");
    if (b136 === null)
        return [null, null];
    var b236 = findFlat(tlvFlat(b136), "B236");
    if (b236 === null)
        return [null, null];
    var t1027 = findFlat(tlvFlat(b236), "1027");
    if (t1027 === null)
        return [null, null];
    var sides = tlvFlat(t1027), result = [];
    try {
        for (var _k = __values(["1127", "1227"]), _l = _k.next(); !_l.done; _l = _k.next()) {
            var sideTag = _l.value;
            var side = findFlat(sides, sideTag), mat = null;
            if (side !== null) {
                var t1327 = findFlat(tlvFlat(side), "1327");
                if (t1327 !== null) {
                    var t1527 = findFlat(tlvFlat(t1327), "1527");
                    if (t1527 !== null && t1527.length === 72) {
                        mat = [];
                        for (var i_9 = 0; i_9 < 9; i_9++)
                            mat.push(readF64(t1527, i_9 * 8));
                    }
                }
            }
            result.push(mat);
        }
    }
    catch (e_11_1) { e_11 = { error: e_11_1 }; }
    finally {
        try {
            if (_l && !_l.done && (_j = _k.return)) _j.call(_k);
        }
        finally { if (e_11) throw e_11.error; }
    }
    return [result[0], result[1]];
} function extractGeometryFromNodes(elements, builder, options) {
    var e_12, _j, e_13, _k, e_14, _l, _m, _o;
    try {
        for (var elements_1 = __values(elements), elements_1_1 = elements_1.next(); !elements_1_1.done; elements_1_1 = elements_1.next()) {
            var el = elements_1_1.value;
            var tag = el.tag;
            if (tag === "C409") {
                var vId = extractEntityId(el), c509 = findChildTag(el.children, "C509");
                if (vId !== null && c509 && c509.payload.length >= 24) {
                    var x_1 = readF64(c509.payload, 0), y = readF64(c509.payload, 8), z = readF64(c509.payload, 16);
                    builder.vertices.set(vId, [x_1, y, z]);
                }
            }
            else if (tag === "B80B") {
                var eId = extractEntityId(el);
                if (eId !== null) {
                    var v1Node = findChildTag(el.children, "B90B"), v2Node = findChildTag(el.children, "BA0B"), v1 = v1Node ? parseVarInt(v1Node.payload, 0, v1Node.payload.length) : null, v2 = v2Node ? parseVarInt(v2Node.payload, 0, v2Node.payload.length) : null;
                    builder.edges.set(eId, [v1, v2]);
                    var d007 = el.children.find(function (c) { return c.tag === "D007"; });
                    if (d007) {
                        var d307 = d007.children.find(function (c) { return c.tag === "D307"; });
                        d307 && d307.payload.length > 0 && builder.edgeFlags.set(eId, d307.payload[0]);
                    }
                }
            }
            else if (tag === "AC0D") {
                var fId = extractEntityId(el);
                if (fId !== null) {
                    var normal = [0, 0, 1], ad0d = findChildTag(el.children, "AD0D");
                    if (ad0d && ad0d.payload.length >= 24) {
                        var nx = readF64(ad0d.payload, 0), ny = readF64(ad0d.payload, 8), nz = readF64(ad0d.payload, 16);
                        normal = [nx, ny, nz];
                    }
                    var ae0d = findChildTag(el.children, "AE0D"), loops = [];
                    if (ae0d) {
                        var loopNodes = [];
                        findAllNodesRec(ae0d.children, "9411", loopNodes);
                        try {
                            for (var loopNodes_1 = (e_13 = void 0, __values(loopNodes)), loopNodes_1_1 = loopNodes_1.next(); !loopNodes_1_1.done; loopNodes_1_1 = loopNodes_1.next()) {
                                var ln = loopNodes_1_1.value;
                                var coEdges = [], coNodes = [];
                                findAllNodesRec(ln.children, "A00F", coNodes);
                                try {
                                    for (var coNodes_1 = (e_14 = void 0, __values(coNodes)), coNodes_1_1 = coNodes_1.next(); !coNodes_1_1.done; coNodes_1_1 = coNodes_1.next()) {
                                        var cn = coNodes_1_1.value;
                                        var payload = cn.payload, edgeId = null, orient = null, subPos = 0;
                                        for (; subPos < payload.length - 6;) {
                                            var subSize = readU32(payload, subPos + 2);
                                            if (subPos + 6 + subSize <= payload.length) {
                                                var val = parseVarInt(payload, subPos + 6, subSize);
                                                payload[subPos] === 161 && payload[subPos + 1] === 15 ? edgeId = val : payload[subPos] === 162 && payload[subPos + 1] === 15 && (orient = val);
                                            }
                                            subPos += 6 + subSize;
                                        }
                                        edgeId !== null && orient !== null && coEdges.push({ edgeId: edgeId, orientation: orient === 0 ? 1 : -1 });
                                    }
                                }
                                catch (e_14_1) { e_14 = { error: e_14_1 }; }
                                finally {
                                    try {
                                        if (coNodes_1_1 && !coNodes_1_1.done && (_l = coNodes_1.return)) _l.call(coNodes_1);
                                    }
                                    finally { if (e_14) throw e_14.error; }
                                }
                                coEdges.length > 0 && loops.push(coEdges);
                            }
                        }
                        catch (e_13_1) { e_13 = { error: e_13_1 }; }
                        finally {
                            try {
                                if (loopNodes_1_1 && !loopNodes_1_1.done && (_k = loopNodes_1.return)) _k.call(loopNodes_1);
                            }
                            finally { if (e_13) throw e_13.error; }
                        }
                    }
                    var faceMatId = null, uvFront = null, uvBack = null, faceHidden = !1, d007 = el.children.find(function (c) { return c.tag === "D007"; });
                    if (d007) {
                        var d107 = d007.children.find(function (c) { return c.tag === "D107"; });
                        d107 && (faceMatId = parseVarInt(d107.payload, 0, d107.payload.length));
                        var dc05 = d007.children.find(function (c) { return c.tag === "DC05"; });
                        dc05 && (_m = extractUvTransforms(dc05.payload), _o = __read(_m, 2), uvFront = _o[0], uvBack = _o[1], _m);
                        var d307 = d007.children.find(function (c) { return c.tag === "D307"; });
                        d307 && d307.payload.length > 0 && (faceHidden = (d307.payload[0] & 1) !== 0);
                    }
                    var backMatId = null, af0d = el.children.find(function (c) { return c.tag === "AF0D"; });
                    af0d && af0d.payload.length > 0 && (backMatId = parseVarInt(af0d.payload, 0, af0d.payload.length)), builder.faces.set(fId, { loops: loops, normal: normal, materialId: faceMatId, backMaterialId: backMatId, uvTransform: uvFront, uvTransformBack: uvBack, hidden: faceHidden });
                }
            }
            else if (tag === "6419") {
                var nodesToSearch = el.children.length > 0 ? el.children : [el], guid = null, defIdx = null, name = null, matrix = [], guidNode = findChildTag(nodesToSearch, "6819");
                if (guidNode && guidNode.payload.length === 16) {
                    var hex = "";
                    for (var i_10 = 0; i_10 < 16; i_10++) {
                        var h = guidNode.payload[i_10].toString(16).toUpperCase();
                        hex += h.length === 1 ? "0" + h : h;
                    }
                    guid = hex;
                }
                var defIdxNode = findChildTag(nodesToSearch, "6719");
                defIdxNode && (defIdx = parseVarInt(defIdxNode.payload, 0, defIdxNode.payload.length));
                var nameNode = findChildTag(nodesToSearch, "6519");
                if (nameNode)
                    try {
                        name = new TextDecoder("utf-8").decode(nameNode.payload).replace(/\0/g, "").trim();
                    }
                    catch (e) {
                        name = "", emitLog(options, "debug", "Failed to decode instance name: ".concat(e.message));
                    }
                var matNode = findChildTag(nodesToSearch, "6619");
                if (matNode && matNode.payload.length >= 104)
                    for (var idx = 0; idx < 13; idx++)
                        matrix.push(readF64(matNode.payload, idx * 8));
                var instMatId = null, instLayerId = null, instHidden = !1, d007 = el.children.find(function (c) { return c.tag === "D007"; });
                if (d007) {
                    var d107 = d007.children.find(function (c) { return c.tag === "D107"; });
                    d107 && (instMatId = parseVarInt(d107.payload, 0, d107.payload.length));
                    var d207 = d007.children.find(function (c) { return c.tag === "D207"; });
                    if (d207 && d207.payload.length > 0) {
                        var p = d207.payload;
                        instLayerId = p.length === 1 ? p[0] : parseVarInt(p, 0, p.length);
                    }
                    var d307 = d007.children.find(function (c) { return c.tag === "D307"; });
                    d307 && d307.payload.length > 0 && (instHidden = (d307.payload[0] & 1) !== 0);
                }
                builder.instances.push({ offset: el.offset, refGuid: guid || "", refIdx: defIdx !== null ? defIdx : -1, name: name || "", matrix: matrix, materialId: instMatId, layerId: instLayerId, hidden: instHidden, children: el.children });
            }
            else
                el.children && el.children.length > 0 && extractGeometryFromNodes(el.children, builder, options);
        }
    }
    catch (e_12_1) { e_12 = { error: e_12_1 }; }
    finally {
        try {
            if (elements_1_1 && !elements_1_1.done && (_j = elements_1.return)) _j.call(elements_1);
        }
        finally { if (e_12) throw e_12.error; }
    }
} function collectLayers(nodes, layerIdToName, options, layerHidden) {
    var e_15, _j, e_16, _k;
    if (layerIdToName === void 0) { layerIdToName = new Map; }
    try {
        for (var nodes_3 = __values(nodes), nodes_3_1 = nodes_3.next(); !nodes_3_1.done; nodes_3_1 = nodes_3.next()) {
            var el = nodes_3_1.value;
            if (el.tag === "993A") {
                try {
                    for (var _l = (e_16 = void 0, __values(el.children)), _m = _l.next(); !_m.done; _m = _l.next()) {
                        var child = _m.value;
                        if (child.tag === "8C3C") {
                            var dc05 = findChildTag(child.children, "DC05"), nameNode = findChildTag(child.children, "8D3C");
                            if (dc05 && nameNode) {
                                var payload = dc05.payload, lId = void 0;
                                if (payload.length >= 6 && payload[0] === 222 && payload[1] === 5) {
                                    var de05Len = readU32(payload, 2);
                                    lId = parseVarInt(payload, 6, de05Len);
                                }
                                else
                                    lId = parseVarInt(payload, 0, payload.length);
                                var lName = "";
                                try {
                                    lName = new TextDecoder("utf-8").decode(nameNode.payload).replace(/\0/g, "").trim();
                                }
                                catch (e) {
                                    emitLog(options, "debug", "Failed to decode layer name for id ".concat(lId, ": ").concat(e.message));
                                }
                                if (layerIdToName.set(lId, lName), layerHidden) {
                                    var hiddenNode = findChildTag(child.children, "8E3C");
                                    hiddenNode && hiddenNode.payload.length > 0 && layerHidden.set(lName, hiddenNode.payload[0] === 1);
                                }
                            }
                        }
                    }
                }
                catch (e_16_1) { e_16 = { error: e_16_1 }; }
                finally {
                    try {
                        if (_m && !_m.done && (_k = _l.return)) _k.call(_l);
                    }
                    finally { if (e_16) throw e_16.error; }
                }
            }
            el.children && el.children.length > 0 && collectLayers(el.children, layerIdToName, options, layerHidden);
        }
    }
    catch (e_15_1) { e_15 = { error: e_15_1 }; }
    finally {
        try {
            if (nodes_3_1 && !nodes_3_1.done && (_j = nodes_3.return)) _j.call(nodes_3);
        }
        finally { if (e_15) throw e_15.error; }
    }
    return layerIdToName;
} function collectDefs(nodes, defsDict, options) {
    var e_17, _j, e_18, _k;
    if (defsDict === void 0) { defsDict = new Map; }
    try {
        for (var nodes_4 = __values(nodes), nodes_4_1 = nodes_4.next(); !nodes_4_1.done; nodes_4_1 = nodes_4.next()) {
            var el = nodes_4_1.value;
            if (el.tag === "7C15") {
                var guid = null, name = null, isImage = !1, facesCamera = !1, shadowsFaceSun = !1;
                try {
                    for (var _l = (e_18 = void 0, __values(el.children)), _m = _l.next(); !_m.done; _m = _l.next()) {
                        var child = _m.value;
                        if (child.tag === "7D15" && child.payload.length === 16) {
                            var hex = "";
                            for (var i_11 = 0; i_11 < 16; i_11++) {
                                var h = child.payload[i_11].toString(16).toUpperCase();
                                hex += h.length === 1 ? "0" + h : h;
                            }
                            guid = hex;
                        }
                        else if (child.tag === "7E15")
                            try {
                                name = new TextDecoder("utf-8").decode(child.payload).replace(/\0/g, "").trim();
                            }
                            catch (e) {
                                name = "", emitLog(options, "debug", "Failed to decode definition name: ".concat(e.message));
                            }
                        else if (child.tag === "8315" && child.payload.length > 0)
                            isImage = parseVarInt(child.payload, 0, child.payload.length) === 2;
                        else if (child.tag === "581B") {
                            var pos = 0, pl = child.payload;
                            for (; pos <= pl.length - 6;) {
                                var subSize = readU32(pl, pos + 2);
                                if (pos + 6 + subSize > pl.length)
                                    break;
                                pl[pos] === 93 && pl[pos + 1] === 27 && subSize >= 1 ? facesCamera = parseVarInt(pl, pos + 6, subSize) === 1 : pl[pos] === 94 && pl[pos + 1] === 27 && subSize >= 1 && (shadowsFaceSun = parseVarInt(pl, pos + 6, subSize) === 1), pos += 6 + subSize;
                            }
                        }
                    }
                }
                catch (e_18_1) { e_18 = { error: e_18_1 }; }
                finally {
                    try {
                        if (_m && !_m.done && (_k = _l.return)) _k.call(_l);
                    }
                    finally { if (e_18) throw e_18.error; }
                }
                var entId = extractEntityId(el);
                if (entId !== null) {
                    var builder = new GeometryBuilder;
                    extractGeometryFromNodes(el.children, builder, options), defsDict.set(entId, { guid: guid || "", name: name || "", isImage: isImage, alwaysFacesCamera: facesCamera, shadowsFaceSun: shadowsFaceSun, builder: builder });
                }
            }
            el.children && el.children.length > 0 && collectDefs(el.children, defsDict, options);
        }
    }
    catch (e_17_1) { e_17 = { error: e_17_1 }; }
    finally {
        try {
            if (nodes_4_1 && !nodes_4_1.done && (_j = nodes_4.return)) _j.call(nodes_4);
        }
        finally { if (e_17) throw e_17.error; }
    }
    return defsDict;
} function extractDynamicProperties(d007, options) { var dc05 = d007.children.find(function (c) { return c.tag === "DC05"; }); if (!dc05)
    return {}; var propContainerTags = new Set(["DD05", "B536", "B136", "B236", "B336", "B036", "A438"]), propElements = parseTlvRecursive(dc05.payload, 0, dc05.payload.length, propContainerTags), properties = {}, currentKey = null; function extractProps(nodes) {
    var e_19, _j;
    try {
        for (var nodes_5 = __values(nodes), nodes_5_1 = nodes_5.next(); !nodes_5_1.done; nodes_5_1 = nodes_5.next()) {
            var n = nodes_5_1.value;
            var tag = n.tag;
            if (tag === "B636")
                try {
                    currentKey = new TextDecoder("utf-8").decode(n.payload).replace(/\0/g, "").trim();
                }
                catch (e) {
                    currentKey = null, emitLog(options, "debug", "Failed to decode dynamic property key: ".concat(e.message));
                }
            else if (tag === "AD38" && currentKey) {
                try {
                    var val = new TextDecoder("utf-8").decode(n.payload).replace(/\0/g, "").trim();
                    properties[currentKey] = val;
                }
                catch (e) {
                    emitLog(options, "debug", "Failed to decode dynamic property value for key ".concat(currentKey, ": ").concat(e.message));
                }
                currentKey = null;
            }
            n.children && n.children.length > 0 && extractProps(n.children);
        }
    }
    catch (e_19_1) { e_19 = { error: e_19_1 }; }
    finally {
        try {
            if (nodes_5_1 && !nodes_5_1.done && (_j = nodes_5.return)) _j.call(nodes_5);
        }
        finally { if (e_19) throw e_19.error; }
    }
} return extractProps(propElements), properties; } var VFF_ATTR_DOUBLE_TAGS = new Set(["AF38", "A938"]); function decodeVffAttrValue(a438Node) { var _a2; if (!a438Node.children || a438Node.children.length === 0)
    return null; var child = a438Node.children[0], tag = child.tag, payload = child.payload; if (tag === "AD38")
    try {
        return new TextDecoder("utf-8").decode(payload).replace(/\0/g, "").trim();
    }
    catch (e) {
        return null;
    } return VFF_ATTR_DOUBLE_TAGS.has(tag) && payload.length === 8 ? readF64(payload, 0) : tag === "A738" && payload.length === 4 ? readI32(payload, 0) : (tag === "B438" || tag === "B538") && payload.length === 24 ? [readF64(payload, 0), readF64(payload, 8), readF64(payload, 16)] : tag === "AE38" ? ((_a2 = child.children) != null ? _a2 : []).map(decodeVffAttrValue) : null; } function stringifyVffAttrValue(value) { return value == null ? "" : Array.isArray(value) ? value.map(function (v) { return stringifyVffAttrValue(v); }).join(",") : String(value); } function extractAttributeDictionaries(d007, options) { var dictionaries = {}, dc05 = d007.children.find(function (c) { return c.tag === "DC05"; }); if (!dc05)
    return dictionaries; var propContainerTags = new Set(["DD05", "B536", "B136", "B236", "B336", "B036", "A438", "AE38"]), propElements = parseTlvRecursive(dc05.payload, 0, dc05.payload.length, propContainerTags), currentKey = null; function extractEntries(nodes, entries) {
    var e_20, _j;
    try {
        for (var nodes_6 = __values(nodes), nodes_6_1 = nodes_6.next(); !nodes_6_1.done; nodes_6_1 = nodes_6.next()) {
            var n = nodes_6_1.value;
            var tag = n.tag;
            if (tag === "B636")
                try {
                    currentKey = new TextDecoder("utf-8").decode(n.payload).replace(/\0/g, "").trim();
                }
                catch (e) {
                    currentKey = null, emitLog(options, "debug", "Failed to decode attribute dictionary key: ".concat(e.message));
                }
            else
                tag === "A438" && currentKey ? (entries[currentKey] = decodeVffAttrValue(n), currentKey = null) : n.children && n.children.length > 0 && extractEntries(n.children, entries);
        }
    }
    catch (e_20_1) { e_20 = { error: e_20_1 }; }
    finally {
        try {
            if (nodes_6_1 && !nodes_6_1.done && (_j = nodes_6.return)) _j.call(nodes_6);
        }
        finally { if (e_20) throw e_20.error; }
    }
} function walk2(nodes) { for (var i_12 = 0; i_12 < nodes.length; i_12++)
    if (nodes[i_12].tag === "B436") {
        var name = "";
        try {
            name = new TextDecoder("utf-8").decode(nodes[i_12].payload).replace(/\0/g, "").trim();
        }
        catch (e) {
            emitLog(options, "debug", "Failed to decode attribute dictionary name: ".concat(e.message));
        }
        var entries = {};
        currentKey = null, i_12 + 1 < nodes.length && nodes[i_12 + 1].children && extractEntries(nodes[i_12 + 1].children, entries), dictionaries[name] = entries;
    }
    else
        nodes[i_12].children && nodes[i_12].children.length > 0 && walk2(nodes[i_12].children); } return walk2(propElements), dictionaries; } var GENERIC_DEFINITION_NAME_PATTERN = /^(?:Group|Component)\d*#\d+$/; function isGenericDefinitionName(name) { return GENERIC_DEFINITION_NAME_PATTERN.test(name); } var NAME_OVERRIDE_KEYS = ["name", "label", "code"]; function findNameOverride(attributeDicts) {
    var e_21, _j, e_22, _k;
    if (!attributeDicts)
        return null;
    try {
        for (var _l = __values(Object.keys(attributeDicts)), _m = _l.next(); !_m.done; _m = _l.next()) {
            var dictName = _m.value;
            if (dictName === "dynamic_attributes" || dictName === "SU_InstanceSet")
                continue;
            var entries = attributeDicts[dictName];
            try {
                for (var NAME_OVERRIDE_KEYS_1 = (e_22 = void 0, __values(NAME_OVERRIDE_KEYS)), NAME_OVERRIDE_KEYS_1_1 = NAME_OVERRIDE_KEYS_1.next(); !NAME_OVERRIDE_KEYS_1_1.done; NAME_OVERRIDE_KEYS_1_1 = NAME_OVERRIDE_KEYS_1.next()) {
                    var key = NAME_OVERRIDE_KEYS_1_1.value;
                    if (!(key in entries))
                        continue;
                    var val = stringifyVffAttrValue(entries[key]);
                    if (val)
                        return val;
                }
            }
            catch (e_22_1) { e_22 = { error: e_22_1 }; }
            finally {
                try {
                    if (NAME_OVERRIDE_KEYS_1_1 && !NAME_OVERRIDE_KEYS_1_1.done && (_k = NAME_OVERRIDE_KEYS_1.return)) _k.call(NAME_OVERRIDE_KEYS_1);
                }
                finally { if (e_22) throw e_22.error; }
            }
        }
    }
    catch (e_21_1) { e_21 = { error: e_21_1 }; }
    finally {
        try {
            if (_m && !_m.done && (_j = _l.return)) _j.call(_l);
        }
        finally { if (e_21) throw e_21.error; }
    }
    return null;
} function reconstructLoopVertices(loop, edges) {
    var e_23, _j;
    var loopVerts = [];
    try {
        for (var loop_1 = __values(loop), loop_1_1 = loop_1.next(); !loop_1_1.done; loop_1_1 = loop_1.next()) {
            var _k = loop_1_1.value, edgeId = _k.edgeId, orientation = _k.orientation;
            var edge = edges.get(edgeId);
            if (edge) {
                var _l = __read(edge, 2), v1 = _l[0], v2 = _l[1], vStart = orientation === 1 ? v1 : v2;
                vStart !== null && (loopVerts.length === 0 || loopVerts[loopVerts.length - 1] !== vStart) && loopVerts.push(vStart);
            }
        }
    }
    catch (e_23_1) { e_23 = { error: e_23_1 }; }
    finally {
        try {
            if (loop_1_1 && !loop_1_1.done && (_j = loop_1.return)) _j.call(loop_1);
        }
        finally { if (e_23) throw e_23.error; }
    }
    return loopVerts.length > 1 && loopVerts[0] === loopVerts[loopVerts.length - 1] && loopVerts.pop(), loopVerts;
} function decodeXmlEntities(value) { return value.replace(/&(lt|gt|amp|apos|quot|#\d+|#x[0-9a-fA-F]+);/g, function (whole, entity) { switch (entity) {
    case "lt": return "<";
    case "gt": return ">";
    case "amp": return "&";
    case "apos": return "'";
    case "quot": return '"';
    default:
        if (entity[0] === "#") {
            var codePoint = entity[1] === "x" || entity[1] === "X" ? parseInt(entity.slice(2), 16) : parseInt(entity.slice(1), 10);
            return Number.isFinite(codePoint) ? String.fromCodePoint(codePoint) : whole;
        }
        return whole;
} }); } function parseMaterialXml(xmlText) { var match = xmlText.match(/<(?:[a-zA-Z0-9_]+:)?material\b([^>]*)\/?>/); if (!match)
    return null; var attrsString = match[1], getAttr = function (name2) { var attrRegex = new RegExp("\\b".concat(name2, "\\s*=\\s*(?:\"([^\"]*)\"|'([^']*)')")), m = attrsString.match(attrRegex), raw = m ? m[1] !== void 0 ? m[1] : m[2] : null; return raw === null ? null : decodeXmlEntities(raw); }, name = getAttr("name") || "unknown", colorRed = parseInt(getAttr("colorRed") || "128", 10), colorGreen = parseInt(getAttr("colorGreen") || "128", 10), colorBlue = parseInt(getAttr("colorBlue") || "128", 10), trans; if (getAttr("useTrans") === "1") {
    var rawTrans = parseFloat(getAttr("trans") || "0");
    trans = Math.min(Math.max(1 - rawTrans, 0), 1);
}
else
    trans = 1; var colorized = getAttr("type") === "2", colorizeTypeRaw = parseInt(getAttr("colorizeType") || "0", 10), colorizeType = Number.isNaN(colorizeTypeRaw) ? 0 : colorizeTypeRaw, textureMatch = xmlText.match(/<(?:[a-zA-Z0-9_]+:)?texture\b([^>]*)\/?>/), hasTexture = !1, textureFilename = "", xScale = 0, yScale = 0; if (textureMatch) {
    hasTexture = !0;
    var texAttrs_1 = textureMatch[1], getTexAttr = function (n) { var r = new RegExp("\\b".concat(n, "\\s*=\\s*(?:\"([^\"]*)\"|'([^']*)')")), m = texAttrs_1.match(r), raw = m ? m[1] !== void 0 ? m[1] : m[2] : null; return raw === null ? null : decodeXmlEntities(raw); };
    textureFilename = getTexAttr("textureFilename") || "";
    var xs = parseFloat(getTexAttr("xScale") || "0");
    xScale = Number.isNaN(xs) ? 0 : xs;
    var ys = parseFloat(getTexAttr("yScale") || "0");
    yScale = Number.isNaN(ys) ? 0 : ys;
} var imageMatch = xmlText.match(/<(?:[a-zA-Z0-9_]+:)?image\b[^>]*\bpath\s*=\s*(?:"([^"]*)"|'([^']*)')[^>]*\/?>/), imagePath = imageMatch ? decodeXmlEntities(imageMatch[1] !== void 0 ? imageMatch[1] : imageMatch[2]) : ""; return { name: name, r: colorRed, g: colorGreen, b: colorBlue, trans: trans, colorized: colorized, colorizeType: colorizeType, hasTexture: hasTexture, textureFilename: textureFilename, xScale: xScale, yScale: yScale, imagePath: imagePath }; } function parseStyleXml(xmlText) { var _a2, _b2; var styleMatch = xmlText.match(/<(?:[a-zA-Z0-9_]+:)?style\b([^>]*)>/); if (!styleMatch)
    return null; var nameMatch = styleMatch[1].match(/\bname\s*=\s*(?:"([^"]*)"|'([^']*)')/), name = nameMatch ? nameMatch[1] !== void 0 ? nameMatch[1] : nameMatch[2] : "", colors = {}, itemRegex = /<(?:[a-zA-Z0-9_]+:)?item\s+id\s*=\s*(?:"(\d+)"|'(\d+)')[^>]*>([\s\S]*?)<\/(?:[a-zA-Z0-9_]+:)?item>/g, m; for (; (m = itemRegex.exec(xmlText)) !== null;) {
    var id = m[1] !== void 0 ? m[1] : m[2];
    if (id !== "2002" && id !== "2003")
        continue;
    var variantMatch = m[3].match(/<(?:[a-zA-Z0-9_]+:)?variant\b[^>]*>(-?\d+)<\/(?:[a-zA-Z0-9_]+:)?variant>/);
    if (!variantMatch)
        continue;
    var raw = parseInt(variantMatch[1], 10);
    if (Number.isNaN(raw))
        continue;
    var v = raw >>> 0;
    colors[id] = [v & 255, v >> 8 & 255, v >> 16 & 255];
} return { name: name, frontColor: (_a2 = colors[2002]) != null ? _a2 : null, backColor: (_b2 = colors[2003]) != null ? _b2 : null }; } function lstripChars(s, chars) { var i = 0; for (; i < s.length && chars.includes(s[i]);)
    i++; return s.slice(i); } function resolveTextureBytes(materialFiles, xmlName, filename, imagePath) {
    var e_24, _j, e_25, _k;
    var names = Object.keys(materialFiles), slashIdx = xmlName.lastIndexOf("/"), folder = slashIdx >= 0 ? xmlName.slice(0, slashIdx) : "", data = null, resolvedFilename = filename, candidate = filename ? "".concat(folder, "/").concat(filename) : null;
    if (candidate && names.includes(candidate))
        data = materialFiles[candidate];
    else
        try {
            for (var names_1 = __values(names), names_1_1 = names_1.next(); !names_1_1.done; names_1_1 = names_1.next()) {
                var entry = names_1_1.value;
                if (entry.startsWith(folder + "/") && entry !== xmlName && !entry.toLowerCase().endsWith(".xml")) {
                    data = materialFiles[entry], resolvedFilename || (resolvedFilename = entry.split("/").pop() || "");
                    break;
                }
            }
        }
        catch (e_24_1) { e_24 = { error: e_24_1 }; }
        finally {
            try {
                if (names_1_1 && !names_1_1.done && (_j = names_1.return)) _j.call(names_1);
            }
            finally { if (e_24) throw e_24.error; }
        }
    if (data === null) {
        var imgPath = lstripChars(imagePath, "./"), candidates = [imgPath, folder ? "".concat(folder, "/").concat(imgPath) : imgPath];
        try {
            for (var candidates_1 = __values(candidates), candidates_1_1 = candidates_1.next(); !candidates_1_1.done; candidates_1_1 = candidates_1.next()) {
                var cand = candidates_1_1.value;
                if (cand && names.includes(cand)) {
                    data = materialFiles[cand], resolvedFilename || (resolvedFilename = cand.split("/").pop() || "");
                    break;
                }
            }
        }
        catch (e_25_1) { e_25 = { error: e_25_1 }; }
        finally {
            try {
                if (candidates_1_1 && !candidates_1_1.done && (_k = candidates_1.return)) _k.call(candidates_1);
            }
            finally { if (e_25) throw e_25.error; }
        }
    }
    return { data: data, filename: resolvedFilename };
} function transformPoint(matrix, point) { if (!matrix || matrix.length < 12)
    return point; var _j = __read(point, 3), x = _j[0], y = _j[1], z = _j[2]; if (matrix.length === 16) {
    var tx = matrix[0] * x + matrix[4] * y + matrix[8] * z + matrix[12], ty = matrix[1] * x + matrix[5] * y + matrix[9] * z + matrix[13], tz = matrix[2] * x + matrix[6] * y + matrix[10] * z + matrix[14];
    return [tx, ty, tz];
}
else {
    var tx = matrix[0] * x + matrix[1] * y + matrix[2] * z + matrix[9], ty = matrix[3] * x + matrix[4] * y + matrix[5] * z + matrix[10], tz = matrix[6] * x + matrix[7] * y + matrix[8] * z + matrix[11];
    return [tx, ty, tz];
} } function multiplyMatrices(a, b) { if (!a || a.length === 0)
    return b; if (!b || b.length === 0)
    return a; if (a.length === 16 && b.length === 16) {
    var result = new Array(16).fill(0);
    for (var row = 0; row < 4; row++)
        for (var col = 0; col < 4; col++) {
            var s = 0;
            for (var k = 0; k < 4; k++)
                s += a[k * 4 + row] * b[col * 4 + k];
            result[col * 4 + row] = s;
        }
    return result;
}
else {
    var aPad = a.length < 13 ? __spreadArray(__spreadArray([], __read(a), false), __read(new Array(13 - a.length).fill(0)), false) : a, bPad = b.length < 13 ? __spreadArray(__spreadArray([], __read(b), false), __read(new Array(13 - b.length).fill(0)), false) : b;
    a.length < 13 && aPad[12] === 0 && (aPad[12] = 1), b.length < 13 && bPad[12] === 0 && (bPad[12] = 1);
    var p_r0 = [aPad[0], aPad[1], aPad[2], aPad[9]], p_r1 = [aPad[3], aPad[4], aPad[5], aPad[10]], p_r2 = [aPad[6], aPad[7], aPad[8], aPad[11]], c_c0 = [bPad[0], bPad[3], bPad[6], 0], c_c1 = [bPad[1], bPad[4], bPad[7], 0], c_c2 = [bPad[2], bPad[5], bPad[8], 0], c_c3 = [bPad[9], bPad[10], bPad[11], 1], dot = function (row, col) { return row[0] * col[0] + row[1] * col[1] + row[2] * col[2] + row[3] * col[3]; }, out = new Array(13).fill(0);
    return out[0] = dot(p_r0, c_c0), out[1] = dot(p_r0, c_c1), out[2] = dot(p_r0, c_c2), out[3] = dot(p_r1, c_c0), out[4] = dot(p_r1, c_c1), out[5] = dot(p_r1, c_c2), out[6] = dot(p_r2, c_c0), out[7] = dot(p_r2, c_c1), out[8] = dot(p_r2, c_c2), out[9] = dot(p_r0, c_c3), out[10] = dot(p_r1, c_c3), out[11] = dot(p_r2, c_c3), out[12] = aPad[12] * bPad[12], out;
} } var steiners = new Set, filteredOut = !1; function earcut(data, holeIndices, dim) {
    if (dim === void 0) { dim = 2; }
    var hasHoles = holeIndices && holeIndices.length, outerLen = hasHoles ? holeIndices[0] * dim : data.length;
    steiners.size && steiners.clear();
    var outerNode = linkedList(data, 0, outerLen, dim, !0), triangles = [];
    if (!outerNode || outerNode.next === outerNode.prev)
        return triangles;
    var minX = 0, minY = 0, invSize = 0;
    if (hasHoles && (outerNode = eliminateHoles(data, holeIndices, outerNode, dim)), data.length > 80 * dim) {
        minX = data[0], minY = data[1];
        var maxX = minX, maxY = minY;
        for (var i_13 = dim; i_13 < outerLen; i_13 += dim) {
            var x_2 = data[i_13], y = data[i_13 + 1];
            x_2 < minX && (minX = x_2), y < minY && (minY = y), x_2 > maxX && (maxX = x_2), y > maxY && (maxY = y);
        }
        invSize = Math.max(maxX - minX, maxY - minY), invSize = invSize !== 0 ? 32767 / invSize : 0;
    }
    return earcutLinked(outerNode, triangles, minX, minY, invSize), triangles;
} function linkedList(data, start, end, dim, clockwise) { var last = null; if (clockwise === signedArea(data, start, end, dim) > 0)
    for (var i_14 = start; i_14 < end; i_14 += dim)
        last = insertNode(i_14 / dim | 0, data[i_14], data[i_14 + 1], last);
else
    for (var i_15 = end - dim; i_15 >= start; i_15 -= dim)
        last = insertNode(i_15 / dim | 0, data[i_15], data[i_15 + 1], last); return last && equals(last, last.next) && (removeNode(last), last = last.next), last; } function filterPoints(start, end) {
    if (end === void 0) { end = start; }
    var full = end === start, p = start, again;
    do
        again = !1, p !== p.next && (steiners.size === 0 || !steiners.has(p)) && (equals(p, p.next) || area(p.prev, p, p.next) === 0) ? ((full || p === end) && (end = p.prev), filteredOut = !0, removeNode(p), p = p.prev, again = !0) : (full || p !== end) && (p = p.next, again = !full);
    while (again || p !== end);
    return end;
} function earcutLinked(ear, triangles, minX, minY, invSize) { invSize && indexCurve(ear, minX, minY, invSize); var stop = ear, cured = !1; for (; ear.prev !== ear.next;) {
    var prev = ear.prev, next = ear.next;
    if (area(prev, ear, next) < 0 && (invSize ? isEarHashed(ear, minX, minY, invSize) : isEar(ear))) {
        triangles.push(prev.i, ear.i, next.i), removeNode(ear), ear = next, stop = next;
        continue;
    }
    if (ear = next, ear === stop) {
        if (filteredOut = !1, ear = filterPoints(ear), filteredOut) {
            stop = ear;
            continue;
        }
        if (!cured) {
            ear = cureLocalIntersections(ear, triangles), stop = ear, cured = !0;
            continue;
        }
        splitEarcut(ear, triangles, minX, minY, invSize);
        break;
    }
} } function isEar(ear) { var a = ear.prev, b = ear, c = ear.next, ax = a.x, bx = b.x, cx = c.x, ay = a.y, by = b.y, cy = c.y, x0 = Math.min(ax, bx, cx), y0 = Math.min(ay, by, cy), x1 = Math.max(ax, bx, cx), y1 = Math.max(ay, by, cy), p = c.next; for (; p !== a;) {
    if (p.x >= x0 && p.x <= x1 && p.y >= y0 && p.y <= y1 && !(ax === p.x && ay === p.y) && pointInTriangle(ax, ay, bx, by, cx, cy, p.x, p.y) && area(p.prev, p, p.next) >= 0)
        return !1;
    p = p.next;
} return !0; } function isEarHashed(ear, minX, minY, invSize) { var a = ear.prev, b = ear, c = ear.next, ax = a.x, bx = b.x, cx = c.x, ay = a.y, by = b.y, cy = c.y, x0 = Math.min(ax, bx, cx), y0 = Math.min(ay, by, cy), x1 = Math.max(ax, bx, cx), y1 = Math.max(ay, by, cy), minZ = zOrder(x0, y0, minX, minY, invSize), maxZ = zOrder(x1, y1, minX, minY, invSize), p = ear.prevZ; for (; p && p.z >= minZ;) {
    if (p.x >= x0 && p.x <= x1 && p.y >= y0 && p.y <= y1 && p !== c && !(ax === p.x && ay === p.y) && pointInTriangle(ax, ay, bx, by, cx, cy, p.x, p.y) && area(p.prev, p, p.next) >= 0)
        return !1;
    p = p.prevZ;
} var n = ear.nextZ; for (; n && n.z <= maxZ;) {
    if (n.x >= x0 && n.x <= x1 && n.y >= y0 && n.y <= y1 && n !== c && !(ax === n.x && ay === n.y) && pointInTriangle(ax, ay, bx, by, cx, cy, n.x, n.y) && area(n.prev, n, n.next) >= 0)
        return !1;
    n = n.nextZ;
} return !0; } function cureLocalIntersections(start, triangles) { var p = start, cured = !1; do {
    var a = p.prev, b = p.next.next;
    intersects(a, p, p.next, b, !1) && locallyInside(a, b) && locallyInside(b, a) && (triangles.push(a.i, p.i, b.i), removeNode(p), removeNode(p.next), p = start = b, cured = !0), p = p.next;
} while (p !== start); return cured ? filterPoints(p) : p; } function splitEarcut(start, triangles, minX, minY, invSize) { var a = start; do {
    var b = a.next.next;
    for (; b !== a.prev;) {
        if (a.i !== b.i && isValidDiagonal(a, b)) {
            var c = splitPolygon(a, b);
            a = filterPoints(a, a.next), c = filterPoints(c, c.next), earcutLinked(a, triangles, minX, minY, invSize), earcutLinked(c, triangles, minX, minY, invSize);
            return;
        }
        b = b.next;
    }
    a = a.next;
} while (a !== start); } var indexActive = !1; function eliminateHoles(data, holeIndices, outerNode, dim) { var queue = []; for (var i_16 = 0, len = holeIndices.length; i_16 < len; i_16++) {
    var start = holeIndices[i_16] * dim, end = i_16 < len - 1 ? holeIndices[i_16 + 1] * dim : data.length, list = linkedList(data, start, end, dim, !1);
    list === list.next && steiners.add(list), queue.push(getLeftmost(list));
} queue.sort(compareXYSlope), buildBlockIndex(data.length / dim, holeIndices.length), indexSegment(outerNode, outerNode), indexActive = !0; for (var i_17 = 0; i_17 < queue.length; i_17++)
    outerNode = eliminateHole(queue[i_17], outerNode); return indexActive = !1, filterPoints(outerNode); } function compareXYSlope(a, b) { return a.x - b.x || a.y - b.y || (a.next.y - a.y) / (a.next.x - a.x) - (b.next.y - b.y) / (b.next.x - b.x); } function eliminateHole(hole, outerNode) { var bridge = findHoleBridge(hole, outerNode); if (!bridge)
    return outerNode; var bridgeReverse = splitPolygon(bridge, hole), bridge2 = bridgeReverse.next; return indexSegment(bridge, bridge2.next), filterPoints(bridgeReverse, bridgeReverse.next), filterPoints(bridge, bridge.next); } var K = 16, blockBBox = new Float64Array(0), numBlocks = 0, blockHead = [], blockStop = []; function buildBlockIndex(maxNodes, numHoles) { var maxBlocks = Math.ceil((maxNodes + 2 * numHoles) / K) + numHoles + 2; blockBBox.length < maxBlocks * 4 && (blockBBox = new Float64Array(maxBlocks * 4)), numBlocks = 0; } function indexSegment(head, stop) { var p = head; do {
    var b = numBlocks++;
    blockHead[b] = p;
    var minX = p.x, minY = p.y, maxX = p.x, maxY = p.y, k = 0;
    do {
        var c = p.next;
        p.z = b, c.x < minX && (minX = c.x), c.x > maxX && (maxX = c.x), c.y < minY && (minY = c.y), c.y > maxY && (maxY = c.y), p = c;
    } while (++k < K && p !== stop);
    blockStop[b] = p;
    var g = b * 4;
    blockBBox[g] = minX, blockBBox[g + 1] = minY, blockBBox[g + 2] = maxX, blockBBox[g + 3] = maxY;
} while (p !== stop); } function growBlock(head, tail) { var g = head.z * 4; tail.x < blockBBox[g] && (blockBBox[g] = tail.x), tail.y < blockBBox[g + 1] && (blockBBox[g + 1] = tail.y), tail.x > blockBBox[g + 2] && (blockBBox[g + 2] = tail.x), tail.y > blockBBox[g + 3] && (blockBBox[g + 3] = tail.y); } function liveBlockStop(b) { var stop = blockStop[b]; for (; stop.prev.next !== stop;)
    stop = stop.next; return blockStop[b] = stop, stop; } function liveBlockHead(b) { var head = blockHead[b]; for (; head.prev.next !== head;)
    head = head.next; return blockHead[b] = head, head; } function findHoleBridge(hole, outerNode) { var p = outerNode, hx = hole.x, hy = hole.y, qx = -1 / 0, m; if (equals(hole, p))
    return p; for (var b = 0, g = 0; b < numBlocks; b++, g += 4) {
    if (hy < blockBBox[g + 1] || hy > blockBBox[g + 3] || blockBBox[g] > hx || blockBBox[g + 2] <= qx)
        continue;
    var stop = liveBlockStop(b);
    p = liveBlockHead(b);
    do {
        if (p.prev.next === p) {
            if (equals(hole, p.next))
                return p.next;
            if (hy <= p.y && hy >= p.next.y && p.next.y !== p.y) {
                var x_3 = p.x + (hy - p.y) * (p.next.x - p.x) / (p.next.y - p.y);
                if (x_3 <= hx && x_3 > qx && (qx = x_3, m = p.x < p.next.x ? p : p.next, x_3 === hx))
                    return m;
            }
        }
        p = p.next;
    } while (p !== stop);
} if (!m)
    return null; var mx = m.x, my = m.y, tminY = Math.min(hy, my), tmaxY = Math.max(hy, my), tanMin = 1 / 0; for (var b = 0, g = 0; b < numBlocks; b++, g += 4) {
    if (blockBBox[g + 2] < mx || blockBBox[g] > hx || blockBBox[g + 3] < tminY || blockBBox[g + 1] > tmaxY)
        continue;
    var stop = liveBlockStop(b);
    p = liveBlockHead(b);
    do {
        if (p.prev.next === p && hx >= p.x && p.x >= mx && hx !== p.x && pointInTriangle(hy < my ? hx : qx, hy, mx, my, hy < my ? qx : hx, hy, p.x, p.y)) {
            var tan = Math.abs(hy - p.y) / (hx - p.x);
            (locallyInside(p, hole) || p.y === hy && p.next.y === hy && p.next.x > hx) && (tan < tanMin || tan === tanMin && (p.x > m.x || p.x === m.x && sectorContainsSector(m, p))) && (m = p, tanMin = tan);
        }
        p = p.next;
    } while (p !== stop);
} return m; } function sectorContainsSector(m, p) { return area(m.prev, m, p.prev) < 0 && area(p.next, m, m.next) < 0; } var sortArr = [], sortBuf = [], zArr = new Uint32Array(0), zBuf = new Uint32Array(0), counts = new Uint32Array(256); function indexCurve(start, minX, minY, invSize) { var p = start, n = 0; do
    p.z = zOrder(p.x, p.y, minX, minY, invSize), sortArr[n++] = p, p = p.next;
while (p !== start); sortNodes(n); var prev = null; for (var i_18 = 0; i_18 < n; i_18++) {
    var node = sortArr[i_18];
    node.prevZ = prev, prev && (prev.nextZ = node), prev = node;
} prev.nextZ = null, sortArr.fill(null, 0, n), sortBuf.fill(null, 0, n); } function sortNodes(n) { if (n <= 32) {
    for (var i_19 = 1; i_19 < n; i_19++) {
        var node = sortArr[i_19], z = node.z, j = i_19 - 1;
        for (; j >= 0 && sortArr[j].z > z;)
            sortArr[j + 1] = sortArr[j], j--;
        sortArr[j + 1] = node;
    }
    return;
} zArr.length < n && (zArr = new Uint32Array(n), zBuf = new Uint32Array(n), sortBuf = new Array(n)); for (var i_20 = 0; i_20 < n; i_20++)
    zArr[i_20] = sortArr[i_20].z; radixPass(n, sortArr, zArr, sortBuf, zBuf, 0), radixPass(n, sortBuf, zBuf, sortArr, zArr, 8), radixPass(n, sortArr, zArr, sortBuf, zBuf, 16), radixPass(n, sortBuf, zBuf, sortArr, zArr, 24); } function radixPass(n, src, srcZ, dst, dstZ, shift) { counts.fill(0); for (var i_21 = 0; i_21 < n; i_21++)
    counts[srcZ[i_21] >>> shift & 255]++; var sum = 0; for (var b = 0; b < 256; b++) {
    var c = counts[b];
    counts[b] = sum, sum += c;
} for (var i_22 = 0; i_22 < n; i_22++) {
    var z = srcZ[i_22], pos = counts[z >>> shift & 255]++;
    dst[pos] = src[i_22], dstZ[pos] = z;
} } function zOrder(x, y, minX, minY, invSize) { return x = (x - minX) * invSize | 0, y = (y - minY) * invSize | 0, x = (x | x << 8) & 16711935, x = (x | x << 4) & 252645135, x = (x | x << 2) & 858993459, x = (x | x << 1) & 1431655765, y = (y | y << 8) & 16711935, y = (y | y << 4) & 252645135, y = (y | y << 2) & 858993459, y = (y | y << 1) & 1431655765, x | y << 1; } function getLeftmost(start) { var p = start, leftmost = start; do
    (p.x < leftmost.x || p.x === leftmost.x && p.y < leftmost.y) && (leftmost = p), p = p.next;
while (p !== start); return leftmost; } function pointInTriangle(ax, ay, bx, by, cx, cy, px, py) { return (cx - px) * (ay - py) >= (ax - px) * (cy - py) && (ax - px) * (by - py) >= (bx - px) * (ay - py) && (bx - px) * (cy - py) >= (cx - px) * (by - py); } function isValidDiagonal(a, b) { var zeroLength = equals(a, b) && area(a.prev, a, a.next) > 0 && area(b.prev, b, b.next) > 0; return a.next.i !== b.i && (zeroLength || locallyInside(a, b) && locallyInside(b, a) && (area(a.prev, a, b.prev) !== 0 || area(a, b.prev, b) !== 0)) && !intersectsPolygon(a, b) && (zeroLength || middleInside(a, b)); } function area(p, q, r) { return (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y); } function equals(p1, p2) { return p1.x === p2.x && p1.y === p2.y; } function intersects(p1, q1, p2, q2, includeBoundary) {
    if (includeBoundary === void 0) { includeBoundary = !0; }
    var o1 = area(p1, q1, p2), o2 = area(p1, q1, q2), o3 = area(p2, q2, p1), o4 = area(p2, q2, q1);
    return (o1 > 0 && o2 < 0 || o1 < 0 && o2 > 0) && (o3 > 0 && o4 < 0 || o3 < 0 && o4 > 0) ? !0 : includeBoundary ? !!(o1 === 0 && onSegment(p1, p2, q1) || o2 === 0 && onSegment(p1, q2, q1) || o3 === 0 && onSegment(p2, p1, q2) || o4 === 0 && onSegment(p2, q1, q2)) : !1;
} function onSegment(p, q, r) { return q.x <= Math.max(p.x, r.x) && q.x >= Math.min(p.x, r.x) && q.y <= Math.max(p.y, r.y) && q.y >= Math.min(p.y, r.y); } function intersectsPolygon(a, b) { var minX = Math.min(a.x, b.x), maxX = Math.max(a.x, b.x), minY = Math.min(a.y, b.y), maxY = Math.max(a.y, b.y), p = a; do {
    var n = p.next;
    if (p.x > maxX && n.x > maxX || p.x < minX && n.x < minX || p.y > maxY && n.y > maxY || p.y < minY && n.y < minY) {
        p = n;
        continue;
    }
    if (p.i !== a.i && n.i !== a.i && p.i !== b.i && n.i !== b.i && intersects(p, n, a, b))
        return !0;
    p = n;
} while (p !== a); return !1; } function locallyInside(a, b) { return area(a.prev, a, a.next) < 0 ? area(a, b, a.next) >= 0 && area(a, a.prev, b) >= 0 : area(a, b, a.prev) < 0 || area(a, a.next, b) < 0; } function middleInside(a, b) { var p = a, inside = !1, px = (a.x + b.x) / 2, py = (a.y + b.y) / 2; do {
    var n = p.next;
    p.y > py != n.y > py && px < (n.x - p.x) * (py - p.y) / (n.y - p.y) + p.x && (inside = !inside), p = n;
} while (p !== a); return inside; } function splitPolygon(a, b) { var a2 = createNode(a.i, a.x, a.y), b22 = createNode(b.i, b.x, b.y), an = a.next, bp = b.prev; return a.next = b, b.prev = a, a2.next = an, an.prev = a2, b22.next = a2, a2.prev = b22, bp.next = b22, b22.prev = bp, b22; } function insertNode(i, x, y, last) { var p = createNode(i, x, y); return last ? (p.next = last.next, p.prev = last, last.next.prev = p, last.next = p) : (p.prev = p, p.next = p), p; } function removeNode(p) { p.next.prev = p.prev, p.prev.next = p.next, p.prevZ && (p.prevZ.nextZ = p.nextZ), p.nextZ && (p.nextZ.prevZ = p.prevZ), indexActive && growBlock(p.prev, p.next); } function createNode(i, x, y) { return { i: i, x: x, y: y, prev: null, next: null, z: 0, prevZ: null, nextZ: null }; } function signedArea(data, start, end, dim) { var sum = 0; for (var i_23 = start, j = end - dim; i_23 < end; i_23 += dim)
    sum += (data[j] - data[i_23]) * (data[i_23 + 1] + data[j + 1]), j = i_23; return sum; } function triangulateFace3D(vertices3D, loops, normal) {
    var e_26, _j, e_27, _k, e_28, _l, e_29, _m, e_30, _o;
    if (loops.length === 0)
        return [];
    if (loops.length === 1 && loops[0].length === 3)
        return [loops[0]];
    if (loops.length === 1 && loops[0].length === 4) {
        var v = loops[0];
        return [[v[0], v[1], v[2]], [v[0], v[2], v[3]]];
    }
    var nx = normal[0], ny = normal[1], nz = normal[2], normVal = Math.sqrt(nx * nx + ny * ny + nz * nz);
    normVal > 1e-6 ? (nx /= normVal, ny /= normVal, nz /= normVal) : (nx = 0, ny = 0, nz = 1);
    var u_axis;
    Math.abs(nx) < .9 ? u_axis = [1, 0, 0] : u_axis = [0, 1, 0];
    var ux = ny * u_axis[2] - nz * u_axis[1], uy = nz * u_axis[0] - nx * u_axis[2], uz = nx * u_axis[1] - ny * u_axis[0], uLen = Math.sqrt(ux * ux + uy * uy + uz * uz);
    uLen < 1e-12 ? (ux = 1, uy = 0, uz = 0) : (ux /= uLen, uy /= uLen, uz /= uLen);
    var vx = ny * uz - nz * uy, vy = nz * ux - nx * uz, vz = nx * uy - ny * ux, vLen = Math.sqrt(vx * vx + vy * vy + vz * vz);
    vLen > 1e-12 && (vx /= vLen, vy /= vLen, vz /= vLen);
    var getVertex = function (id) { var pt; return typeof vertices3D.get == "function" ? pt = vertices3D.get(id) : pt = vertices3D[id], pt ? Array.isArray(pt) ? { x: pt[0], y: pt[1], z: pt[2] } : pt : null; }, loops2d = [];
    try {
        for (var loops_1 = __values(loops), loops_1_1 = loops_1.next(); !loops_1_1.done; loops_1_1 = loops_1.next()) {
            var loop = loops_1_1.value;
            var pts = [];
            try {
                for (var loop_2 = (e_27 = void 0, __values(loop)), loop_2_1 = loop_2.next(); !loop_2_1.done; loop_2_1 = loop_2.next()) {
                    var vId = loop_2_1.value;
                    var pt = getVertex(vId);
                    if (!pt)
                        return [];
                    pts.push({ u: pt.x * ux + pt.y * uy + pt.z * uz, v: pt.x * vx + pt.y * vy + pt.z * vz });
                }
            }
            catch (e_27_1) { e_27 = { error: e_27_1 }; }
            finally {
                try {
                    if (loop_2_1 && !loop_2_1.done && (_k = loop_2.return)) _k.call(loop_2);
                }
                finally { if (e_27) throw e_27.error; }
            }
            loops2d.push(pts);
        }
    }
    catch (e_26_1) { e_26 = { error: e_26_1 }; }
    finally {
        try {
            if (loops_1_1 && !loops_1_1.done && (_j = loops_1.return)) _j.call(loops_1);
        }
        finally { if (e_26) throw e_26.error; }
    }
    if (loops.length > 2 && holesOverlap(loops2d))
        return triangulateByFilteringHoles(loops, loops2d);
    var allVIds = [], holeIndices = [], currentOffset = 0;
    for (var l = 0; l < loops.length; l++) {
        l > 0 && holeIndices.push(currentOffset);
        var loop = loops[l];
        try {
            for (var loop_3 = (e_28 = void 0, __values(loop)), loop_3_1 = loop_3.next(); !loop_3_1.done; loop_3_1 = loop_3.next()) {
                var vId = loop_3_1.value;
                allVIds.push(vId);
            }
        }
        catch (e_28_1) { e_28 = { error: e_28_1 }; }
        finally {
            try {
                if (loop_3_1 && !loop_3_1.done && (_l = loop_3.return)) _l.call(loop_3);
            }
            finally { if (e_28) throw e_28.error; }
        }
        currentOffset += loop.length;
    }
    var flatCoords = [];
    try {
        for (var loops2d_1 = __values(loops2d), loops2d_1_1 = loops2d_1.next(); !loops2d_1_1.done; loops2d_1_1 = loops2d_1.next()) {
            var pts = loops2d_1_1.value;
            try {
                for (var pts_1 = (e_30 = void 0, __values(pts)), pts_1_1 = pts_1.next(); !pts_1_1.done; pts_1_1 = pts_1.next()) {
                    var _p = pts_1_1.value, u = _p.u, v = _p.v;
                    flatCoords.push(u, v);
                }
            }
            catch (e_30_1) { e_30 = { error: e_30_1 }; }
            finally {
                try {
                    if (pts_1_1 && !pts_1_1.done && (_o = pts_1.return)) _o.call(pts_1);
                }
                finally { if (e_30) throw e_30.error; }
            }
        }
    }
    catch (e_29_1) { e_29 = { error: e_29_1 }; }
    finally {
        try {
            if (loops2d_1_1 && !loops2d_1_1.done && (_m = loops2d_1.return)) _m.call(loops2d_1);
        }
        finally { if (e_29) throw e_29.error; }
    }
    var triIndices;
    try {
        triIndices = earcut(flatCoords, holeIndices, 2);
    }
    catch (e) {
        var outerLoop = loops[0], fallback = [];
        for (var i_24 = 1; i_24 < outerLoop.length - 1; i_24++)
            fallback.push([outerLoop[0], outerLoop[i_24], outerLoop[i_24 + 1]]);
        return fallback;
    }
    var result = [];
    for (var i_25 = 0; i_25 < triIndices.length; i_25 += 3) {
        var idx0 = triIndices[i_25], idx1 = triIndices[i_25 + 1], idx2 = triIndices[i_25 + 2];
        result.push([allVIds[idx0], allVIds[idx1], allVIds[idx2]]);
    }
    return result;
} function holesOverlap(loops2d) { for (var i_26 = 1; i_26 < loops2d.length; i_26++)
    for (var j = i_26 + 1; j < loops2d.length; j++)
        if (anyVertexInside(loops2d[i_26], loops2d[j]) || anyVertexInside(loops2d[j], loops2d[i_26]))
            return !0; return !1; } function anyVertexInside(points, polygon) {
    var e_31, _j;
    try {
        for (var points_1 = __values(points), points_1_1 = points_1.next(); !points_1_1.done; points_1_1 = points_1.next()) {
            var p = points_1_1.value;
            if (pointInPolygon(p.u, p.v, polygon))
                return !0;
        }
    }
    catch (e_31_1) { e_31 = { error: e_31_1 }; }
    finally {
        try {
            if (points_1_1 && !points_1_1.done && (_j = points_1.return)) _j.call(points_1);
        }
        finally { if (e_31) throw e_31.error; }
    }
    return !1;
} function pointInPolygon(u, v, polygon) { var inside = !1, n = polygon.length; for (var i_27 = 0, j = n - 1; i_27 < n; j = i_27++) {
    var ui = polygon[i_27].u, vi = polygon[i_27].v, uj = polygon[j].u, vj = polygon[j].v;
    vi > v != vj > v && u < (uj - ui) * (v - vi) / (vj - vi) + ui && (inside = !inside);
} return inside; } function triangulateByFilteringHoles(loops, loops2d) {
    var e_32, _j;
    var outerLoop = loops[0], outer2d = loops2d[0], flatOuter = [];
    try {
        for (var outer2d_1 = __values(outer2d), outer2d_1_1 = outer2d_1.next(); !outer2d_1_1.done; outer2d_1_1 = outer2d_1.next()) {
            var _k = outer2d_1_1.value, u = _k.u, v = _k.v;
            flatOuter.push(u, v);
        }
    }
    catch (e_32_1) { e_32 = { error: e_32_1 }; }
    finally {
        try {
            if (outer2d_1_1 && !outer2d_1_1.done && (_j = outer2d_1.return)) _j.call(outer2d_1);
        }
        finally { if (e_32) throw e_32.error; }
    }
    var triIndices;
    try {
        triIndices = earcut(flatOuter, [], 2);
    }
    catch (e) {
        var fallback = [];
        for (var i_28 = 1; i_28 < outerLoop.length - 1; i_28++)
            fallback.push([outerLoop[0], outerLoop[i_28], outerLoop[i_28 + 1]]);
        return fallback;
    }
    var result = [];
    for (var i_29 = 0; i_29 < triIndices.length; i_29 += 3) {
        var ia = triIndices[i_29], ib = triIndices[i_29 + 1], ic = triIndices[i_29 + 2], cu = (outer2d[ia].u + outer2d[ib].u + outer2d[ic].u) / 3, cv = (outer2d[ia].v + outer2d[ib].v + outer2d[ic].v) / 3, insideAnyHole = !1;
        for (var h = 1; h < loops2d.length; h++)
            if (pointInPolygon(cu, cv, loops2d[h])) {
                insideAnyHole = !0;
                break;
            }
        insideAnyHole || result.push([outerLoop[ia], outerLoop[ib], outerLoop[ic]]);
    }
    return result;
} function buildLocalFaceGroups(builder, ctx) {
    var e_33, _j, e_34, _k;
    var _a2, _b2, _c, _d, _e, _f;
    var faceGroups = new Map, addSide = function (triangles, fn, color, doubleSided, reverse, mat, uvTransform, xr, yr) {
        var e_35, _j, e_36, _k;
        var _a3;
        var texIndex = ctx.textureIndexFor(mat == null ? void 0 : mat.texture), transparency = (color.a !== void 0 ? color.a / 255 : 1) * ((_a3 = mat == null ? void 0 : mat.transparency) != null ? _a3 : 1), colorKey = "".concat(color.r, ",").concat(color.g, ",").concat(color.b, ",").concat(doubleSided, ",").concat(texIndex != null ? texIndex : -1, ",").concat(transparency), group = faceGroups.get(colorKey);
        group || (group = { color: color, transparency: transparency, doubleSided: doubleSided, textureIndex: texIndex, localVerts: [], localUvs: [], normalsAccum: [], localFaces: [], localVMap: new Map }, faceGroups.set(colorKey, group));
        var tex = mat == null ? void 0 : mat.texture, tileW = tex && tex.width > 1e-9 ? tex.width : 1, tileH = tex && tex.height > 1e-9 ? tex.height : 1, sideNormal = reverse ? [-fn[0], -fn[1], -fn[2]] : fn, faceLocalMap = new Map;
        try {
            for (var triangles_1 = __values(triangles), triangles_1_1 = triangles_1.next(); !triangles_1_1.done; triangles_1_1 = triangles_1.next()) {
                var tri = triangles_1_1.value;
                var triIds = reverse ? [tri[0], tri[2], tri[1]] : tri, faceIndices = [];
                try {
                    for (var triIds_1 = (e_36 = void 0, __values(triIds)), triIds_1_1 = triIds_1.next(); !triIds_1_1.done; triIds_1_1 = triIds_1.next()) {
                        var vId = triIds_1_1.value;
                        if (!builder.vertices.has(vId))
                            continue;
                        var idx = faceLocalMap.get(vId);
                        if (idx === void 0) {
                            var p = builder.vertices.get(vId), _l = __read(computeFaceUv(p, xr, yr, uvTransform, tileW, tileH), 2), u = _l[0], v = _l[1], key = "".concat(vId, ",").concat(u, ",").concat(v);
                            if (idx = group.localVMap.get(key), idx === void 0)
                                group.localVerts.push(p), group.localUvs.push([u, v]), group.normalsAccum.push([sideNormal[0], sideNormal[1], sideNormal[2]]), idx = group.localVerts.length - 1, group.localVMap.set(key, idx);
                            else {
                                var accum = group.normalsAccum[idx];
                                accum[0] += sideNormal[0], accum[1] += sideNormal[1], accum[2] += sideNormal[2];
                            }
                            faceLocalMap.set(vId, idx);
                        }
                        faceIndices.push(idx);
                    }
                }
                catch (e_36_1) { e_36 = { error: e_36_1 }; }
                finally {
                    try {
                        if (triIds_1_1 && !triIds_1_1.done && (_k = triIds_1.return)) _k.call(triIds_1);
                    }
                    finally { if (e_36) throw e_36.error; }
                }
                faceIndices.length === 3 && group.localFaces.push(faceIndices);
            }
        }
        catch (e_35_1) { e_35 = { error: e_35_1 }; }
        finally {
            try {
                if (triangles_1_1 && !triangles_1_1.done && (_j = triangles_1.return)) _j.call(triangles_1);
            }
            finally { if (e_35) throw e_35.error; }
        }
    };
    try {
        for (var _l = __values(builder.faces.entries()), _m = _l.next(); !_m.done; _m = _l.next()) {
            var _o = __read(_m.value, 2), _fId = _o[0], fData = _o[1];
            if (ctx.respectVisibility && fData.hidden)
                continue;
            var fallbackColor = (_b2 = (_a2 = ctx.inheritedMaterial) == null ? void 0 : _a2.color) != null ? _b2 : ctx.fallbackLayerColor, frontMat = (_c = ctx.resolveMaterial(fData.materialId)) != null ? _c : ctx.inheritedMaterial, backMat = (_d = ctx.resolveMaterial(fData.backMaterialId)) != null ? _d : ctx.inheritedMaterial, frontColor = (_e = frontMat == null ? void 0 : frontMat.color) != null ? _e : fallbackColor, backColor = (_f = backMat == null ? void 0 : backMat.color) != null ? _f : fallbackColor, loops = [];
            try {
                for (var _p = (e_34 = void 0, __values(fData.loops)), _q = _p.next(); !_q.done; _q = _p.next()) {
                    var loop = _q.value;
                    var loopVerts = reconstructLoopVertices(loop, builder.edges);
                    loopVerts.length > 0 && loops.push(loopVerts);
                }
            }
            catch (e_34_1) { e_34 = { error: e_34_1 }; }
            finally {
                try {
                    if (_q && !_q.done && (_k = _p.return)) _k.call(_p);
                }
                finally { if (e_34) throw e_34.error; }
            }
            if (loops.length === 0)
                continue;
            var triangles = void 0;
            try {
                triangles = triangulateFace3D(builder.vertices, loops, fData.normal);
            }
            catch (e) {
                throw new SkpParseError("Failed to triangulate face: ".concat(e.message), { stage: "build_scene", definitionId: ctx.definitionId, cause: e });
            }
            var fn = fData.normal, _r = faceUvBasis(fn), xr = _r.xr, yr = _r.yr, uvTransform = fData.uvTransform, uvTransformBack = fData.uvTransformBack;
            frontColor.r === backColor.r && frontColor.g === backColor.g && frontColor.b === backColor.b ? addSide(triangles, fn, frontColor, !0, !1, frontMat, uvTransform, xr, yr) : (addSide(triangles, fn, frontColor, !1, !1, frontMat, uvTransform, xr, yr), addSide(triangles, fn, backColor, !1, !0, backMat, uvTransformBack, xr, yr));
        }
    }
    catch (e_33_1) { e_33 = { error: e_33_1 }; }
    finally {
        try {
            if (_m && !_m.done && (_j = _l.return)) _j.call(_l);
        }
        finally { if (e_33) throw e_33.error; }
    }
    return faceGroups;
} function sniffImageMime(data) { return data.length >= 3 && data[0] === 255 && data[1] === 216 && data[2] === 255 ? "image/jpeg" : data.length >= 8 && data[0] === 137 && data[1] === 80 && data[2] === 78 && data[3] === 71 && data[4] === 13 && data[5] === 10 && data[6] === 26 && data[7] === 10 ? "image/png" : null; } function buildModelFromParsed(parsed) {
    var e_37, _j, e_38, _k;
    var version = parsed.version, units = parsed.units, layerColors = parsed.layerColors, layerHidden = parsed.layerHidden, layerIdToName = parsed.layerIdToName, pages = parsed.pages, dimensions = parsed.dimensions, materialIdToName = parsed.materialIdToName, materialsMap = parsed.materialsMap, materialsByFolder = parsed.materialsByFolder, styles = parsed.styles, defsDict = parsed.defsDict, materialsById = new Map;
    try {
        for (var _l = __values(materialIdToName.entries()), _m = _l.next(); !_m.done; _m = _l.next()) {
            var _o = __read(_m.value, 2), mId = _o[0], mName = _o[1];
            var mat = materialsMap.get(mName) || materialsByFolder.get(mName);
            mat && (mat.id === null && (mat.id = mId), materialsById.set(mId, mat));
        }
    }
    catch (e_37_1) { e_37 = { error: e_37_1 }; }
    finally {
        try {
            if (_m && !_m.done && (_j = _l.return)) _j.call(_l);
        }
        finally { if (e_37) throw e_37.error; }
    }
    var finalLayersList = Array.from(layerColors.entries()).map(function (_j) {
        var _k = __read(_j, 2), name = _k[0], c = _k[1];
        var _a2;
        return { name: name, color: { r: c[0], g: c[1], b: c[2] }, hidden: (_a2 = layerHidden.get(name)) != null ? _a2 : !1 };
    }), finalMaterialsList = Array.from(materialsMap.values()), finalPagesList = pages.map(function (pg) { return ({ name: pg.name, eye: pg.eye, target: pg.target, up: pg.up, fov: pg.fov, parallel: pg.parallel, orthoHeight: pg.orthoHeight, hiddenLayers: pg.hiddenLayerIds.map(function (id) { return layerIdToName.get(id); }).filter(function (name) { return name !== void 0; }) }); }), finalDimensionsList = dimensions.map(function (dm) { return ({ a: dm.a, b: dm.b, offset: dm.offset, planeX: dm.planeX, normal: dm.normal, text: dm.text, hidden: !1 }); }), finalDefinitions = new Map, rootDefinition = null;
    try {
        for (var _p = __values(defsDict.entries()), _q = _p.next(); !_q.done; _q = _p.next()) {
            var _r = __read(_q.value, 2), id = _r[0], d = _r[1];
            var defn = buildDefinition(typeof id == "number" ? id : 0, d, layerIdToName);
            typeof id == "number" ? finalDefinitions.set(id, defn) : rootDefinition = defn;
        }
    }
    catch (e_38_1) { e_38 = { error: e_38_1 }; }
    finally {
        try {
            if (_q && !_q.done && (_k = _p.return)) _k.call(_p);
        }
        finally { if (e_38) throw e_38.error; }
    }
    return { version: version, definitions: finalDefinitions, root: rootDefinition != null ? rootDefinition : { id: 0, guid: "ROOT", name: "ROOT_MODEL", vertices: [], edges: [], faces: [], instances: [], sectionPlanes: [], texts: [], dimensions: [], constructionLines: [], constructionPoints: [], isImage: !1, alwaysFacesCamera: !1, shadowsFaceSun: !1 }, layers: finalLayersList, pages: finalPagesList, dimensions: finalDimensionsList, materials: finalMaterialsList, materialsById: materialsById, styles: styles, units: units };
} function buildDefinition(id, d, layerIdToName) { var vertices = Array.from(d.builder.vertices.entries()).map(function (_j) {
    var _k = __read(_j, 2), vId = _k[0], _l = __read(_k[1], 3), x = _l[0], y = _l[1], z = _l[2];
    return ({ id: vId, x: x, y: y, z: z });
}), edges = Array.from(d.builder.edges.entries()).map(function (_j) {
    var _k = __read(_j, 2), eId = _k[0], _l = __read(_k[1], 2), v1 = _l[0], v2 = _l[1];
    var _a2;
    var flags = (_a2 = d.builder.edgeFlags.get(eId)) != null ? _a2 : 0;
    return { id: eId, v1Id: v1 != null ? v1 : 0, v2Id: v2 != null ? v2 : 0, soft: (flags & 8) !== 0, smooth: (flags & 16) !== 0, hidden: (flags & 1) !== 0 };
}), faces = Array.from(d.builder.faces.entries()).map(function (_j) {
    var _k = __read(_j, 2), fId = _k[0], fData = _k[1];
    var _a2, _b2, _c, _d, _e, _f, _g;
    return { id: fId, loops: fData.loops, normal: fData.normal, materialId: (_a2 = fData.materialId) != null ? _a2 : null, backMaterialId: (_b2 = fData.backMaterialId) != null ? _b2 : null, uvTransform: (_c = fData.uvTransform) != null ? _c : null, uvTransformBack: (_d = fData.uvTransformBack) != null ? _d : null, uvProjected: (_e = fData.uvProjected) != null ? _e : !1, uvProjectedBack: (_f = fData.uvProjectedBack) != null ? _f : !1, hidden: (_g = fData.hidden) != null ? _g : !1 };
}), instances = d.builder.instances.map(function (inst) { var _a2, _b2, _c; return { name: inst.name, refIdx: inst.refIdx, guid: inst.refGuid, matrix: inst.matrix, materialId: inst.materialId, hidden: (_a2 = inst.hidden) != null ? _a2 : !1, layer: (_b2 = inst.layerId != null ? layerIdToName == null ? void 0 : layerIdToName.get(inst.layerId) : void 0) != null ? _b2 : "", properties: (_c = inst.properties) != null ? _c : {} }; }), sectionPlanes = (d.builder.sectionPlanes || []).map(function (sp) { return ({ plane: sp.plane || [0, 0, 1, 0], name: sp.name || "", label: sp.label || "", hidden: sp.hidden || !1 }); }), texts = (d.builder.texts || []).map(function (txt) { return ({ text: txt.text || "", hidden: txt.hidden || !1 }); }), dimensions = (d.builder.dimensions || []).map(function (dim) { return ({ text: dim.text || "", hidden: dim.hidden || !1, a: null, b: null, offset: 0, planeX: null, normal: null }); }), constructionLines = (d.builder.constructionLines || []).map(function (cl) { return ({ point: cl.point, direction: cl.direction, start: cl.start, end: cl.end }); }), constructionPoints = (d.builder.constructionPoints || []).map(function (cp) { return ({ position: cp.position }); }); return { id: id, guid: d.guid, name: d.name, vertices: vertices, edges: edges, faces: faces, instances: instances, sectionPlanes: sectionPlanes, texts: texts, dimensions: dimensions, constructionLines: constructionLines, constructionPoints: constructionPoints, isImage: d.isImage, alwaysFacesCamera: d.alwaysFacesCamera, shadowsFaceSun: d.shadowsFaceSun || !1 }; } function invertMatrix3x3(m) { var _j = __read(m, 9), a = _j[0], b = _j[1], c = _j[2], d = _j[3], e = _j[4], f = _j[5], g = _j[6], h = _j[7], i = _j[8], det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g); if (Math.abs(det) < 1e-12)
    return [1, 0, 0, 0, 1, 0, 0, 0, 1]; var invDet = 1 / det; return [(e * i - f * h) * invDet, (c * h - b * i) * invDet, (b * f - c * e) * invDet, (f * g - d * i) * invDet, (a * i - c * g) * invDet, (c * d - a * f) * invDet, (d * h - e * g) * invDet, (b * g - a * h) * invDet, (a * e - b * d) * invDet]; } function faceUvBasis(n) { var _j = __read(n, 3), nx = _j[0], ny = _j[1], nz = _j[2], cx = -ny, cy = nx, clen = Math.sqrt(cx * cx + cy * cy), xr, yr; return clen < 1e-9 ? (xr = [1, 0, 0], yr = [0, nz >= 0 ? 1 : -1, 0]) : (xr = [cx / clen, cy / clen, 0], yr = [ny * xr[2] - nz * xr[1], nz * xr[0] - nx * xr[2], nx * xr[1] - ny * xr[0]]), { xr: xr, yr: yr }; } function computeFaceUv(p, xr, yr, uvTransform, tileW, tileH) { var px = p[0] * xr[0] + p[1] * xr[1] + p[2] * xr[2], py = p[0] * yr[0] + p[1] * yr[1] + p[2] * yr[2]; if (!uvTransform)
    return [px / tileW, py / tileH]; var inv = invertMatrix3x3(uvTransform), u = px * inv[0] + py * inv[3] + inv[6], v = px * inv[1] + py * inv[4] + inv[7], q = px * inv[2] + py * inv[5] + inv[8]; return Math.abs(q) < 1e-12 && (q = 1), [u / q / tileW, v / q / tileH]; } function buildSceneFromParsed(parsed, options) {
    var e_39, _j, e_40, _k;
    var t0 = Date.now(), layerColors = parsed.layerColors, layerIdToName = parsed.layerIdToName, materialIdToName = parsed.materialIdToName, materialsMap = parsed.materialsMap, materialsByFolder = parsed.materialsByFolder, defsDict = parsed.defsDict;
    emitLog(options, "info", "Building scene: ".concat(defsDict.size, " definitions available"));
    var instanceCounter = { count: 0 }, meshCounter = { count: 0 }, meshIndex = {}, glbPrimitives = [], pathUpdates = new Map, getLayerColor = function (name) { var c = layerColors.get(name) || [136, 136, 136]; return { r: c[0], g: c[1], b: c[2] }; }, textures = [], textureIndexByKey = new Map;
    function textureIndexFor(tex) { if (!tex || !tex.data || tex.data.length === 0)
        return null; var mimeType = sniffImageMime(tex.data); if (mimeType === null)
        return null; var head = Array.from(tex.data.subarray(0, 16)).join(","), key = "".concat(tex.data.length, ":").concat(head), hit = textureIndexByKey.get(key); if (hit !== void 0)
        return hit; var idx = textures.length; return textures.push({ data: tex.data, mimeType: mimeType, filename: tex.filename }), textureIndexByKey.set(key, idx), idx; }
    var colorToMaterialIndex = new Map, gltfMaterials = [], boundsMin = [1 / 0, 1 / 0, 1 / 0], boundsMax = [-1 / 0, -1 / 0, -1 / 0], activeDefinitions = new Set;
    function getMaterialIndex(color, doubleSided, textureIndex, transparency) {
        if (transparency === void 0) { transparency = 1; }
        var key = "".concat(color.r, ",").concat(color.g, ",").concat(color.b, ",").concat(doubleSided, ",").concat(textureIndex != null ? textureIndex : -1, ",").concat(transparency);
        if (colorToMaterialIndex.has(key))
            return colorToMaterialIndex.get(key);
        var idx = gltfMaterials.length, pbr = { baseColorFactor: [color.r / 255, color.g / 255, color.b / 255, transparency], metallicFactor: 0, roughnessFactor: .8 };
        textureIndex !== null && (pbr.baseColorTexture = { index: textureIndex });
        var material = { pbrMetallicRoughness: pbr };
        return doubleSided && (material.doubleSided = !0), transparency < 1 ? material.alphaMode = "BLEND" : textureIndex !== null && (material.alphaMode = "MASK"), gltfMaterials.push(material), colorToMaterialIndex.set(key, idx), idx;
    }
    function instantiate(defId, currentMatrix, parentLayer, pathName, inheritedMaterial) {
        var e_41, _j, e_42, _k, e_43, _l, e_44, _m;
        if (parentLayer === void 0) { parentLayer = "Layer0"; }
        if (pathName === void 0) { pathName = "ROOT"; }
        var _a2, _b2, _c, _d, _e, _f, _g, _h;
        var d = defsDict.get(defId);
        if (!d)
            return [];
        var builder = d.builder;
        if (builder.faces.size > 0) {
            var faceGroups = buildLocalFaceGroups(builder, { resolveMaterial: function (matId) { return resolveMaterialFromMaps(matId, materialIdToName, materialsMap, materialsByFolder); }, textureIndexFor: textureIndexFor, inheritedMaterial: inheritedMaterial, fallbackLayerColor: getLayerColor(parentLayer), definitionId: defId, respectVisibility: options == null ? void 0 : options.respectEdgeVisibility });
            try {
                for (var _o = __values(faceGroups.values()), _p = _o.next(); !_p.done; _p = _o.next()) {
                    var group = _p.value;
                    if (group.localFaces.length === 0)
                        continue;
                    var isRoot = pathName === "ROOT", tx = isRoot ? 0 : ((_a2 = currentMatrix[9]) != null ? _a2 : 0) * 25.4, ty = isRoot ? 0 : ((_b2 = currentMatrix[10]) != null ? _b2 : 0) * 25.4, tz = isRoot ? 0 : ((_c = currentMatrix[11]) != null ? _c : 0) * 25.4, safePath = pathName.replace(/ \/ /g, "__").replace(/ /g, "_");
                    safePath.length > 80 && (safePath = safePath.slice(0, 80));
                    var colorSuffix = faceGroups.size > 1 ? "_".concat(group.color.r, "_").concat(group.color.g, "_").concat(group.color.b, "_").concat(group.doubleSided ? "ds" : "ss") : "", geomName = "mesh_".concat(meshCounter.count, "_").concat(safePath, "_").concat(parentLayer).concat(colorSuffix);
                    meshCounter.count++, meshIndex[geomName] = { name: isRoot ? "ROOT" : pathName.split(" / ").pop() || "", definitionName: d.name || "", layer: parentLayer, positionMm: [Math.round(tx * 100) / 100, Math.round(ty * 100) / 100, Math.round(tz * 100) / 100], properties: {}, attributeDictionaries: {}, path: pathName };
                    var scale = .0254, positions = new Float32Array(group.localVerts.length * 3), normals = new Float32Array(group.localVerts.length * 3), uvs = new Float32Array(group.localVerts.length * 2), vertexNormalsAccum = group.normalsAccum;
                    for (var i_30 = 0; i_30 < group.localVerts.length; i_30++) {
                        var v = group.localVerts[i_30], pt = transformPoint(currentMatrix, v);
                        positions[i_30 * 3] = pt[0] * scale, positions[i_30 * 3 + 1] = pt[2] * scale, positions[i_30 * 3 + 2] = -pt[1] * scale;
                        var wx = positions[i_30 * 3], wy = positions[i_30 * 3 + 1], wz = positions[i_30 * 3 + 2];
                        wx < boundsMin[0] && (boundsMin[0] = wx), wy < boundsMin[1] && (boundsMin[1] = wy), wz < boundsMin[2] && (boundsMin[2] = wz), wx > boundsMax[0] && (boundsMax[0] = wx), wy > boundsMax[1] && (boundsMax[1] = wy), wz > boundsMax[2] && (boundsMax[2] = wz), uvs[i_30 * 2] = group.localUvs[i_30][0], uvs[i_30 * 2 + 1] = group.localUvs[i_30][1];
                        var rawNorm = vertexNormalsAccum[i_30], normLen = Math.sqrt(Math.pow(rawNorm[0], 2) + Math.pow(rawNorm[1], 2) + Math.pow(rawNorm[2], 2)), n = normLen > 1e-6 ? [rawNorm[0] / normLen, rawNorm[1] / normLen, rawNorm[2] / normLen] : [0, 0, 1], nx = currentMatrix[0] * n[0] + currentMatrix[1] * n[1] + currentMatrix[2] * n[2], ny = currentMatrix[3] * n[0] + currentMatrix[4] * n[1] + currentMatrix[5] * n[2], nz = currentMatrix[6] * n[0] + currentMatrix[7] * n[1] + currentMatrix[8] * n[2], l = Math.sqrt(nx * nx + ny * ny + nz * nz);
                        l > 1e-6 ? (normals[i_30 * 3] = nx / l, normals[i_30 * 3 + 1] = nz / l, normals[i_30 * 3 + 2] = -ny / l) : (normals[i_30 * 3] = 0, normals[i_30 * 3 + 1] = 1, normals[i_30 * 3 + 2] = 0);
                    }
                    var indices = new Uint32Array(group.localFaces.length * 3);
                    for (var i_31 = 0; i_31 < group.localFaces.length; i_31++)
                        indices[i_31 * 3] = group.localFaces[i_31][0], indices[i_31 * 3 + 1] = group.localFaces[i_31][1], indices[i_31 * 3 + 2] = group.localFaces[i_31][2];
                    var materialIndex = getMaterialIndex(group.color, group.doubleSided, group.textureIndex, group.transparency);
                    glbPrimitives.push({ positions: positions, normals: normals, uvs: uvs, indices: indices, materialIndex: materialIndex, geomName: geomName });
                }
            }
            catch (e_41_1) { e_41 = { error: e_41_1 }; }
            finally {
                try {
                    if (_p && !_p.done && (_j = _o.return)) _j.call(_o);
                }
                finally { if (e_41) throw e_41.error; }
            }
        }
        var childInstancesInfo = [];
        try {
            for (var _q = __values(builder.instances), _r = _q.next(); !_r.done; _r = _q.next()) {
                var inst = _r.value;
                var refIdx = inst.refIdx, instMatrix = inst.matrix, newMatrix = multiplyMatrices(currentMatrix, instMatrix), lName = parentLayer, instMaterial = inheritedMaterial, properties = __spreadValues({}, inst.properties || {});
                if (inst.layerId !== null && inst.layerId !== void 0 && (lName = layerIdToName.get(inst.layerId) || parentLayer), inst.materialId !== null && inst.materialId !== void 0) {
                    var matName = materialIdToName.get(inst.materialId);
                    if (matName) {
                        var mat = materialsMap.get(matName) || materialsByFolder.get(matName);
                        mat && (instMaterial = mat);
                    }
                }
                var d007 = inst.children.find(function (c) { return c.tag === "D007"; }), attributeDicts = null;
                if (d007)
                    try {
                        properties = extractDynamicProperties(d007, options), attributeDicts = extractAttributeDictionaries(d007, options);
                    }
                    catch (e) {
                        emitLog(options, "debug", "Failed to extract dynamic properties for instance ".concat((_d = inst.name) != null ? _d : "", " (refIdx=").concat(refIdx, "): ").concat(e.message));
                    }
                var instName = inst.name || "Component_".concat(refIdx), fullPathName = "".concat(pathName, " / ").concat(instName);
                if (instanceCounter.count++, instanceCounter.count % 500 === 0 && (emitProgress(options, "build_scene", instanceCounter.count, instanceCounter.count), emitLog(options, "debug", "Processed ".concat(instanceCounter.count, " placed instances"))), activeDefinitions.has(refIdx))
                    throw new SkpParseError("Recursive component definition", { stage: "build_scene", definitionId: refIdx });
                activeDefinitions.add(refIdx);
                var childNodes = instantiate(refIdx, newMatrix, lName, fullPathName, instMaterial);
                activeDefinitions.delete(refIdx);
                var tx = ((_e = newMatrix[9]) != null ? _e : 0) * 25.4, ty = ((_f = newMatrix[10]) != null ? _f : 0) * 25.4, tz = ((_g = newMatrix[11]) != null ? _g : 0) * 25.4, childDefName = ((_h = defsDict.get(refIdx)) == null ? void 0 : _h.name) || "", defNameIsReal = !!childDefName && !isGenericDefinitionName(childDefName), nameOverride = findNameOverride(attributeDicts), instNameNonEmpty = !!inst.name, fallbackName = instNameNonEmpty ? inst.name : defNameIsReal ? childDefName : "Component_".concat(refIdx), displayName = nameOverride != null ? nameOverride : fallbackName, nameIsGenerated = nameOverride === null && !instNameNonEmpty && !defNameIsReal, attributeDictionaries = {};
                if (attributeDicts)
                    try {
                        for (var _s = (e_43 = void 0, __values(Object.keys(attributeDicts))), _t = _s.next(); !_t.done; _t = _s.next()) {
                            var dictName = _t.value;
                            if (dictName === "dynamic_attributes" || dictName === "SU_InstanceSet")
                                continue;
                            var entries = attributeDicts[dictName], stringified = {};
                            try {
                                for (var _u = (e_44 = void 0, __values(Object.keys(entries))), _v = _u.next(); !_v.done; _v = _u.next()) {
                                    var key = _v.value;
                                    stringified[key] = stringifyVffAttrValue(entries[key]);
                                }
                            }
                            catch (e_44_1) { e_44 = { error: e_44_1 }; }
                            finally {
                                try {
                                    if (_v && !_v.done && (_m = _u.return)) _m.call(_u);
                                }
                                finally { if (e_44) throw e_44.error; }
                            }
                            attributeDictionaries[dictName] = stringified;
                        }
                    }
                    catch (e_43_1) { e_43 = { error: e_43_1 }; }
                    finally {
                        try {
                            if (_t && !_t.done && (_l = _s.return)) _l.call(_s);
                        }
                        finally { if (e_43) throw e_43.error; }
                    }
                var instInfo = { name: displayName, nameIsGenerated: nameIsGenerated, definitionName: childDefName, layer: lName, positionMm: [Math.round(tx * 100) / 100, Math.round(ty * 100) / 100, Math.round(tz * 100) / 100], properties: properties, attributeDictionaries: attributeDictionaries, guid: inst.refGuid || "", children: childNodes };
                childInstancesInfo.push(instInfo), pathUpdates.set(fullPathName, { properties: properties, name: inst.name || "", attributeDictionaries: attributeDictionaries });
            }
        }
        catch (e_42_1) { e_42 = { error: e_42_1 }; }
        finally {
            try {
                if (_r && !_r.done && (_k = _q.return)) _k.call(_q);
            }
            finally { if (e_42) throw e_42.error; }
        }
        return childInstancesInfo;
    }
    var rootChildren = instantiate("ROOT", [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]);
    try {
        for (var _l = __values(Object.keys(meshIndex)), _m = _l.next(); !_m.done; _m = _l.next()) {
            var geomName = _m.value;
            var existing = meshIndex[geomName], update = existing ? pathUpdates.get(existing.path) : void 0;
            existing && update && (existing.properties = update.properties, existing.name = update.name, existing.attributeDictionaries = update.attributeDictionaries);
        }
    }
    catch (e_39_1) { e_39 = { error: e_39_1 }; }
    finally {
        try {
            if (_m && !_m.done && (_j = _l.return)) _j.call(_l);
        }
        finally { if (e_39) throw e_39.error; }
    }
    try {
        for (var _o = __values(Object.keys(meshIndex)), _p = _o.next(); !_p.done; _p = _o.next()) {
            var geomName = _p.value;
            var existing = meshIndex[geomName];
            existing && existing.path === "ROOT" && (existing.name = "ROOT", existing.definitionName = "ROOT_MODEL", existing.layer = "Layer0", existing.positionMm = [0, 0, 0], existing.properties = {}, existing.attributeDictionaries = {});
        }
    }
    catch (e_40_1) { e_40 = { error: e_40_1 }; }
    finally {
        try {
            if (_p && !_p.done && (_k = _o.return)) _k.call(_o);
        }
        finally { if (e_40) throw e_40.error; }
    }
    var sceneHierarchy = { name: "ROOT", nameIsGenerated: !1, definitionName: "ROOT_MODEL", layer: "Layer0", positionMm: [0, 0, 0], properties: {}, attributeDictionaries: {}, guid: "", children: rootChildren };
    emitLog(options, "info", "Scene build complete: ".concat(instanceCounter.count, " instances, ").concat(Object.keys(meshIndex).length, " meshes, ").concat(glbPrimitives.length, " primitives (").concat(((Date.now() - t0) / 1e3).toFixed(2), "s)"));
    var bounds = Number.isFinite(boundsMin[0]) ? { min: [boundsMin[0], boundsMin[1], boundsMin[2]], max: [boundsMax[0], boundsMax[1], boundsMax[2]], size: [boundsMax[0] - boundsMin[0], boundsMax[1] - boundsMin[1], boundsMax[2] - boundsMin[2]], center: [(boundsMin[0] + boundsMax[0]) / 2, (boundsMin[1] + boundsMax[1]) / 2, (boundsMin[2] + boundsMax[2]) / 2] } : null;
    return { sceneHierarchy: sceneHierarchy, meshIndex: meshIndex, glbPrimitives: glbPrimitives, gltfMaterials: gltfMaterials, textures: textures, bounds: bounds };
} function resolveMaterialFromMaps(matId, materialIdToName, materialsMap, materialsByFolder) { if (matId == null)
    return; var matName = materialIdToName.get(matId); if (matName)
    return materialsMap.get(matName) || materialsByFolder.get(matName); } var LegacyParseError = (function (_super) {
    __extends(LegacyParseError, _super);
    function LegacyParseError() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return LegacyParseError;
}(Error)), STR_MARKER = new Uint8Array([255, 254, 255]), MAX_V20_FILLER_PAD = 29; function bytesEqual(a, b) { if (a.length !== b.length)
    return !1; for (var i_32 = 0; i_32 < a.length; i_32++)
    if (a[i_32] !== b[i_32])
        return !1; return !0; } function findCountAfterV20Filler(data, countPos, limit, ar) { var markerAt = -1; for (var i_33 = countPos; i_33 < countPos + 12 && i_33 + 4 <= data.length; i_33++)
    if (data[i_33] === 255 && data[i_33 + 1] === 254 && data[i_33 + 2] === 255) {
        markerAt = i_33;
        break;
    } if (markerAt < 0 || data[markerAt + 3] !== 0)
    return null; var view = new DataView(data.buffer, data.byteOffset, data.byteLength); for (var pad = 1; pad <= MAX_V20_FILLER_PAD; pad += 4) {
    var at = markerAt + 4 + pad;
    if (at + 4 > data.length)
        break;
    var count = view.getUint32(at, !0);
    if (count > 0 && count <= limit && (ar === void 0 || plausibleListTag(ar, data, at + 4)))
        return { count: count, next: at + 4 };
} return null; } function retryCountAfterV20Filler(r, countPos, limit, ar) { var hit = findCountAfterV20Filler(r.data, countPos, limit, ar); return hit === null ? null : (r.pos = hit.next, hit.count); } function plausibleListTag(ar, data, at) { if (at + 2 > data.length)
    return !1; var t = new DataView(data.buffer, data.byteOffset, data.byteLength).getUint16(at, !0); if (t === 0 || t === 32767 || t === 65535)
    return !0; if (t & 32768) {
    var ent = ar.slots.get(t & 32767);
    return ent !== void 0 && ent[0] === "class";
} return t < ar.nextSlot; } function findBytes(data, needle, start, end) {
    if (start === void 0) { start = 0; }
    if (end === void 0) { end = data.length; }
    var nlen = needle.length, limit = end - nlen;
    outer: for (var i_34 = start; i_34 <= limit; i_34++) {
        for (var j = 0; j < nlen; j++)
            if (data[i_34 + j] !== needle[j])
                continue outer;
        return i_34;
    }
    return -1;
} function findPattern(data, pattern, start, end) {
    if (start === void 0) { start = 0; }
    if (end === void 0) { end = data.length; }
    var patLen = pattern.length, limit = end - patLen;
    outer: for (var i_35 = start; i_35 <= limit; i_35++) {
        for (var j = 0; j < patLen; j++) {
            var want = pattern[j];
            if (want !== null && data[i_35 + j] !== want)
                continue outer;
        }
        return i_35;
    }
    return -1;
} function asciiBytes(s) { return s.split("").map(function (c) { return c.charCodeAt(0); }); } function matchesAscii(data, offset, str) { if (offset + str.length > data.length)
    return !1; for (var i_36 = 0; i_36 < str.length; i_36++)
    if (data[offset + i_36] !== str.charCodeAt(i_36))
        return !1; return !0; } function toHex(data) { var s = ""; for (var i_37 = 0; i_37 < data.length; i_37++) {
    var h = data[i_37].toString(16).toUpperCase();
    s += h.length === 1 ? "0" + h : h;
} return s; } function isClassRef(data, p, slot) { var view = new DataView(data.buffer, data.byteOffset, data.byteLength); return slot <= 32767 ? p + 2 <= data.length && view.getUint16(p, !0) === (32768 | slot) : p + 6 <= data.length && view.getUint16(p, !0) === 32767 && view.getUint32(p + 2, !0) === (2147483648 | slot) >>> 0; } var R = (function () {
    function R(data, pos) {
        if (pos === void 0) { pos = 0; }
        this.data = data, this.pos = pos, this.view = new DataView(data.buffer, data.byteOffset, data.byteLength);
    }
    R.prototype.u8 = function () { var v = this.data[this.pos]; return this.pos += 1, v; };
    R.prototype.u16 = function () { var v = this.view.getUint16(this.pos, !0); return this.pos += 2, v; };
    R.prototype.u32 = function () { var v = this.view.getUint32(this.pos, !0); return this.pos += 4, v; };
    R.prototype.i32 = function () { var v = this.view.getInt32(this.pos, !0); return this.pos += 4, v; };
    R.prototype.f64 = function () { var v = this.view.getFloat64(this.pos, !0); return this.pos += 8, v; };
    R.prototype.f64s = function (n) { var out = []; for (var i_38 = 0; i_38 < n; i_38++)
        out.push(this.f64()); return out; };
    R.prototype.raw = function (n) { var v = this.data.subarray(this.pos, this.pos + n); return this.pos += n, v; };
    R.prototype.peek = function (n) { return this.data.subarray(this.pos, this.pos + n); };
    R.prototype.peekU16 = function () { return this.view.getUint16(this.pos, !0); };
    R.prototype.utf16 = function () { if (!bytesEqual(this.peek(3), STR_MARKER))
        throw new LegacyParseError("expected a string record ".concat(this.ctx())); this.pos += 3; var n = this.u8(); n === 255 && (n = this.u16(), n === 65535 && (n = this.u32())); var bytes = this.raw(2 * n); return new TextDecoder("utf-16le").decode(bytes); };
    R.prototype.ctx = function (back, fwd) {
        if (back === void 0) { back = 16; }
        if (fwd === void 0) { fwd = 32; }
        var p = this.pos, before = toHex(this.data.subarray(Math.max(0, p - back), p)), after = toHex(this.data.subarray(p, p + fwd));
        return "@0x".concat(p.toString(16), ": ...").concat(before, " | ").concat(after, "...");
    };
    return R;
}()), Archive = (function () {
    function Archive(data, ver) {
        this.slots = new Map;
        this.classSlot = new Map;
        this.classSchema = new Map;
        this.currentClass = null;
        this.currentObjSlot = null;
        this.nextSlot = 0;
        this.walkBase = 0;
        this.readers = {};
        this.currentLoop = null;
        this.inEntityList = !1;
        this.burns = [];
        this.cumDelta = 0;
        this.annotWatermark = null;
        this.burnStack = [];
        this.onDefinitionDone = null;
        this.prebuilt = new Map;
        this.releasedSpans = [];
        this.clineTail = null;
        this.data = data, this.ver = ver, this.hasPid = ver >= 17, this.r = new R(data);
    }
    Archive.prototype.alloc = function (entry) { var s = this.nextSlot; return this.slots.set(s, entry), this.nextSlot += 1, s; };
    Archive.prototype.readObject = function (r, expect) {
        if (expect === void 0) { expect = null; }
        var tag = r.u16();
        if (tag === 0)
            return [null, null, null];
        if (tag === 32767) {
            var big = r.u32();
            return big & 2147483648 ? this.newOfClass(r, big & 2147483647, expect) : this.backref(big, r);
        }
        if (tag === 65535) {
            var schema = r.u16(), namelen = r.u16();
            if (namelen > 40)
                throw new LegacyParseError("implausible class name length ".concat(r.ctx()));
            var nameBytes = r.raw(namelen), name = new TextDecoder("utf-8").decode(nameBytes);
            return this.alloc(["class", name, schema]), this.classSlot.set(name, this.nextSlot - 1), this.classSchema.set(name, schema), this.newObj(r, name);
        }
        return tag & 32768 ? this.newOfClass(r, tag & 32767, expect) : this.backref(tag, r);
    };
    Archive.prototype.newOfClass = function (r, cslot, expect) { var ent = this.slots.get(cslot); if (ent === void 0) {
        if (expect === null)
            throw new LegacyParseError("class-ref to unknown slot ".concat(cslot, " ").concat(r.ctx()));
        var newEnt = ["class", expect, null];
        this.slots.set(cslot, newEnt), this.classSlot.set(expect, cslot), ent = newEnt;
    } if (ent[0] !== "class")
        throw new LegacyParseError("class-ref to non-class slot ".concat(cslot, " (").concat(ent[1], ") ").concat(r.ctx())); return this.newObj(r, ent[1]); };
    Archive.prototype.newObj = function (r, name) { this.inEntityList = !1; var slot = this.alloc(["obj", name, null]), reader = this.readers[name]; if (reader === void 0)
        throw new LegacyParseError("no reader for class ".concat(name, " ").concat(r.ctx())); var prevClass = this.currentClass, prevSlot = this.currentObjSlot; this.currentClass = name, this.currentObjSlot = slot; var value; try {
        value = reader(this, r);
    }
    finally {
        this.currentClass = prevClass, this.currentObjSlot = prevSlot;
    } return this.slots.set(slot, ["obj", name, value]), name === "CComponentDefinition" && value && this.onDefinitionDone && this.onDefinitionDone(slot, value), (name === "CDimensionLinear" || name === "CText") && (this.annotWatermark = this.nextSlot), [slot, name, value]; };
    Archive.prototype.clayerRecordAt = function (at, unmatchedClassRef) {
        if (unmatchedClassRef === void 0) { unmatchedClassRef = !1; }
        if (at + 2 > this.data.length)
            return !1;
        var tag = this.data[at] | this.data[at + 1] << 8;
        if (tag === 65535 && at + 12 <= this.data.length && (this.data[at + 4] | this.data[at + 5] << 8) === 6 && matchesAscii(this.data, at + 6, "CLayer"))
            return !0;
        var layCs = this.classSlot.get("CLayer");
        return layCs !== void 0 && isClassRef(this.data, at, layCs) ? !0 : unmatchedClassRef && (tag & 32768) !== 0 && tag !== 65535;
    };
    Archive.prototype.skipClayerColourExt = function () { if (!(this.r.pos + 16 + 2 > this.data.length)) {
        for (var i_39 = 0; i_39 < 12; i_39++)
            if (this.data[this.r.pos + i_39] !== 0)
                return;
        this.clayerRecordAt(this.r.pos + 16, !0) && (this.r.pos += 16);
    } };
    Archive.prototype.skipClayerParentRef = function (selfSlot) { if (this.r.pos + 4 > this.data.length || selfSlot === null)
        return; var a = this.data[this.r.pos] | this.data[this.r.pos + 1] << 8, b = this.data[this.r.pos + 2] | this.data[this.r.pos + 3] << 8; if (!a || a & 32768 || a === 32767 || a === selfSlot || !b || b & 32768 || b === 32767)
        return; var ea = this.slots.get(a), eb = this.slots.get(b); ea === void 0 || eb === void 0 || ea[0] === "class" || eb[0] === "class" || ea[1] !== "CLayer" || eb[1] !== "CLayer" || (this.r.pos += 2); };
    Archive.prototype.collectTrailingLayers = function (slotsOut, layersOut, unmatchedClassRef) {
        if (unmatchedClassRef === void 0) { unmatchedClassRef = !1; }
        for (; this.r.pos + 2 <= this.data.length;) {
            if (this.r.peekU16() === 0) {
                this.r.pos += 2;
                continue;
            }
            if (!this.clayerRecordAt(this.r.pos, unmatchedClassRef))
                break;
            var _j = __read(this.readObject(this.r, "CLayer"), 3), s = _j[0], v = _j[2];
            v != null && (slotsOut && slotsOut.push(s), layersOut && layersOut.push([s, v]));
        }
    };
    Archive.prototype.translateRef = function (slot) {
        var e_45, _j;
        var offset = 0;
        try {
            for (var _k = __values(this.burns), _l = _k.next(); !_l.done; _l = _k.next()) {
                var _m = __read(_l.value, 2), start = _m[0], width = _m[1];
                if (slot < start)
                    break;
                if (slot < start + width)
                    return null;
                offset += width;
            }
        }
        catch (e_45_1) { e_45 = { error: e_45_1 }; }
        finally {
            try {
                if (_l && !_l.done && (_j = _k.return)) _j.call(_k);
            }
            finally { if (e_45) throw e_45.error; }
        }
        return slot - offset;
    };
    Archive.prototype.backref = function (slot, r) { if (this.burns.length > 0 && slot >= this.burns[0][0]) {
        var walker = this.translateRef(slot);
        if (walker === null)
            return [slot, "reserved", null];
        slot = walker;
    } var ent = this.slots.get(slot); if (ent === void 0) {
        if (slot < this.walkBase)
            return [slot, "premodel", null];
        throw new LegacyParseError("back-ref to unwalked slot ".concat(slot, " ").concat(r.ctx()));
    } if (ent[0] === "class")
        throw new LegacyParseError("back-ref to class slot ".concat(slot, " ").concat(r.ctx())); return [slot, ent[1], ent[2]]; };
    return Archive;
}()); function preamble(ar, r) { var _j = __read(ar.readObject(r, "CAttributeContainer"), 3), attrsSlot = _j[0], attrs = _j[2], pid = 0; if (ar.hasPid) {
    var mask = r.u8();
    for (var bit = 0; bit < 8; bit++)
        mask & 1 << bit && (pid |= r.u8() << 8 * bit);
} return { attrs: attrs, pid: pid, attrsSlot: attrsSlot }; } var FIRST_V4 = 4; function earlyPreamble(ar, r) { return ar.ver < FIRST_V4 ? { attrs: null, pid: 0, attrsSlot: null } : preamble(ar, r); } function drawbase(ar, r) { var b = ar.ver < FIRST_V4 ? r.raw(5) : r.raw(8), view = new DataView(b.buffer, b.byteOffset, b.byteLength), layCls = ar.classSlot.get("CLayer"), tag = r.peekU16(), layer; if (layCls !== void 0 && tag === (32768 | layCls))
    ar.readObject(r, "CLayer"), layer = 0;
else if (tag === 32767) {
    if (r.u16(), r.u32() & 2147483648)
        throw new LegacyParseError("drawbase layer: unexpected class ".concat(r.ctx()));
    layer = 0;
}
else
    layer = r.u16(); return ar.ver < FIRST_V4 ? { mat: 0, hidden: 0, soft: 0, smooth: 0, layer: layer } : { mat: view.getUint16(0, !0), hidden: b[2], soft: b[5], smooth: b[6], layer: layer }; } function readVertex(ar, r) { return earlyPreamble(ar, r), { k: "vertex", xyz: r.f64s(3) }; } function readEdge(ar, r) { preamble(ar, r); var db = drawbase(ar, r), _j = __read(ar.readObject(r, "CVertex"), 1), s1 = _j[0], _k = __read(ar.readObject(r, "CVertex"), 1), s2 = _k[0], _l = __read(ar.readObject(r), 2), cs = _l[0], cn = _l[1]; if (cn !== null && cn !== "CCurve" && cn !== "CArcCurve")
    throw new LegacyParseError("edge curve pointer resolved to ".concat(cn, " ").concat(r.ctx())); return { k: "edge", db: db, curve: cs, v1: s1, v2: s2 }; } function readCurve(ar, r) { return preamble(ar, r), r.u8(), { k: "curve", n: r.u32() }; } function readArcCurve(ar, r) { return preamble(ar, r), r.raw(5), r.f64s(14), { k: "arccurve" }; } function registerBurn(ar, delta) { ar.burns.push([ar.annotWatermark + ar.cumDelta, delta]), ar.cumDelta += delta, ar.annotWatermark = null, ar.burnStack.length > 0 && (ar.burnStack[ar.burnStack.length - 1] += 1); } function readEdgeUse(ar, r) { earlyPreamble(ar, r); var _j = __read(ar.readObject(r, "CEdge"), 1), es = _j[0], sense = r.u8(), p0 = r.pos, tag = r.u16(), ps; if (tag === 32767) {
    var big = r.u32();
    if (big & 2147483648)
        throw new LegacyParseError("edge-use parent is a new object ".concat(r.ctx()));
    ps = big;
}
else {
    if (tag === 65535 || tag & 32768)
        throw new LegacyParseError("edge-use parent is a new object ".concat(r.ctx()));
    ps = tag !== 0 ? tag : null;
} var expected = ar.currentLoop !== null ? ar.currentLoop + ar.cumDelta : null; if (ps !== expected) {
    var delta = typeof ps == "number" && expected !== null ? ps - expected : 0;
    if (delta > 0 && delta <= 4096 && ar.annotWatermark !== null)
        registerBurn(ar, delta);
    else
        throw r.pos = p0, new LegacyParseError("edge-use parent slot ".concat(ps, " != current loop ").concat(expected, " ").concat(r.ctx()));
} return { k: "edgeuse", edge: es, sense: sense }; } function readLoop(ar, r) { var mySlot = ar.nextSlot - 1, prev = ar.currentLoop; ar.currentLoop = mySlot, earlyPreamble(ar, r), r.raw(2); var uses = []; for (;;) {
    if (r.peekU16() === 0) {
        r.pos += 2;
        break;
    }
    var _j = __read(ar.readObject(r, "CEdgeUse"), 3), v = _j[2];
    uses.push(v);
} return ar.currentLoop = prev, { k: "loop", uses: uses }; } function readFace(ar, r) { var pre = preamble(ar, r), db = drawbase(ar, r), attrs = pre.attrs; ar.ver < FIRST_V4 && attrs && typeof attrs == "object" && attrs.k === "material" && (db.mat = pre.attrsSlot, attrs = null); var plane = r.f64s(4), nloops = r.u32(); if (nloops > 1e4)
    throw new LegacyParseError("implausible loop count ".concat(nloops, " ").concat(r.ctx())); var loops = []; for (var i_40 = 0; i_40 < nloops; i_40++) {
    var _j = __read(ar.readObject(r, "CLoop"), 3), v = _j[2];
    loops.push(v);
} var backMat = r.u16(); return { k: "face", db: db, plane: plane, loops: loops, back_mat: backMat, attrs: attrs }; } function readAttrContainer(ar, r) { preamble(ar, r); var children = []; for (;;) {
    if (r.peekU16() === 0) {
        r.pos += 2;
        break;
    }
    var _j = __read(ar.readObject(r, "CAttributeNamed"), 3), n = _j[1], v = _j[2];
    children.push([n, v]);
} return { k: "attrs", children: children }; } function readAttrNamed(ar, r) { preamble(ar, r), r.raw(4); var dictname = r.utf16(); function readTyped(t) { if (t === 0)
    return null; if (t === 4)
    return r.i32(); if (t === 6)
    return r.f64(); if (t === 7)
    return r.u8(); if (t === 9)
    return r.u32(); if (t === 10)
    return r.utf16(); if (t === 12)
    return r.f64(); if (t === 11) {
    var n = r.u32();
    if (n > 1e5)
        throw new LegacyParseError("implausible attr array count ".concat(r.ctx()));
    var arr = [];
    for (var i_41 = 0; i_41 < n; i_41++)
        arr.push(readTyped(r.u8()));
    return arr;
} if (t === 17 || t === 18)
    return r.f64s(3); throw new LegacyParseError("unknown attribute value type 0x".concat(t.toString(16), " ").concat(r.ctx())); } var entries = {}; for (;;) {
    var key = r.utf16();
    if (key === "")
        break;
    entries[key] = readTyped(r.u8());
} return ar.ver >= 7 && r.u32(), { k: "dict", name: dictname, entries: entries }; } var DYNAMIC_ATTRIBUTES_DICT_NAME = "dynamic_attributes"; function stringifyAttrValue(value) { return value == null ? "" : Array.isArray(value) ? value.map(stringifyAttrValue).join(",") : String(value); } function extractLegacyDynamicProperties(attrs) {
    var e_46, _j, e_47, _k;
    if (!attrs || typeof attrs != "object")
        return {};
    try {
        for (var _l = __values(attrs.children || []), _m = _l.next(); !_m.done; _m = _l.next()) {
            var _o = __read(_m.value, 2), value = _o[1];
            if (value && typeof value == "object" && value.name === DYNAMIC_ATTRIBUTES_DICT_NAME) {
                var entries = value.entries || {}, properties = {};
                try {
                    for (var _p = (e_47 = void 0, __values(Object.keys(entries))), _q = _p.next(); !_q.done; _q = _p.next()) {
                        var key = _q.value;
                        properties[key] = stringifyAttrValue(entries[key]);
                    }
                }
                catch (e_47_1) { e_47 = { error: e_47_1 }; }
                finally {
                    try {
                        if (_q && !_q.done && (_k = _p.return)) _k.call(_p);
                    }
                    finally { if (e_47) throw e_47.error; }
                }
                return properties;
            }
        }
    }
    catch (e_46_1) { e_46 = { error: e_46_1 }; }
    finally {
        try {
            if (_m && !_m.done && (_j = _l.return)) _j.call(_l);
        }
        finally { if (e_46) throw e_46.error; }
    }
    return {};
} function readLayer(ar, r) { earlyPreamble(ar, r); var name = r.utf16(), mid = []; for (; mid.length < 8 && !bytesEqual(r.peek(3), STR_MARKER);)
    mid.push(r.raw(1)[0]); if (r.utf16(), r.u16() & 255) {
    var tex = textureBlock(ar, r);
    return r.raw(4), { k: "layer", name: name, hidden: mid.length ? mid[0] : 0, rgba: tex.rgba };
} var rgba = r.raw(4); return r.utf16(), r.raw(ar.ver < FIRST_V4 ? 17 : 21), ar.skipClayerColourExt(), ar.skipClayerParentRef(ar.currentObjSlot), { k: "layer", name: name, hidden: mid.length ? mid[0] : 0, rgba: Array.from(rgba) }; } function textureBlock(ar, r) {
    var _j;
    var s, dib;
    if (ar.ver < FIRST_V4)
        s = null, dib = readDib(ar, r);
    else if (r.pos -= 1, preamble(ar, r), _j = __read(ar.readObject(r, "CDib"), 3), s = _j[0], dib = _j[2], !(dib && typeof dib == "object" && dib.k === "dib"))
        throw new LegacyParseError("texture object is not a dib ".concat(r.ctx()));
    var marker = findBytes(r.data, STR_MARKER, r.pos, r.pos + 28);
    if (marker - r.pos === 20)
        r.u32();
    else if (marker - r.pos !== 16)
        throw new LegacyParseError("texture size block misaligned ".concat(r.ctx()));
    var w = r.f64(), h = r.f64(), fname = r.utf16(), avg = r.raw(9);
    r.utf16();
    var blob = r.raw(8), opacity = r.f64(), useOp = r.u8(), colorized = !!blob[4] || avg[3] === 255;
    return { rgba: Array.from(avg.subarray(0, 4)), opacity: opacity, use_opacity: useOp, tex_dib: s, tex_data: s === null ? dib.data : null, tex_w: w, tex_h: h, tex_file: fname, colorized: colorized };
} function readMaterial(ar, r) { earlyPreamble(ar, r); var name = r.utf16(), texflag = r.u16(), out = { k: "material", name: name }; if (texflag === 0) {
    var rgba = r.raw(4);
    r.utf16(), r.raw(8);
    var opacity = r.f64(), useOp = r.u8();
    out.rgba = Array.from(rgba), out.opacity = opacity, out.use_opacity = useOp;
}
else {
    var tex = textureBlock(ar, r);
    out.rgba = tex.rgba, out.opacity = tex.opacity, out.use_opacity = tex.use_opacity, out.tex_dib = tex.tex_dib, out.tex_data = tex.tex_data, out.tex_w = tex.tex_w, out.tex_h = tex.tex_h, out.tex_file = tex.tex_file, out.colorized = tex.colorized;
} return out; } function readDib(ar, r) { var subtype = r.u32(), length = r.u32(); if (length > r.data.length)
    throw new LegacyParseError("implausible dib length ".concat(length, " ").concat(r.ctx())); var data = r.raw(length); return { k: "dib", subtype: subtype, data: data }; } function readFtc(ar, r) { preamble(ar, r), r.u32(); var ks = r.f64s(24), frontPinsCount = r.u32(), frontPins = []; for (var i_42 = 0; i_42 < frontPinsCount; i_42++)
    frontPins.push(r.f64s(4)); var backPinsCount = r.u32(), backPins = []; for (var i_43 = 0; i_43 < backPinsCount; i_43++)
    backPins.push(r.f64s(4)); var fflags = r.u32(), bflags = r.u32(); return { k: "ftc", front: ks.slice(0, 9), back: ks.slice(12, 21), front_pins: frontPins, back_pins: backPins, front_projected: !!(fflags & 2), back_projected: !!(bflags & 2) }; } function readCamera(ar, r) { return r.raw(137), r.u16(), r.utf16(), r.raw(33), { k: "camera" }; } function readThumbnail(ar, r) { if (preamble(ar, r), ar.ver < FIRST_V4)
    return r.raw(129), { k: "thumbnail", dib: null }; ar.readObject(r, "CCamera"); var _j = __read(ar.readObject(r, "CDib"), 3), dib = _j[2]; return { k: "thumbnail", dib: dib }; } function readImage(ar, r) { preamble(ar, r); var db = drawbase(ar, r), _j = __read(ar.readObject(r), 1), ds = _j[0], xform = r.f64s(12); r.f64(), r.utf16(); var guid = r.raw(16); return { k: "image", db: db, def: ds, xform: xform, guid: toHex(guid) }; } function entityRef(ar, r) { var tag = r.u16(); if (tag === 0)
    return null; if (tag === 32767) {
    var big = r.u32();
    if (big & 2147483648)
        throw new LegacyParseError("entity ref is a new object ".concat(r.ctx()));
    return big;
} if (tag === 65535 || tag & 32768)
    throw new LegacyParseError("entity ref is a new object ".concat(r.ctx())); return tag; } function readRelationship(ar, r) { preamble(ar, r); var a = entityRef(ar, r), b = entityRef(ar, r); return { k: "relationship", refs: [a, b] }; } function strictNextTag(ar, data, at, allowNull) {
    if (allowNull === void 0) { allowNull = !0; }
    if (at + 2 > data.length)
        return !1;
    var t = new DataView(data.buffer, data.byteOffset, data.byteLength).getUint16(at, !0);
    if (t === 0)
        return allowNull;
    if (t === 32767 || t === 65535)
        return !0;
    if (t & 32768) {
        var ent = ar.slots.get(t & 32767);
        return ent !== void 0 && ent[0] === "class";
    }
    return !1;
} function readConstructionLine(ar, r) {
    var e_48, _j, e_49, _k;
    preamble(ar, r), drawbase(ar, r);
    var point = r.f64s(3), direction = r.f64s(3), _l = __read(r.f64s(2), 2), startParam = _l[0], endParam = _l[1], k = ar.clineTail;
    if (k === null) {
        var dflt_1 = ar.ver === 17 ? 7 : 4, order = __spreadArray([dflt_1], __read([0, 4, 7].filter(function (c) { return c !== dflt_1; })), false);
        try {
            outer: for (var _m = __values([!1, !0]), _o = _m.next(); !_o.done; _o = _m.next()) {
                var allowNull = _o.value;
                try {
                    for (var order_1 = (e_49 = void 0, __values(order)), order_1_1 = order_1.next(); !order_1_1.done; order_1_1 = order_1.next()) {
                        var cand = order_1_1.value;
                        if (strictNextTag(ar, r.data, r.pos + cand, allowNull)) {
                            k = cand;
                            break outer;
                        }
                    }
                }
                catch (e_49_1) { e_49 = { error: e_49_1 }; }
                finally {
                    try {
                        if (order_1_1 && !order_1_1.done && (_k = order_1.return)) _k.call(order_1);
                    }
                    finally { if (e_49) throw e_49.error; }
                }
            }
        }
        catch (e_48_1) { e_48 = { error: e_48_1 }; }
        finally {
            try {
                if (_o && !_o.done && (_j = _m.return)) _j.call(_m);
            }
            finally { if (e_48) throw e_48.error; }
        }
        k === null && (k = dflt_1), ar.clineTail = k;
    }
    r.raw(k);
    var huge = 1e20, start = Math.abs(startParam) >= huge ? null : [point[0] + direction[0] * startParam, point[1] + direction[1] * startParam, point[2] + direction[2] * startParam], end = Math.abs(endParam) >= huge ? null : [point[0] + direction[0] * endParam, point[1] + direction[1] * endParam, point[2] + direction[2] * endParam];
    return { k: "cline", point: [point[0], point[1], point[2]], direction: [direction[0], direction[1], direction[2]], start: start, end: end };
} function readConstructionPoint(ar, r) { preamble(ar, r); var db = drawbase(ar, r), pos = r.f64s(3); return r.f64s(3), r.u8(), { k: "cpoint", db: db, pos: pos }; } function readSectionPlane(ar, r) { preamble(ar, r); var db = drawbase(ar, r), first = new DataView(r.data.buffer, r.data.byteOffset, r.data.byteLength).getFloat64(r.pos, !0); Math.abs(first) <= 1.0001 || ar.readObject(r); var plane = r.f64s(4), name = "", label = ""; return bytesEqual(r.peek(3), STR_MARKER) && (name = r.utf16(), label = r.utf16()), { k: "sectionplane", plane: plane, name: name, label: label, db: db }; } function readSkFont(ar, r) { return ar.readObject(r, "CAttributeContainer"), ar.hasPid && r.u8(), r.utf16(), r.raw(15), { k: "font" }; } function readDimLinear(ar, r) { preamble(ar, r); var db = drawbase(ar, r), text = r.utf16(); ar.readObject(r, "CSkFont"), r.raw(37); var c1 = entityRef(ar, r); r.raw(42); var c2 = entityRef(ar, r); return r.raw(82), { k: "dimension", db: db, text: text, connect: [c1, c2] }; } function readText(ar, r) { preamble(ar, r); var db = drawbase(ar, r); ar.readObject(r, "CSkFont"); var p = r.pos, idx; for (;;) {
    if (idx = findBytes(r.data, STR_MARKER, p, r.pos + 512), idx < 0)
        throw new LegacyParseError("text delimiter not found ".concat(r.ctx()));
    var blk = r.data.subarray(idx - 11, idx);
    if (blk[0] === 1 && blk[1] === 0 && blk[2] === 0 && blk[3] === 0 && blk[6] === 3 && blk[7] === 0 && blk[8] === 0 && blk[9] === 0 && blk[10] === 1)
        break;
    p = idx + 3;
} r.raw(idx - r.pos); var text = r.utf16(); r.raw(5); var attach = []; for (;;) {
    var head = r.peek(2);
    if (!(head.length === 2 && head[0] === 255 && head[1] === 127))
        break;
    var full = r.peek(6);
    if (full.length < 6)
        break;
    var val = new DataView(full.buffer, full.byteOffset, full.byteLength).getUint32(2, !0);
    if (val & 2147483648)
        break;
    r.raw(6), attach.push(val);
} return { k: "text", text: text, db: db, attach: attach }; } function readEntityList(ar, r, count, owner) { var ents = []; ar.burnStack.push(0); try {
    return readEntityListInner(ar, r, count, owner, ents);
}
finally {
    ar.burnStack.pop();
} } function readEntityListInner(ar, r, count, owner, ents) { var view = new DataView(r.data.buffer, r.data.byteOffset, r.data.byteLength); for (; ents.length < count;) {
    var p = r.pos, hasBurnCredit = owner === "def" && ar.burnStack.length > 0 && ar.burnStack[ar.burnStack.length - 1] > 0;
    if (hasBurnCredit && p + 25 <= r.data.length && view.getUint32(p, !0) === 0 && bytesEqual(r.data.subarray(p + 22, p + 25), STR_MARKER))
        break;
    var prevFlag = ar.inEntityList;
    ar.inEntityList = !0;
    try {
        var _j = __read(ar.readObject(r), 3), s = _j[0], n = _j[1], v = _j[2];
        ar.inEntityList = prevFlag, ents.push([s, n, v]);
    }
    catch (e) {
        if (ar.inEntityList = prevFlag, !(e instanceof LegacyParseError))
            throw e;
        if (owner === "root") {
            r.pos = p;
            break;
        }
        if (hasBurnCredit) {
            r.pos = p;
            break;
        }
        throw e;
    }
} return ents; } function readDefinition(ar, r) { preamble(ar, r), r.raw(ar.ver >= 17 ? 22 : ar.ver >= FIRST_V4 ? 20 : 13); var nlayers = r.u32(); if (nlayers > 1e4)
    throw new LegacyParseError("implausible def layer count ".concat(r.ctx())); var got = 0; for (; got < nlayers;) {
    if (r.peekU16() === 0) {
        r.pos += 2;
        continue;
    }
    ar.readObject(r, "CLayer"), got += 1;
} r.u16() === 32767 && r.u32(); var count = null; if (ar.ver >= 20 && (count = retryCountAfterV20Filler(r, r.pos, 5e6, ar)), count === null && (r.u32(), count = r.u32()), count > 5e6 || count === 0) {
    var retry = retryCountAfterV20Filler(r, r.pos - 4, 5e6, ar);
    retry !== null && (count = retry);
} if (count > 5e6)
    throw new LegacyParseError("implausible def entity count ".concat(r.ctx())); var ents = readEntityList(ar, r, count, "def"), nrel = r.u32(); if (nrel > 1e5) {
    var retry = retryCountAfterV20Filler(r, r.pos - 4, 1e5, ar);
    retry !== null && (nrel = retry);
} if (nrel > 1e5)
    throw new LegacyParseError("definition list misaligned ".concat(r.ctx())); for (var i_44 = 0; i_44 < nrel; i_44++)
    ar.readObject(r, "CRelationship"); if (r.u16(), !bytesEqual(r.peek(19).subarray(16, 19), STR_MARKER))
    for (var skip = 1; skip <= 4; skip++) {
        var at = r.pos + skip;
        if (bytesEqual(r.data.subarray(at + 16, at + 19), STR_MARKER)) {
            r.pos = at;
            break;
        }
    } var guid = r.raw(16), name = r.utf16(); r.utf16(), r.utf16(), r.u32(); var tpos = null, thumbSlot = ar.classSlot.get("CThumbnail"); for (var off = 0; off < 96; off++) {
    var p = r.pos + off;
    if (r.data[p] === 255 && r.data[p + 1] === 255 && r.data[p + 4] === 10 && r.data[p + 5] === 0 && matchesAscii(r.data, p + 6, "CThumbnail")) {
        tpos = p;
        break;
    }
    if (thumbSlot !== void 0 && isClassRef(r.data, p, thumbSlot)) {
        tpos = p;
        break;
    }
} if (tpos === null)
    throw new LegacyParseError("definition tail: thumbnail not found ".concat(r.ctx())); var gap = r.raw(tpos - r.pos), behavior = gap.length >= 9 ? gap[gap.length - 9] : 0; return ar.readObject(r, "CThumbnail"), { k: "definition", name: name, guid: toHex(guid), ents: ents, faces_camera: !!(behavior & 1), shadows_face_sun: !!(behavior & 2) }; } function readInstance(ar, r) { var pre = preamble(ar, r), db = drawbase(ar, r), _j = __read(ar.readObject(r, "CComponentDefinition"), 2), ds = _j[0], dn = _j[1]; if (dn !== "CComponentDefinition")
    throw new LegacyParseError("instance definition ref is ".concat(dn, " ").concat(r.ctx())); var xf = r.f64s(13), name = ar.ver >= FIRST_V4 || bytesEqual(r.peek(3), STR_MARKER) ? r.utf16() : "", guid = ar.ver >= 14 ? r.raw(16) : new Uint8Array(0); return { k: "instance", db: db, def: ds, xf: xf, name: name, guid: toHex(guid), attrs: pre.attrs }; } var READERS = { CVertex: readVertex, CEdge: readEdge, CCurve: readCurve, CArcCurve: readArcCurve, CEdgeUse: readEdgeUse, CLoop: readLoop, CFace: readFace, CLayer: readLayer, CMaterial: readMaterial, CDib: readDib, CAttributeContainer: readAttrContainer, CAttributeNamed: readAttrNamed, CCamera: readCamera, CThumbnail: readThumbnail, CRelationship: readRelationship, CComponentDefinition: readDefinition, CImage: readImage, CComponentInstance: readInstance, CGroup: readInstance, CFaceTextureCoords: readFtc, CConstructionLine: readConstructionLine, CConstructionPoint: readConstructionPoint, CSectionPlane: readSectionPlane, CSkFont: readSkFont, CDimensionLinear: readDimLinear, CText: readText }; function isLegacy(data) { if (!(data.length >= 4 && data[0] === 255 && data[1] === 254 && data[2] === 255 && data[3] === 14))
    return !1; var head100 = data.subarray(0, Math.min(256, data.length)); if (findBytes(head100, new Uint8Array([80, 75, 3, 4])) >= 0)
    return !1; var head200 = data.subarray(0, Math.min(512, data.length)); return findBytes(head200, new Uint8Array(asciiBytes("CVersionMap"))) >= 0; } var CMATERIAL_PATTERN = __spreadArray([255, 255, null, null, 9, 0], __read(asciiBytes("CMaterial")), false), CLAYER_PATTERN = __spreadArray([255, 255, null, null, 6, 0], __read(asciiBytes("CLayer")), false); function findVersionMajor(data) { var head = data.subarray(0, Math.min(96, data.length)), stripped = []; for (var i_45 = 0; i_45 < head.length; i_45++)
    head[i_45] !== 0 && stripped.push(head[i_45]); var m = new TextDecoder("latin1").decode(new Uint8Array(stripped)).match(/\{(\d+)\./); return m ? parseInt(m[1], 10) : null; } function bootstrapTwoMaterials(data, ver, matHdr) { var boot = new Archive(data, ver); Object.assign(boot.readers, READERS), boot.nextSlot = 1 << 20, boot.walkBase = 1 << 20, boot.r.pos = matHdr, boot.readObject(boot.r, "CMaterial"); var tag = boot.r.peekU16(); if (tag === 65535 || !(tag & 32768))
    throw new LegacyParseError("cannot bootstrap the slot base"); return tag & 32767; } function probeLayerAnchorBases(data, ver, start, matCount) { var boot = new Archive(data, ver); Object.assign(boot.readers, READERS); var b0 = 1 << 20; boot.nextSlot = b0, boot.walkBase = b0, boot.r.pos = start; for (var i_46 = 0; i_46 < matCount; i_46++)
    boot.readObject(boot.r, "CMaterial"); boot.r.u32(), ver >= 17 && boot.r.u8(); var layerCount = boot.r.u32(); if (!(layerCount >= 1 && layerCount <= 1e5))
    throw new LegacyParseError("implausible layer count in base probe"); var layerSlots = []; for (var i_47 = 0; i_47 < layerCount; i_47++) {
    var _j = __read(boot.readObject(boot.r, "CLayer"), 1), s2 = _j[0];
    layerSlots.push(s2);
} boot.collectTrailingLayers(layerSlots, null, !0); var _k = __read(boot.readObject(boot.r), 2), s = _k[0], n = _k[1]; if (n !== "premodel")
    throw new LegacyParseError("base probe: anchor resolved to ".concat(n)); return layerSlots.map(function (rel) { return s - (rel - b0); }).filter(function (cand) { return cand > 0 && cand < b0; }); } function walk(data) {
    var e_50, _j;
    var ver = findVersionMajor(data);
    if (ver === null)
        throw new LegacyParseError("no version string in header");
    var headerView = new DataView(data.buffer, data.byteOffset, data.byteLength), matHdr = findPattern(data, CMATERIAL_PATTERN), start, matCount;
    if (matHdr >= 0) {
        if (start = matHdr, matCount = headerView.getUint32(matHdr - 4, !0), matCount > 1e5)
            throw new LegacyParseError("implausible material count");
    }
    else {
        var layerHdr = findPattern(data, CLAYER_PATTERN);
        if (layerHdr < 0)
            throw new LegacyParseError("no CMaterial or CLayer class record found");
        matCount = 0, start = layerHdr - (ver >= 17 ? 9 : 8);
    }
    var bases = matCount >= 2 ? [bootstrapTwoMaterials(data, ver, start)] : probeLayerAnchorBases(data, ver, start, matCount), lastExc = null;
    try {
        for (var bases_1 = __values(bases), bases_1_1 = bases_1.next(); !bases_1_1.done; bases_1_1 = bases_1.next()) {
            var base = bases_1_1.value;
            try {
                return walkModel(data, ver, start, matCount, base);
            }
            catch (exc) {
                if (!(exc instanceof LegacyParseError))
                    throw exc;
                lastExc = exc;
            }
        }
    }
    catch (e_50_1) { e_50 = { error: e_50_1 }; }
    finally {
        try {
            if (bases_1_1 && !bases_1_1.done && (_j = bases_1.return)) _j.call(bases_1);
        }
        finally { if (e_50) throw e_50.error; }
    }
    throw lastExc !== null ? lastExc : new LegacyParseError("no viable slot base candidate");
} var RELEASED_ENTITIES = new Map(["CVertex", "CEdge", "CEdgeUse", "CLoop", "CFace"].map(function (name) { return [name, ["obj", name, null]]; })); function buildAndReleaseDefinition(ar, slot, def) { var builder = new LegacyBuilder; try {
    fillBuilder(builder, def.ents, ar.slots);
}
catch (e) {
    throw new SkpParseError("Failed while building component definitions: ".concat(e.message), { stage: "legacy_defs", definitionId: slot, cause: e });
} ar.prebuilt.set(slot, builder), def.ents = [], ar.releasedSpans.push([slot + 1, ar.nextSlot]); for (var k = slot + 1; k < ar.nextSlot; k++) {
    var ent = ar.slots.get(k);
    if (ent === void 0 || ent[0] !== "obj" || ent[2] === null || ent[1] === null)
        continue;
    var placeholder = RELEASED_ENTITIES.get(ent[1]);
    placeholder !== void 0 && ar.slots.set(k, placeholder);
} } function walkModel(data, ver, start, matCount, base) { var ar = new Archive(data, ver); Object.assign(ar.readers, READERS), ar.nextSlot = base, ar.walkBase = base, ar.onDefinitionDone = function (slot, def) { return buildAndReleaseDefinition(ar, slot, def); }; var r = ar.r; r.pos = start; var materials = []; for (var i_48 = 0; i_48 < matCount; i_48++) {
    var _j = __read(ar.readObject(r, "CMaterial"), 3), s = _j[0], v = _j[2];
    materials.push([s, v]);
} r.u32(), ver >= 17 && r.u8(); var layerCount = ver < FIRST_V4 ? Math.pow(2, 30) : r.u32(); if (layerCount > 1e5 && ver >= FIRST_V4)
    throw new LegacyParseError("implausible layer count"); var layers = []; for (; layers.length < layerCount;) {
    var tag = r.peekU16();
    if (tag === 0) {
        r.pos += 2;
        continue;
    }
    if (tag !== 65535 && !(tag & 32768))
        break;
    var _k = __read(ar.readObject(r, "CLayer"), 3), s = _k[0], v = _k[2];
    v !== null && layers.push([s, v]);
} ar.collectTrailingLayers(null, layers); var _l = __read(ar.readObject(r), 2), dn = _l[1]; if (dn !== "CLayer")
    throw new LegacyParseError("definition-list anchor is ".concat(dn, ", not a layer")); var defCount = r.u32(); if (defCount > 1e6) {
    var retry = retryCountAfterV20Filler(r, r.pos - 4, 1e6, ar);
    retry !== null && (defCount = retry);
} if (defCount > 1e6)
    throw new LegacyParseError("implausible definition count"); for (var i_49 = 0; i_49 < defCount; i_49++)
    ar.readObject(r, "CComponentDefinition"); var defCls = ar.classSlot.get("CComponentDefinition"); for (;;) {
    var tag = r.peekU16(), isDef = defCls !== void 0 && tag === (32768 | defCls);
    if (!isDef && tag === 65535 && matchesAscii(r.peek(26), 6, "CComponentDefinition") && (isDef = !0), !isDef)
        break;
    ar.readObject(r);
} var rootCount = r.u32(); if (rootCount > 5e6) {
    var retry = retryCountAfterV20Filler(r, r.pos - 4, 5e6, ar);
    retry !== null && (rootCount = retry);
} if (rootCount > 5e6)
    throw new LegacyParseError("implausible root entity count"); var root = readEntityList(ar, r, rootCount, "root"); return { ar: ar, root: root, layers: layers, materials: materials }; } var LegacyBuilder = (function () {
    function LegacyBuilder() {
        this.vertices = new DefaultVertexStore;
        this.edges = new Map;
        this.edgeFlags = new EdgeFlagStore;
        this.faces = new Map;
        this.instances = [];
        this.sectionPlanes = [];
        this.texts = [];
        this.dimensions = [];
        this.constructionLines = [];
        this.constructionPoints = [];
    }
    return LegacyBuilder;
}()); function addEdge(builder, slot, e, slots) {
    var e_51, _j;
    if (builder.edges.has(slot))
        return;
    var v1 = e.v1, v2 = e.v2;
    try {
        for (var _k = __values([v1, v2]), _l = _k.next(); !_l.done; _l = _k.next()) {
            var vs = _l.value;
            if (vs == null)
                continue;
            var ent = slots.get(vs);
            if (ent !== void 0 && ent[2] !== null && !builder.vertices.has(vs)) {
                var xyz = ent[2].xyz;
                builder.vertices.set(vs, [xyz[0], xyz[1], xyz[2]]);
            }
        }
    }
    catch (e_51_1) { e_51 = { error: e_51_1 }; }
    finally {
        try {
            if (_l && !_l.done && (_j = _k.return)) _j.call(_k);
        }
        finally { if (e_51) throw e_51.error; }
    }
    builder.edges.set(slot, [v1, v2]);
    var db = e.db || {}, flags = (db.soft ? 8 : 0) | (db.smooth ? 16 : 0) | (db.hidden ? 1 : 0);
    flags && builder.edgeFlags.set(slot, flags);
} function fillBuilder(builder, ents, slots) {
    var e_52, _j, e_53, _k, e_54, _l, e_55, _m;
    try {
        for (var ents_1 = __values(ents), ents_1_1 = ents_1.next(); !ents_1_1.done; ents_1_1 = ents_1.next()) {
            var _o = __read(ents_1_1.value, 3), s = _o[0], v = _o[2];
            if (v === null || typeof v != "object")
                continue;
            var k = v.k;
            if (k === "edge")
                addEdge(builder, s, v, slots);
            else if (k === "face") {
                var loops = [];
                try {
                    for (var _p = (e_53 = void 0, __values(v.loops)), _q = _p.next(); !_q.done; _q = _p.next()) {
                        var lp = _q.value;
                        var loop = [];
                        try {
                            for (var _r = (e_54 = void 0, __values(lp.uses)), _s = _r.next(); !_s.done; _s = _r.next()) {
                                var u = _s.value;
                                var es = u.edge, ent = slots.get(es);
                                ent === void 0 || ent[2] === null || (addEdge(builder, es, ent[2], slots), loop.push({ edgeId: es, orientation: u.sense ? -1 : 1 }));
                            }
                        }
                        catch (e_54_1) { e_54 = { error: e_54_1 }; }
                        finally {
                            try {
                                if (_s && !_s.done && (_l = _r.return)) _l.call(_r);
                            }
                            finally { if (e_54) throw e_54.error; }
                        }
                        loops.push(loop);
                    }
                }
                catch (e_53_1) { e_53 = { error: e_53_1 }; }
                finally {
                    try {
                        if (_q && !_q.done && (_k = _p.return)) _k.call(_p);
                    }
                    finally { if (e_53) throw e_53.error; }
                }
                var face = { loops: loops, normal: [v.plane[0], v.plane[1], v.plane[2]], materialId: v.db.mat || null, backMaterialId: v.back_mat || null, uvTransform: null, uvTransformBack: null, uvProjected: !1, uvProjectedBack: !1, hidden: !!v.db.hidden }, attrs = v.attrs;
                if (attrs && typeof attrs == "object")
                    try {
                        for (var _t = (e_55 = void 0, __values(attrs.children || [])), _u = _t.next(); !_u.done; _u = _t.next()) {
                            var _v = __read(_u.value, 2), cv = _v[1];
                            cv && typeof cv == "object" && cv.k === "ftc" && (face.uvTransform = __spreadArray([], __read(cv.front), false), face.uvTransformBack = __spreadArray([], __read(cv.back), false), face.uvProjected = cv.front_projected, face.uvProjectedBack = cv.back_projected);
                        }
                    }
                    catch (e_55_1) { e_55 = { error: e_55_1 }; }
                    finally {
                        try {
                            if (_u && !_u.done && (_m = _t.return)) _m.call(_t);
                        }
                        finally { if (e_55) throw e_55.error; }
                    }
                builder.faces.set(s, face);
            }
            else
                k === "instance" ? builder.instances.push({ offset: 0, name: v.name, refIdx: v.def, refGuid: "", matrix: __spreadArray([], __read(v.xf), false), materialId: v.db.mat || null, layerId: v.db.layer || null, hidden: !!v.db.hidden, children: [], properties: extractLegacyDynamicProperties(v.attrs) }) : k === "image" ? builder.instances.push({ offset: 0, name: "", refIdx: v.def, refGuid: v.guid || "", matrix: __spreadArray([], __read(v.xform), false), materialId: v.db.mat || null, layerId: v.db.layer || null, hidden: !!v.db.hidden, children: [], properties: {} }) : k === "sectionplane" ? builder.sectionPlanes.push({ plane: v.plane || [0, 0, 1, 0], name: v.name || "", label: v.label || "", hidden: !!(v.db && v.db.hidden) }) : k === "text" ? builder.texts.push({ text: v.text || "", hidden: !!(v.db && v.db.hidden) }) : k === "dimension" ? builder.dimensions.push({ text: v.text || "", hidden: !!(v.db && v.db.hidden) }) : k === "cline" ? builder.constructionLines.push({ point: v.point, direction: v.direction, start: v.start, end: v.end }) : k === "cpoint" && builder.constructionPoints.push({ position: [v.pos[0], v.pos[1], v.pos[2]] });
        }
    }
    catch (e_52_1) { e_52 = { error: e_52_1 }; }
    finally {
        try {
            if (ents_1_1 && !ents_1_1.done && (_j = ents_1.return)) _j.call(ents_1);
        }
        finally { if (e_52) throw e_52.error; }
    }
} function parseLegacyToRaw(data, options) {
    var e_56, _j, e_57, _k, e_58, _l, e_59, _m;
    var _a2;
    var t0 = Date.now();
    emitLog(options, "info", "Parsing legacy buffer (".concat(data.length, " bytes)"));
    var version = "unknown", second = findBytes(data, STR_MARKER, 4);
    if (second > 0) {
        var textBytes = data.subarray(second + 4, Math.min(second + 100, data.length)), text = new TextDecoder("utf-16le", { fatal: !1 }).decode(textBytes), braceStart = text.indexOf("{"), braceEnd = text.indexOf("}");
        braceStart >= 0 && braceEnd >= 0 && (version = text.slice(braceStart, braceEnd + 1));
    }
    emitLog(options, "debug", "Detected legacy version ".concat(version));
    var walkResult;
    try {
        walkResult = walk(data);
    }
    catch (e) {
        throw e instanceof LegacyParseError || e instanceof RangeError ? new SkpParseError("legacy .skp parse failed: ".concat(e.message), { stage: "legacy_walk", cause: e }) : e;
    }
    var ar = walkResult.ar, root = walkResult.root, layers = walkResult.layers, materials = walkResult.materials, slots = ar.slots;
    emitLog(options, "debug", "Legacy walk complete: ".concat(materials.length, " materials, ").concat(layers.length, " layers"));
    var imageDefIds = new Set;
    try {
        for (var _o = __values(slots.values()), _p = _o.next(); !_p.done; _p = _o.next()) {
            var ent = _p.value;
            ent[0] === "obj" && ent[1] === "CImage" && ent[2] && imageDefIds.add(ent[2].def);
        }
    }
    catch (e_56_1) { e_56 = { error: e_56_1 }; }
    finally {
        try {
            if (_p && !_p.done && (_j = _o.return)) _j.call(_o);
        }
        finally { if (e_56) throw e_56.error; }
    }
    var materialsMap = new Map, materialIdToName = new Map;
    try {
        for (var materials_1 = __values(materials), materials_1_1 = materials_1.next(); !materials_1_1.done; materials_1_1 = materials_1.next()) {
            var _q = __read(materials_1_1.value, 2), s = _q[0], v = _q[1];
            var rgba = v.rgba || [128, 128, 128, 255], trans = void 0;
            v.use_opacity ? trans = Math.min(Math.max(1 - v.opacity, 0), 1) : trans = 1;
            var colorized = v.colorized || !1, texture = null;
            if ("tex_dib" in v) {
                var dib = v.tex_dib !== null ? slots.get(v.tex_dib) : void 0, texData = dib && dib[2] ? dib[2].data : (_a2 = v.tex_data) != null ? _a2 : null, ext = texData && texData.length >= 4 && texData[0] === 137 && texData[1] === 80 && texData[2] === 78 && texData[3] === 71 ? ".png" : ".jpg";
                texture = { filename: v.tex_file || "".concat(v.name).concat(ext), width: v.tex_w, height: v.tex_h, data: texData };
            }
            var matObj = { name: v.name, color: { r: rgba[0], g: rgba[1], b: rgba[2], a: rgba[3] }, transparency: trans, id: null, texture: texture, colorized: colorized, colorizeType: colorized ? 1 : 0 };
            materialsMap.set(v.name, matObj), materialIdToName.set(s, v.name);
        }
    }
    catch (e_57_1) { e_57 = { error: e_57_1 }; }
    finally {
        try {
            if (materials_1_1 && !materials_1_1.done && (_k = materials_1.return)) _k.call(materials_1);
        }
        finally { if (e_57) throw e_57.error; }
    }
    var layerColors = new Map, layerHidden = new Map, layerIdToName = new Map;
    try {
        for (var layers_1 = __values(layers), layers_1_1 = layers_1.next(); !layers_1_1.done; layers_1_1 = layers_1.next()) {
            var _r = __read(layers_1_1.value, 2), s = _r[0], v = _r[1];
            var rgba = v.rgba || [136, 136, 136, 255];
            layerColors.set(v.name, [rgba[0], rgba[1], rgba[2]]), layerHidden.set(v.name, !!v.hidden), layerIdToName.set(s, v.name);
        }
    }
    catch (e_58_1) { e_58 = { error: e_58_1 }; }
    finally {
        try {
            if (layers_1_1 && !layers_1_1.done && (_l = layers_1.return)) _l.call(layers_1);
        }
        finally { if (e_58) throw e_58.error; }
    }
    layerColors.has("Layer0") || layerColors.set("Layer0", [136, 136, 136]), layerHidden.has("Layer0") || layerHidden.set("Layer0", !1);
    var defsDict = new Map, processed = 0, lastSlot;
    try {
        try {
            for (var _s = __values(slots.entries()), _t = _s.next(); !_t.done; _t = _s.next()) {
                var _u = __read(_t.value, 2), s = _u[0], ent = _u[1];
                if (lastSlot = s, ent[0] === "obj" && ent[1] === "CComponentDefinition" && ent[2]) {
                    var d = ent[2], b = ar.prebuilt.get(s);
                    b === void 0 && (b = new LegacyBuilder, fillBuilder(b, d.ents, slots)), defsDict.set(s, { guid: d.guid, name: d.name, isImage: imageDefIds.has(s), alwaysFacesCamera: d.faces_camera || !1, shadowsFaceSun: d.shadows_face_sun || !1, builder: b }), processed++, processed % 500 === 0 && (emitProgress(options, "legacy_defs", processed, processed), emitLog(options, "debug", "Processed ".concat(processed, " component definitions")));
                }
            }
        }
        catch (e_59_1) { e_59 = { error: e_59_1 }; }
        finally {
            try {
                if (_t && !_t.done && (_m = _s.return)) _m.call(_s);
            }
            finally { if (e_59) throw e_59.error; }
        }
    }
    catch (e) {
        throw new SkpParseError("Failed while building component definitions: ".concat(e.message), { stage: "legacy_defs", definitionId: lastSlot, cause: e });
    }
    var rootBuilder = new LegacyBuilder;
    return fillBuilder(rootBuilder, root, slots), defsDict.set("ROOT", { guid: "ROOT", name: "ROOT_MODEL", isImage: !1, alwaysFacesCamera: !1, shadowsFaceSun: !1, builder: rootBuilder }), emitLog(options, "info", "Parse complete: ".concat(defsDict.size, " defs (").concat(((Date.now() - t0) / 1e3).toFixed(2), "s)")), { version: version, units: null, layerColors: layerColors, layerHidden: layerHidden, layerIdToName: layerIdToName, pages: [], dimensions: [], materialIdToName: materialIdToName, materialsMap: materialsMap, materialsByFolder: new Map, styles: [], defsDict: defsDict };
} function tlvItemsInt(buf) { if (buf === null)
    return null; var items = [], off = 0, n = buf.length; for (; off < n;) {
    if (off + 6 > n)
        return null;
    var tag = buf[off] | buf[off + 1] << 8, ln = readU32(buf, off + 2);
    if (tag === 0 || off + 6 + ln > n)
        return null;
    items.push({ tag: tag, payload: buf.subarray(off + 6, off + 6 + ln) }), off += 6 + ln;
} return items; } function tlvFindInt(items, tag) {
    var e_60, _j;
    if (items === null)
        return null;
    try {
        for (var items_1 = __values(items), items_1_1 = items_1.next(); !items_1_1.done; items_1_1 = items_1.next()) {
            var it = items_1_1.value;
            if (it.tag === tag)
                return it.payload;
        }
    }
    catch (e_60_1) { e_60 = { error: e_60_1 }; }
    finally {
        try {
            if (items_1_1 && !items_1_1.done && (_j = items_1.return)) _j.call(items_1);
        }
        finally { if (e_60) throw e_60.error; }
    }
    return null;
} function toHex2(data) { var s = ""; for (var i_50 = 0; i_50 < data.length; i_50++) {
    var h = data[i_50].toString(16).toUpperCase();
    s += h.length === 1 ? "0" + h : h;
} return s; } function stripDe05(p) { if (p.length >= 2 && p[0] === 222 && p[1] === 5) {
    var idlen = readU32(p, 2);
    return p.subarray(6, 6 + idlen);
} return p; } function findBytes2(data, needle, start) {
    if (start === void 0) { start = 0; }
    var nlen = needle.length, limit = data.length - nlen;
    outer: for (var i_51 = start; i_51 <= limit; i_51++) {
        for (var j = 0; j < nlen; j++)
            if (data[i_51 + j] !== needle[j])
                continue outer;
        return i_51;
    }
    return -1;
} function scanVertexPositions(top, id2pos) { function walk2(nodes) {
    var e_61, _j;
    try {
        for (var nodes_7 = __values(nodes), nodes_7_1 = nodes_7.next(); !nodes_7_1.done; nodes_7_1 = nodes_7.next()) {
            var el = nodes_7_1.value;
            if (el.tag === "C409") {
                var dc05 = findChildTag(el.children, "DC05"), c509 = findChildTag(el.children, "C509");
                if (dc05 && c509 && c509.payload.length === 24) {
                    var idb = stripDe05(dc05.payload);
                    id2pos.set(toHex2(idb), [readF64(c509.payload, 0), readF64(c509.payload, 8), readF64(c509.payload, 16)]);
                }
            }
            el.children.length > 0 && walk2(el.children);
        }
    }
    catch (e_61_1) { e_61 = { error: e_61_1 }; }
    finally {
        try {
            if (nodes_7_1 && !nodes_7_1.done && (_j = nodes_7.return)) _j.call(nodes_7);
        }
        finally { if (e_61) throw e_61.error; }
    }
} walk2([top]); } function scanInstanceTransforms(top, world) { function walk2(nodes, parent) {
    var e_62, _j;
    try {
        for (var nodes_8 = __values(nodes), nodes_8_1 = nodes_8.next(); !nodes_8_1.done; nodes_8_1 = nodes_8.next()) {
            var el = nodes_8_1.value;
            if (el.tag === "6419") {
                var d007 = findChildTag(el.children, "D007"), dc05 = d007 ? findChildTag(d007.children, "DC05") : null, iid = dc05 ? toHex2(stripDe05(dc05.payload)) : null, m = findChildTag(el.children, "6619"), mat = null;
                if (m && m.payload.length === 104) {
                    mat = [];
                    for (var i_52 = 0; i_52 < 13; i_52++)
                        mat.push(readF64(m.payload, i_52 * 8));
                }
                var here = mat !== null ? multiplyMatrices(parent, mat) : parent;
                iid !== null && world.set(iid, here), walk2(el.children, here);
            }
            else
                el.children.length > 0 && walk2(el.children, parent);
        }
    }
    catch (e_62_1) { e_62 = { error: e_62_1 }; }
    finally {
        try {
            if (nodes_8_1 && !nodes_8_1.done && (_j = nodes_8.return)) _j.call(nodes_8);
        }
        finally { if (e_62) throw e_62.error; }
    }
} walk2([top], null); } function parseDimensions(modelData, id2pos, instWorld) {
    var e_63, _j;
    var dims = [], needle = new Uint8Array([204, 91]), i = 0, n = modelData.length;
    function point(blockPayload) { if (blockPayload === null)
        return null; var blk = tlvFindInt(tlvItemsInt(blockPayload), 21e3); if (blk === null)
        return null; var sub = tlvItemsInt(blk), typB = tlvFindInt(sub, 21001); if ((typB !== null && typB.length === 4 ? readU32(typB, 0) : null) === 1) {
        var pos = tlvFindInt(sub, 21002);
        return pos === null || pos.length !== 24 ? null : [readF64(pos, 0), readF64(pos, 8), readF64(pos, 16)];
    } var refB = tlvFindInt(sub, 21003), f53fc = refB !== null ? tlvFindInt(tlvItemsInt(refB), 21500) : null, fi = f53fc !== null ? tlvItemsInt(f53fc) : null, vid = tlvFindInt(fi, 21501), iid = tlvFindInt(fi, 21502); if (vid === null)
        return null; var local = id2pos.get(toHex2(vid)); if (local === void 0)
        return null; if (iid !== null && iid.length >= 1 && iid[0] > 0 && 1 + iid[0] <= iid.length) {
        var idBytes = iid.subarray(1, 1 + iid[0]), w = instWorld.get(toHex2(idBytes));
        if (w)
            return transformPoint(w, local);
    } return local; }
    for (;;) {
        var j = findBytes2(modelData, needle, i);
        if (j < 0)
            break;
        if (i = j + 1, j + 6 > n)
            continue;
        var ln = readU32(modelData, j + 2);
        if (ln < 40 || j + 6 + ln > n)
            continue;
        var bodyBytes = modelData.subarray(j + 6, j + 6 + ln), body = tlvItemsInt(bodyBytes);
        if (body === null)
            continue;
        var has5Bcd = !1, has5Bce = !1;
        try {
            for (var body_1 = (e_63 = void 0, __values(body)), body_1_1 = body_1.next(); !body_1_1.done; body_1_1 = body_1.next()) {
                var it = body_1_1.value;
                it.tag === 23501 && (has5Bcd = !0), it.tag === 23502 && (has5Bce = !0);
            }
        }
        catch (e_63_1) { e_63 = { error: e_63_1 }; }
        finally {
            try {
                if (body_1_1 && !body_1_1.done && (_j = body_1.return)) _j.call(body_1);
            }
            finally { if (e_63) throw e_63.error; }
        }
        if (!has5Bcd || !has5Bce)
            continue;
        var a = point(tlvFindInt(body, 23501)), b = point(tlvFindInt(body, 23502));
        if (a === null || b === null)
            continue;
        var xaxisB = tlvFindInt(body, 23503), normalB = tlvFindInt(body, 23504), offB = tlvFindInt(body, 23506);
        dims.push({ a: a, b: b, planeX: xaxisB !== null && xaxisB.length === 24 ? [readF64(xaxisB, 0), readF64(xaxisB, 8), readF64(xaxisB, 16)] : null, normal: normalB !== null && normalB.length === 24 ? [readF64(normalB, 0), readF64(normalB, 8), readF64(normalB, 16)] : null, offset: offB !== null && offB.length === 8 ? readF64(offB, 0) : 0, text: "" });
    }
    return dims;
} function findPageNode(top) { return findChildTag([top], "0702"); } function parsePages(node) {
    var e_64, _j, e_65, _k, e_66, _l;
    var pages = [];
    if (node === null)
        return pages;
    function vec3(p) { return p !== null && p.length === 24 ? [readF64(p, 0), readF64(p, 8), readF64(p, 16)] : null; }
    var t60Items = tlvItemsInt(node.payload);
    if (t60Items === null)
        return pages;
    try {
        for (var t60Items_1 = __values(t60Items), t60Items_1_1 = t60Items_1.next(); !t60Items_1_1.done; t60Items_1_1 = t60Items_1.next()) {
            var it60 = t60Items_1_1.value;
            if (it60.tag !== 28e3)
                continue;
            var t61Items = tlvItemsInt(it60.payload);
            if (t61Items !== null)
                try {
                    for (var t61Items_1 = (e_65 = void 0, __values(t61Items)), t61Items_1_1 = t61Items_1.next(); !t61Items_1_1.done; t61Items_1_1 = t61Items_1.next()) {
                        var it61 = t61Items_1_1.value;
                        if (it61.tag !== 28001)
                            continue;
                        var t48Items = tlvItemsInt(it61.payload);
                        if (t48Items !== null)
                            try {
                                for (var t48Items_1 = (e_66 = void 0, __values(t48Items)), t48Items_1_1 = t48Items_1.next(); !t48Items_1_1.done; t48Items_1_1 = t48Items_1.next()) {
                                    var it48 = t48Items_1_1.value;
                                    if (it48.tag !== 29e3)
                                        continue;
                                    var items = tlvItemsInt(it48.payload);
                                    if (items === null)
                                        continue;
                                    var page = { name: "", eye: null, target: null, up: null, fov: 35, parallel: !1, orthoHeight: 0, hiddenLayerIds: [] }, head = tlvItemsInt(tlvFindInt(items, 28500)), name = tlvFindInt(head, 28501);
                                    name !== null && name.length > 0 && (page.name = new TextDecoder("utf-8").decode(name));
                                    var camWrap = tlvItemsInt(tlvFindInt(items, 29002)), cam = camWrap !== null ? tlvItemsInt(tlvFindInt(camWrap, 13500)) : null;
                                    if (cam !== null) {
                                        page.eye = vec3(tlvFindInt(cam, 13501)), page.target = vec3(tlvFindInt(cam, 13502)), page.up = vec3(tlvFindInt(cam, 13503));
                                        var fov = tlvFindInt(cam, 13508);
                                        fov !== null && fov.length === 8 && (page.fov = readF64(fov, 0));
                                        var flag = tlvFindInt(cam, 13506);
                                        page.parallel = flag !== null && flag.length > 0 && flag[0] === 0;
                                        var height = tlvFindInt(cam, 13507);
                                        height !== null && height.length === 8 && (page.orthoHeight = readF64(height, 0));
                                    }
                                    var hidden = tlvFindInt(items, 29008), off = 0;
                                    for (; hidden !== null && off + 1 <= hidden.length;) {
                                        var ln = hidden[off];
                                        if (ln === 0 || off + 1 + ln > hidden.length)
                                            break;
                                        page.hiddenLayerIds.push(parseVarInt(hidden, off + 1, ln)), off += 1 + ln;
                                    }
                                    page.eye !== null && page.target !== null && pages.push(page);
                                }
                            }
                            catch (e_66_1) { e_66 = { error: e_66_1 }; }
                            finally {
                                try {
                                    if (t48Items_1_1 && !t48Items_1_1.done && (_l = t48Items_1.return)) _l.call(t48Items_1);
                                }
                                finally { if (e_66) throw e_66.error; }
                            }
                    }
                }
                catch (e_65_1) { e_65 = { error: e_65_1 }; }
                finally {
                    try {
                        if (t61Items_1_1 && !t61Items_1_1.done && (_k = t61Items_1.return)) _k.call(t61Items_1);
                    }
                    finally { if (e_65) throw e_65.error; }
                }
        }
    }
    catch (e_64_1) { e_64 = { error: e_64_1 }; }
    finally {
        try {
            if (t60Items_1_1 && !t60Items_1_1.done && (_j = t60Items_1.return)) _j.call(t60Items_1);
        }
        finally { if (e_64) throw e_64.error; }
    }
    return pages;
} function buildInstancedSceneFromParsed(parsed, options) { var t0 = Date.now(), layerColors = parsed.layerColors, layerIdToName = parsed.layerIdToName, materialIdToName = parsed.materialIdToName, materialsMap = parsed.materialsMap, materialsByFolder = parsed.materialsByFolder, defsDict = parsed.defsDict, layerHidden = parsed.layerHidden; emitLog(options, "info", "Building instanced scene: ".concat(defsDict.size, " definitions available")); var instanceCounter = { count: 0 }, getLayerColor = function (name) { var c = layerColors.get(name) || [136, 136, 136]; return { r: c[0], g: c[1], b: c[2] }; }, textures = [], textureIndexByKey = new Map; function textureIndexFor(tex) { if (!tex || !tex.data || tex.data.length === 0)
    return null; var mimeType = sniffImageMime(tex.data); if (mimeType === null)
    return null; var head = Array.from(tex.data.subarray(0, 16)).join(","), key = "".concat(tex.data.length, ":").concat(head), hit = textureIndexByKey.get(key); if (hit !== void 0)
    return hit; var idx = textures.length; return textures.push({ data: tex.data, mimeType: mimeType, filename: tex.filename }), textureIndexByKey.set(key, idx), idx; } var colorToMaterialIndex = new Map, gltfMaterials = []; function getMaterialIndex(color, doubleSided, textureIndex, transparency) {
    if (transparency === void 0) { transparency = 1; }
    var key = "".concat(color.r, ",").concat(color.g, ",").concat(color.b, ",").concat(doubleSided, ",").concat(textureIndex != null ? textureIndex : -1, ",").concat(transparency);
    if (colorToMaterialIndex.has(key))
        return colorToMaterialIndex.get(key);
    var idx = gltfMaterials.length, pbr = { baseColorFactor: [color.r / 255, color.g / 255, color.b / 255, transparency], metallicFactor: 0, roughnessFactor: .8 };
    textureIndex !== null && (pbr.baseColorTexture = { index: textureIndex });
    var material = { pbrMetallicRoughness: pbr };
    return doubleSided && (material.doubleSided = !0), transparency < 1 ? material.alphaMode = "BLEND" : textureIndex !== null && (material.alphaMode = "MASK"), gltfMaterials.push(material), colorToMaterialIndex.set(key, idx), idx;
} var meshResources = [], resourceIdByKey = new Map; function resourceVariantKey(defId, inheritedMaterial, layer) { var tex = inheritedMaterial == null ? void 0 : inheritedMaterial.texture, texKey = tex && tex.data && tex.data.length > 0 ? "".concat(tex.data.length, ":").concat(Array.from(tex.data.subarray(0, 16)).join(","), ":").concat(tex.width, "x").concat(tex.height) : "-", matKey = inheritedMaterial ? "".concat(inheritedMaterial.name, "|").concat(inheritedMaterial.color.r, ",").concat(inheritedMaterial.color.g, ",").concat(inheritedMaterial.color.b, "|").concat(texKey) : "-", lc = getLayerColor(layer); return "".concat(String(defId), "|").concat(matKey, "|").concat(lc.r, ",").concat(lc.g, ",").concat(lc.b); } function meshResourceFor(defId, inheritedMaterial, layer) {
    var e_67, _j;
    var d = defsDict.get(defId);
    if (!d || d.builder.faces.size === 0)
        return;
    var key = resourceVariantKey(defId, inheritedMaterial, layer), hit = resourceIdByKey.get(key);
    if (hit !== void 0)
        return hit;
    var faceGroups = buildLocalFaceGroups(d.builder, { resolveMaterial: function (matId) { return resolveMaterialFromMaps(matId, materialIdToName, materialsMap, materialsByFolder); }, textureIndexFor: textureIndexFor, inheritedMaterial: inheritedMaterial, fallbackLayerColor: getLayerColor(layer), definitionId: defId, respectVisibility: options == null ? void 0 : options.respectEdgeVisibility }), primitives = [], scale = .0254;
    try {
        for (var _k = __values(faceGroups.values()), _l = _k.next(); !_l.done; _l = _k.next()) {
            var group = _l.value;
            if (group.localFaces.length === 0)
                continue;
            var positions = new Float32Array(group.localVerts.length * 3), normals = new Float32Array(group.localVerts.length * 3), uvs = new Float32Array(group.localVerts.length * 2);
            for (var i_53 = 0; i_53 < group.localVerts.length; i_53++) {
                var v = group.localVerts[i_53];
                positions[i_53 * 3] = v[0] * scale, positions[i_53 * 3 + 1] = v[2] * scale, positions[i_53 * 3 + 2] = -v[1] * scale, uvs[i_53 * 2] = group.localUvs[i_53][0], uvs[i_53 * 2 + 1] = group.localUvs[i_53][1];
                var rawNorm = group.normalsAccum[i_53], normLen = Math.sqrt(Math.pow(rawNorm[0], 2) + Math.pow(rawNorm[1], 2) + Math.pow(rawNorm[2], 2)), n = normLen > 1e-6 ? [rawNorm[0] / normLen, rawNorm[1] / normLen, rawNorm[2] / normLen] : [0, 0, 1];
                normals[i_53 * 3] = n[0], normals[i_53 * 3 + 1] = n[2], normals[i_53 * 3 + 2] = -n[1];
            }
            var indices = new Uint32Array(group.localFaces.length * 3);
            for (var i_54 = 0; i_54 < group.localFaces.length; i_54++)
                indices[i_54 * 3] = group.localFaces[i_54][0], indices[i_54 * 3 + 1] = group.localFaces[i_54][1], indices[i_54 * 3 + 2] = group.localFaces[i_54][2];
            primitives.push({ positions: positions, normals: normals, uvs: uvs, indices: indices, materialIndex: getMaterialIndex(group.color, group.doubleSided, group.textureIndex, group.transparency) });
        }
    }
    catch (e_67_1) { e_67 = { error: e_67_1 }; }
    finally {
        try {
            if (_l && !_l.done && (_j = _k.return)) _j.call(_k);
        }
        finally { if (e_67) throw e_67.error; }
    }
    if (primitives.length === 0)
        return;
    var id = "mesh_".concat(meshResources.length);
    return meshResources.push({ id: id, definitionId: defId, definitionName: d.name || "", variantKey: key, primitives: primitives }), resourceIdByKey.set(key, id), id;
} var activeDefinitions = new Set; function toGltfMatrix(m) { var _a2, _b2, _c; var a = m[0], b = m[1], c = m[2], d = m[3], e = m[4], f = m[5], g = m[6], h = m[7], i = m[8], tx = (_a2 = m[9]) != null ? _a2 : 0, ty = (_b2 = m[10]) != null ? _b2 : 0, tz = (_c = m[11]) != null ? _c : 0, r00 = a, r01 = c, r02 = -b, r10 = g, r11 = i, r12 = -h, r20 = -d, r21 = -f; return [r00, r10, r20, 0, r01, r11, r21, 0, r02, r12, e, 0, tx * .0254, tz * .0254, -ty * .0254, 1]; } var IDENTITY_GLTF = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]; function walk2(defId, currentMatrix, parentLayer, inheritedMaterial) {
    var e_68, _j, e_69, _k, e_70, _l;
    var _a2, _b2, _c, _d, _e;
    var d = defsDict.get(defId);
    if (!d)
        return [];
    var nodes = [];
    try {
        for (var _m = __values(d.builder.instances), _o = _m.next(); !_o.done; _o = _m.next()) {
            var inst = _o.value;
            var refIdx = inst.refIdx, newMatrix = multiplyMatrices(currentMatrix, inst.matrix), lName = parentLayer, instMaterial = inheritedMaterial, properties = __spreadValues({}, inst.properties || {});
            if (inst.layerId !== null && inst.layerId !== void 0 && (lName = layerIdToName.get(inst.layerId) || parentLayer), inst.materialId !== null && inst.materialId !== void 0) {
                var matName = materialIdToName.get(inst.materialId);
                if (matName) {
                    var mat = materialsMap.get(matName) || materialsByFolder.get(matName);
                    mat && (instMaterial = mat);
                }
            }
            var d007 = inst.children.find(function (c) { return c.tag === "D007"; }), attributeDicts = null;
            if (d007)
                try {
                    properties = extractDynamicProperties(d007, options), attributeDicts = extractAttributeDictionaries(d007, options);
                }
                catch (e) {
                    emitLog(options, "debug", "Failed to extract dynamic properties for instance ".concat((_a2 = inst.name) != null ? _a2 : "", " (refIdx=").concat(refIdx, "): ").concat(e.message));
                }
            if (instanceCounter.count++, instanceCounter.count % 500 === 0 && (emitProgress(options, "build_scene", instanceCounter.count, instanceCounter.count), emitLog(options, "debug", "Processed ".concat(instanceCounter.count, " placed instances"))), activeDefinitions.has(refIdx))
                throw new SkpParseError("Recursive component definition", { stage: "build_scene", definitionId: refIdx });
            activeDefinitions.add(refIdx);
            var children = walk2(refIdx, newMatrix, lName, instMaterial);
            activeDefinitions.delete(refIdx);
            var tx = ((_b2 = newMatrix[9]) != null ? _b2 : 0) * 25.4, ty = ((_c = newMatrix[10]) != null ? _c : 0) * 25.4, tz = ((_d = newMatrix[11]) != null ? _d : 0) * 25.4, childDefName = ((_e = defsDict.get(refIdx)) == null ? void 0 : _e.name) || "", defNameIsReal = !!childDefName && !isGenericDefinitionName(childDefName), nameOverride = findNameOverride(attributeDicts), instNameNonEmpty = !!inst.name, fallbackName = instNameNonEmpty ? inst.name : defNameIsReal ? childDefName : "Component_".concat(refIdx), displayName = nameOverride != null ? nameOverride : fallbackName, nameIsGenerated = nameOverride === null && !instNameNonEmpty && !defNameIsReal, attributeDictionaries = {};
            if (attributeDicts)
                try {
                    for (var _p = (e_69 = void 0, __values(Object.keys(attributeDicts))), _q = _p.next(); !_q.done; _q = _p.next()) {
                        var dictName = _q.value;
                        if (dictName === "dynamic_attributes" || dictName === "SU_InstanceSet")
                            continue;
                        var entries = attributeDicts[dictName], stringified = {};
                        try {
                            for (var _r = (e_70 = void 0, __values(Object.keys(entries))), _s = _r.next(); !_s.done; _s = _r.next()) {
                                var key = _s.value;
                                stringified[key] = stringifyVffAttrValue(entries[key]);
                            }
                        }
                        catch (e_70_1) { e_70 = { error: e_70_1 }; }
                        finally {
                            try {
                                if (_s && !_s.done && (_l = _r.return)) _l.call(_r);
                            }
                            finally { if (e_70) throw e_70.error; }
                        }
                        attributeDictionaries[dictName] = stringified;
                    }
                }
                catch (e_69_1) { e_69 = { error: e_69_1 }; }
                finally {
                    try {
                        if (_q && !_q.done && (_k = _p.return)) _k.call(_p);
                    }
                    finally { if (e_69) throw e_69.error; }
                }
            nodes.push({ name: displayName, nameIsGenerated: nameIsGenerated, definitionName: childDefName, layer: lName, matrix: toGltfMatrix(inst.matrix), positionMm: [Math.round(tx * 100) / 100, Math.round(ty * 100) / 100, Math.round(tz * 100) / 100], properties: properties, attributeDictionaries: attributeDictionaries, guid: inst.refGuid || "", meshResourceId: meshResourceFor(refIdx, instMaterial, lName), children: children });
        }
    }
    catch (e_68_1) { e_68 = { error: e_68_1 }; }
    finally {
        try {
            if (_o && !_o.done && (_j = _m.return)) _j.call(_m);
        }
        finally { if (e_68) throw e_68.error; }
    }
    return nodes;
} var rootChildren = walk2("ROOT", [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1], "Layer0", void 0), rootMeshResourceId = meshResourceFor("ROOT", void 0, "Layer0"), sceneHierarchy = { name: "ROOT", nameIsGenerated: !1, definitionName: "ROOT_MODEL", layer: "Layer0", matrix: __spreadArray([], __read(IDENTITY_GLTF), false), positionMm: [0, 0, 0], properties: {}, attributeDictionaries: {}, guid: "", meshResourceId: rootMeshResourceId, children: rootChildren }, bMin = [1 / 0, 1 / 0, 1 / 0], bMax = [-1 / 0, -1 / 0, -1 / 0], resourceById = new Map(meshResources.map(function (r) { return [r.id, r]; })), localBoxCache = new Map, localBox = function (id) {
    var e_71, _j;
    var cached = localBoxCache.get(id);
    if (cached !== void 0)
        return cached;
    var res = resourceById.get(id), box = null;
    if (res) {
        var lo = [1 / 0, 1 / 0, 1 / 0], hi = [-1 / 0, -1 / 0, -1 / 0];
        try {
            for (var _k = __values(res.primitives), _l = _k.next(); !_l.done; _l = _k.next()) {
                var prim = _l.value;
                for (var i_55 = 0; i_55 < prim.positions.length; i_55 += 3)
                    for (var k = 0; k < 3; k++) {
                        var v = prim.positions[i_55 + k];
                        v < lo[k] && (lo[k] = v), v > hi[k] && (hi[k] = v);
                    }
            }
        }
        catch (e_71_1) { e_71 = { error: e_71_1 }; }
        finally {
            try {
                if (_l && !_l.done && (_j = _k.return)) _j.call(_k);
            }
            finally { if (e_71) throw e_71.error; }
        }
        Number.isFinite(lo[0]) && (box = { min: lo, max: hi });
    }
    return localBoxCache.set(id, box), box;
}, mul4 = function (a, b) { var out = new Array(16).fill(0); for (var col = 0; col < 4; col++)
    for (var row = 0; row < 4; row++) {
        var acc = 0;
        for (var k = 0; k < 4; k++)
            acc += a[k * 4 + row] * b[col * 4 + k];
        out[col * 4 + row] = acc;
    } return out; }, accumulate = function (node, parent) {
    var e_72, _j;
    var world = mul4(parent, node.matrix);
    if (node.meshResourceId !== void 0) {
        var box = localBox(node.meshResourceId);
        if (box)
            for (var c = 0; c < 8; c++) {
                var x_4 = c & 1 ? box.max[0] : box.min[0], y = c & 2 ? box.max[1] : box.min[1], z = c & 4 ? box.max[2] : box.min[2], wx = world[0] * x_4 + world[4] * y + world[8] * z + world[12], wy = world[1] * x_4 + world[5] * y + world[9] * z + world[13], wz = world[2] * x_4 + world[6] * y + world[10] * z + world[14];
                wx < bMin[0] && (bMin[0] = wx), wy < bMin[1] && (bMin[1] = wy), wz < bMin[2] && (bMin[2] = wz), wx > bMax[0] && (bMax[0] = wx), wy > bMax[1] && (bMax[1] = wy), wz > bMax[2] && (bMax[2] = wz);
            }
    }
    try {
        for (var _k = __values(node.children), _l = _k.next(); !_l.done; _l = _k.next()) {
            var child = _l.value;
            accumulate(child, world);
        }
    }
    catch (e_72_1) { e_72 = { error: e_72_1 }; }
    finally {
        try {
            if (_l && !_l.done && (_j = _k.return)) _j.call(_k);
        }
        finally { if (e_72) throw e_72.error; }
    }
}; accumulate(sceneHierarchy, __spreadArray([], __read(IDENTITY_GLTF), false)); var bounds = Number.isFinite(bMin[0]) ? { min: [bMin[0], bMin[1], bMin[2]], max: [bMax[0], bMax[1], bMax[2]], size: [bMax[0] - bMin[0], bMax[1] - bMin[1], bMax[2] - bMin[2]], center: [(bMin[0] + bMax[0]) / 2, (bMin[1] + bMax[1]) / 2, (bMin[2] + bMax[2]) / 2] } : null; return emitLog(options, "info", "Instanced scene build complete: ".concat(instanceCounter.count, " instances, ").concat(meshResources.length, " mesh resources (").concat(((Date.now() - t0) / 1e3).toFixed(2), "s)")), { sceneHierarchy: sceneHierarchy, meshResources: meshResources, gltfMaterials: gltfMaterials, textures: textures, bounds: bounds, layerHidden: Object.fromEntries(layerHidden) }; } var int32 = new Int32Array(2), float32 = new Float32Array(int32.buffer), float64 = new Float64Array(int32.buffer), isLittleEndian = new Uint16Array(new Uint8Array([1, 0]).buffer)[0] === 1; var Encoding; (function (Encoding2) { Encoding2[Encoding2.UTF8_BYTES = 1] = "UTF8_BYTES", Encoding2[Encoding2.UTF16_STRING = 2] = "UTF16_STRING"; })(Encoding || (Encoding = {})); var SUPPORTED_REPRESENTATION_CLASSES = new Set([1]); function hexToBytes(hex) { var out = []; for (var i_56 = 0; i_56 < hex.length; i_56 += 2)
    out.push(parseInt(hex.slice(i_56, i_56 + 2), 16)); return out; } var ISO_CAMERA_PREFIX_PATCH = hexToBytes("594000000000000059c000000000000059400000000000000000000000000000000000000000000000003f2c0c70bd20dabf3f2c0c70bd20da3f3f2c0c70bd20ea3f000000000000f03f0000000000408f40000000000000003e402adf272c803457"), ISO_CAMERA_TAIL_PATCHES = [[509, hexToBytes("d0a869613c442d4799a4667d1adfa836")], [1390, hexToBytes("4e53c84477029246bba95827bba7e2")]]; var _TEXTURE_H_SENTINEL = hexToBytes("f0ffffffffffff0f"); var DIM_FONT_PAYLOAD = hexToBytes("000000fffeff065400610068006f006d00610000000800000000ecf57abd5eaf2340"), TEXT_DELIM = hexToBytes("0100000001000300000001"); var CAMERA_TEMPLATE = hexToBytes("00000000000000000000000000000000000000000000f03f000000000000000000000000000000000000000000000000004000000000000000000000000000f03f0000000000000000000000000000000000000000000000000100000000003e40000000000000f03f00000000000000000000000000000000000000000000000000000000000000000100fffeff00000000000000000000000000000000f03f00000000000000000000000000000000"); function parseToRaw(buffer, options) {
    var e_73, _j, e_74, _k, e_75, _l;
    var t0 = Date.now(), data = new Uint8Array(buffer);
    if (emitLog(options, "info", "Parsing buffer (".concat(data.length, " bytes)")), !(data.length >= 4 && data[0] === 255 && data[1] === 254 && data[2] === 255 && data[3] === 14))
        throw new SkpParseError("Not a valid SketchUp file (bad header magic)", { stage: "header" });
    if (isLegacy(data))
        return emitLog(options, "debug", "Detected legacy MFC container; routing to legacy walker"), parseLegacyToRaw(data, options);
    var contents;
    try {
        contents = extractSkpContents(data, options);
    }
    catch (e) {
        throw new SkpParseError("Failed to extract SKP contents: ".concat(e.message), { stage: "zip_extract", cause: e });
    }
    var version = contents.version, modelData = contents.modelData, materialFiles = contents.materialFiles;
    emitLog(options, "debug", "Detected version ".concat(version, " (VFF/ZIP container)"));
    var units = contents.metaData ? readMetaUnits(contents.metaData) : null, layerColors = new Map, layerHidden = new Map, materialsMap = new Map, materialsByFolder = new Map;
    try {
        for (var _m = __values(Object.entries(materialFiles)), _o = _m.next(); !_o.done; _o = _m.next()) {
            var _p = __read(_o.value, 2), name = _p[0], xmlBytes = _p[1];
            var lowerName = name.toLowerCase();
            if (lowerName.endsWith("material.xml") && lowerName.startsWith("materials/"))
                try {
                    var xmlText = new TextDecoder("utf-8").decode(xmlBytes), parsedMat = parseMaterialXml(xmlText);
                    if (parsedMat) {
                        var folderName = name.split("/")[1] || "", texture = null;
                        if (parsedMat.hasTexture) {
                            var resolved = resolveTextureBytes(materialFiles, name, parsedMat.textureFilename, parsedMat.imagePath);
                            texture = { filename: resolved.filename, width: parsedMat.xScale, height: parsedMat.yScale, data: resolved.data };
                        }
                        var matObj = { name: parsedMat.name, color: { r: parsedMat.r, g: parsedMat.g, b: parsedMat.b, a: 255 }, transparency: parsedMat.trans, id: null, texture: texture, colorized: parsedMat.colorized, colorizeType: parsedMat.colorizeType };
                        materialsMap.set(parsedMat.name, matObj), folderName && materialsByFolder.set(folderName, matObj), parsedMat.name.startsWith("Layer_") && (layerColors.set(parsedMat.name.slice(6), [parsedMat.r, parsedMat.g, parsedMat.b]), layerHidden.set(parsedMat.name.slice(6), !1));
                    }
                }
                catch (e) {
                    emitLog(options, "debug", "Failed to parse material.xml ".concat(name, ": ").concat(e.message));
                }
        }
    }
    catch (e_73_1) { e_73 = { error: e_73_1 }; }
    finally {
        try {
            if (_o && !_o.done && (_j = _m.return)) _j.call(_m);
        }
        finally { if (e_73) throw e_73.error; }
    }
    var styles = [];
    try {
        for (var _q = __values(Object.entries(materialFiles)), _r = _q.next(); !_r.done; _r = _q.next()) {
            var _s = __read(_r.value, 2), name = _s[0], xmlBytes = _s[1];
            var lowerName = name.toLowerCase();
            if (lowerName.startsWith("styles/") && lowerName.endsWith("style.xml"))
                try {
                    var xmlText = new TextDecoder("utf-8").decode(xmlBytes), parsedStyle = parseStyleXml(xmlText);
                    parsedStyle && styles.push({ name: parsedStyle.name, frontColor: parsedStyle.frontColor, backColor: parsedStyle.backColor });
                }
                catch (e) {
                    emitLog(options, "debug", "Failed to parse style.xml ".concat(name, ": ").concat(e.message));
                }
        }
    }
    catch (e_74_1) { e_74 = { error: e_74_1 }; }
    finally {
        try {
            if (_r && !_r.done && (_k = _q.return)) _k.call(_q);
        }
        finally { if (e_74) throw e_74.error; }
    }
    var layerIdToName = new Map, materialIdToName = new Map;
    function collectMaterialIds(nodes) {
        var e_76, _j;
        try {
            for (var nodes_9 = __values(nodes), nodes_9_1 = nodes_9.next(); !nodes_9_1.done; nodes_9_1 = nodes_9.next()) {
                var el = nodes_9_1.value;
                if (el.tag === "C832") {
                    var dc05 = findChildTag(el.children, "DC05"), nameNode = findChildTag(el.children, "CC32");
                    if (dc05 && nameNode) {
                        var payload = dc05.payload, mId = void 0;
                        if (payload.length >= 6 && payload[0] === 222 && payload[1] === 5) {
                            var de05Len = readU32(payload, 2);
                            mId = parseVarInt(payload, 6, de05Len);
                        }
                        else
                            mId = parseVarInt(payload, 0, payload.length);
                        var mName = "";
                        try {
                            mName = new TextDecoder("utf-8").decode(nameNode.payload);
                        }
                        catch (e) {
                            emitLog(options, "debug", "Failed to decode material name for id ".concat(mId, ": ").concat(e.message));
                        }
                        materialIdToName.set(mId, mName);
                    }
                }
                el.children && el.children.length > 0 && collectMaterialIds(el.children);
            }
        }
        catch (e_76_1) { e_76 = { error: e_76_1 }; }
        finally {
            try {
                if (nodes_9_1 && !nodes_9_1.done && (_j = nodes_9.return)) _j.call(nodes_9);
            }
            finally { if (e_76) throw e_76.error; }
        }
    }
    emitLog(options, "debug", "Parsed ".concat(materialsMap.size, " materials, ").concat(styles.length, " styles"));
    var defsDict = new Map, rootBuilder = new GeometryBuilder, vertexPositions = new Map, instanceWorld = new Map, pageNode = null;
    try {
        for (var _t = __values(iterTopLevelLazy(modelData, 0, modelData.length)), _u = _t.next(); !_u.done; _u = _t.next()) {
            var _v = _u.value, index = _v.index, total = _v.total, el = _v.node;
            try {
                collectLayers([el], layerIdToName, options, layerHidden), collectMaterialIds([el]), collectDefs([el], defsDict, options), scanVertexPositions(el, vertexPositions), scanInstanceTransforms(el, instanceWorld), pageNode === null && (pageNode = findPageNode(el)), el.tag === "F601" && extractGeometryFromNodes(el.children, rootBuilder, options);
            }
            catch (e) {
                throw new SkpParseError("Failed while processing top-level record: ".concat(e.message), { stage: "tlv_walk", recordIndex: index, totalRecords: total, tag: el.tag, cause: e });
            }
            (index % 500 === 0 || index === total - 1) && (emitProgress(options, "tlv_walk", index + 1, total), emitLog(options, "debug", "Processed ".concat(index + 1, "/").concat(total, " top-level records")));
        }
    }
    catch (e_75_1) { e_75 = { error: e_75_1 }; }
    finally {
        try {
            if (_u && !_u.done && (_l = _t.return)) _l.call(_t);
        }
        finally { if (e_75) throw e_75.error; }
    }
    return emitLog(options, "info", "Parse complete: ".concat(defsDict.size, " defs (").concat(((Date.now() - t0) / 1e3).toFixed(2), "s)")), layerIdToName.has(1) || layerIdToName.set(1, "Layer0"), layerColors.has("Layer0") || layerColors.set("Layer0", [136, 136, 136]), layerHidden.has("Layer0") || layerHidden.set("Layer0", !1), defsDict.set("ROOT", { guid: "ROOT", name: "ROOT_MODEL", isImage: !1, alwaysFacesCamera: !1, shadowsFaceSun: !1, builder: rootBuilder }), { version: version, units: units, layerColors: layerColors, layerHidden: layerHidden, layerIdToName: layerIdToName, pages: parsePages(pageNode), dimensions: parseDimensions(modelData, vertexPositions, instanceWorld), materialIdToName: materialIdToName, materialsMap: materialsMap, materialsByFolder: materialsByFolder, styles: styles, defsDict: defsDict };
} function parseSkp(buffer, options) { return buildModelFromParsed(parseToRaw(buffer, options)); } function buildScene(buffer, options) { return buildSceneFromParsed(parseToRaw(buffer, options), options); } function buildInstancedScene(buffer, options) { return buildInstancedSceneFromParsed(parseToRaw(buffer, options), options); } return __toCommonJS(entry_exports); })();

return OpenSkp;
})();
