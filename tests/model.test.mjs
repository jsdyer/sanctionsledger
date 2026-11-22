import test from 'node:test';import assert from 'node:assert/strict';
import {analyse} from '../web/model.mjs';
test('source update date is independent of capture date',()=>{const a=analyse([{regime:'R',kind:'individual',listed_year:'2020'}],{},{source_updated:'2026-01-01',captured_at:'2026-02-01'});assert.equal(a.metrics[3].value,'2026-01-01');});
