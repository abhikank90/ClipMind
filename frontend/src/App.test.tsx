import { render, screen } from '@testing-library/react';
import App from './App';

test('renders ClipMind header', () => {
  render(<App />);
  const headerElement = screen.getByText(/ClipMind/i);
  expect(headerElement).toBeInTheDocument();
});
