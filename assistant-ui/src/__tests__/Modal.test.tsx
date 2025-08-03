import { render, screen } from '@testing-library/react';
import Modal from '../components/ui/Modal';

describe('Modal', () => {
  it('renders modal content', () => {
render(<Modal isOpen={true} onClose={() => {}}><div>Modal Content</div></Modal>);
    expect(screen.getByText('Modal Content')).toBeInTheDocument();
  });
});
