import { useState } from 'react';

export function usePasswordToggle() {
  const [visible, setVisible] = useState(false);

  const toggleVisibility = () => setVisible((prev) => !prev);

  return {
    type: visible ? 'text' : 'password',
    visible,
    toggleVisibility,
  };
}