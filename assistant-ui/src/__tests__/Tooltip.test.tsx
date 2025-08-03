import { render, screen } from '@testing-library/react';
import Tooltip from '../components/ui/Tooltip';

describe('Tooltip', () => {
  it('renders tooltip text', () => {
render(<Tooltip content="tip"><span>Hover me</span></Tooltip>);
    expect(screen.getByText('tip')).toBeInTheDocument();
  });
});
