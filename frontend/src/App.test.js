import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

jest.mock('./services/api', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn(), eject: jest.fn() },
      response: { use: jest.fn(), eject: jest.fn() },
    },
  },
}));

test('renders the application navigation', () => {
  // Mock sessionStorage so App renders the authenticated routes
  jest.spyOn(window.sessionStorage.__proto__, 'getItem').mockImplementation((key) => {
    if (key === 'isAuthenticated') return 'true';
    return null;
  });

  render(<App />);

  const menuButton = screen.getByRole('button', { name: /menú de herramientas/i });
  fireEvent.click(menuButton);

  expect(
    screen.getByRole('link', { name: /gestión de expedientes/i })
  ).toBeInTheDocument();

  expect(
    screen.getByRole('link', { name: /historial/i })
  ).toBeInTheDocument();

  expect(
    screen.getByRole('link', { name: /dashboard/i })
  ).toBeInTheDocument();
});
