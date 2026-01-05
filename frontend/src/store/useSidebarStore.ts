/**
 * Sidebar Store - Manages mobile sidebar open/close state
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface SidebarState {
  isOpen: boolean;
  toggle: () => void;
  open: () => void;
  close: () => void;
}

export const useSidebarStore = create<SidebarState>()(
  devtools(
    (set) => ({
      isOpen: false,
      toggle: () => set((state) => ({ isOpen: !state.isOpen })),
      open: () => set({ isOpen: true }),
      close: () => set({ isOpen: false }),
    }),
    { name: 'SidebarStore' }
  )
);
