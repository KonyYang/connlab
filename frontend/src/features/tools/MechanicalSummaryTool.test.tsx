import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { MechanicalSummaryTool } from './MechanicalSummaryTool';

vi.mock('../../api/mechanicalSummary', () => ({
  previewMechanicalSource: vi.fn().mockResolvedValue({
    sha256: 'abc', requires_review: true,
    rows: [{ curve: '1.20', sample: '', value: 241.07 }],
  }),
  generateMechanicalSummary: vi.fn(),
}));

describe('Mechanical Summary', () => {
  it('requires a reviewed sample before allowing generation', async () => {
    const user = userEvent.setup();
    render(<MechanicalSummaryTool />);
    await user.upload(screen.getByLabelText('Select mechanical test files'),
      new File(['test'], 'hold.pdf', { type: 'application/pdf' }));
    await user.selectOptions(screen.getByLabelText('Test type for hold.pdf'), 'hold');
    await user.click(screen.getByRole('button', { name: 'Preview hold.pdf' }));
    expect(await screen.findByDisplayValue('1.20')).toBeTruthy();
    expect((screen.getByRole('button', { name: 'Generate Summary' }) as HTMLButtonElement).disabled).toBe(true);
    await user.type(screen.getByLabelText('Sample for curve 1.20'), 'SN-3');
    await user.click(screen.getByLabelText('Confirm hold.pdf'));
    expect((screen.getByRole('button', { name: 'Generate Summary' }) as HTMLButtonElement).disabled).toBe(false);
  });
});
