import test from 'node:test';import assert from 'node:assert/strict';import {filterRows,csv,quantile,comparison} from '../web/shared.mjs';
test('filters preserve missing values and allow exact multi-value facets',()=>{const r=[{id:'a',tags:['BC','NS'],amount:0},{id:'b',tags:['BC'],amount:null}];assert.equal(filterRows(r,{facets:{tags:'NS'}}).length,1);assert.deepEqual(filterRows(r,{min:'0'}).map(r=>r.id),['a']);});
test('CSV escapes fields and neutralizes spreadsheet expressions',()=>{const out=csv([{name:'=SUM(1,2)',amount:-3}],[{key:'name',label:'Name'},{key:'amount',label:'Amount'}]);assert.match(out,/"'=SUM/);assert.match(out,/"-3"/);});
test('quantiles never treat missing readings as zero',()=>{assert.equal(quantile([null,10,20],.5),15);assert.equal(quantile([], .9),null);});
test('comparison keys separate changes from additions/removals',()=>{assert.deepEqual(comparison([{id:'a',n:1},{id:'b'}],[{id:'a',n:2},{id:'c'}]),{added:['c'],removed:['b'],changed:['a']});});
