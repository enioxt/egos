import { describe, expect, test } from 'bun:test';
import { parseOpenTaskIds } from '../pr-pack';

describe('parseOpenTaskIds', () => {
  test('collects open task lines from multiple prefixes', () => {
    const content = [
      '- [ ] EGOS-163: Pix billing integration',
      '- [ ] GH-034: P0 urgent harness evaluation',
      '- [ ] OBS-010: Wire hooks to OTel spans',
      '- [ ] EGOS-TELEM-001: Agent execution telemetry',
    ].join('\n');

    const result = parseOpenTaskIds(content, 10);
    expect(result).toEqual([
      'EGOS-163: Pix billing integration',
      'GH-034: P0 urgent harness evaluation',
      'OBS-010: Wire hooks to OTel spans',
      'EGOS-TELEM-001: Agent execution telemetry',
    ]);
  });

  test('deduplicates repeated task ids and obeys limit', () => {
    const content = [
      '- [ ] GH-025: first',
      '- [ ] GH-025: duplicate',
      '- [ ] LEAK-010: monitor',
    ].join('\n');

    const result = parseOpenTaskIds(content, 2);
    expect(result).toEqual([
      'GH-025: first',
      'LEAK-010: monitor',
    ]);
  });
});
