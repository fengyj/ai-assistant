import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Input from '../components/ui/Input';

describe('Input', () => {
  it('renders input element', () => {
    render(<Input value="test" onChange={() => {}} />);
    expect(screen.getByDisplayValue('test')).toBeInTheDocument();
  });
});
