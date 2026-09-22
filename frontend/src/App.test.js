import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the application navigation', () => {
  render(<App />);

  expect(
    screen.getByRole('link', { name: /generador/i })
  ).toBeInTheDocument();

  expect(
    screen.getByRole('link', { name: /historial/i })
  ).toBeInTheDocument();

  expect(
    screen.getByRole('link', { name: /dashboard/i })
  ).toBeInTheDocument();
});
