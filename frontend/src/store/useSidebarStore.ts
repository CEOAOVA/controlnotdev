/**
 * Sidebar Store - Manages mobile sidebar open/close state
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface SidebarState {
  isOpen: boolean;
  isCollapsed: boolean;
  toggle: () => void;
  open: () => void;
  close: () => void;
  toggleCollapse: () => void;
}

export const useSidebarStore = create<SidebarState>()(
  devtools(
    (set) => ({
      isOpen: false,
      isCollapsed: false,
      toggle: () => set((state) => ({ isOpen: !state.isOpen })),
      open: () => set({ isOpen: true }),
      close: () => set({ isOpen: false }),
      toggleCollapse: () => set((state) => ({ isCollapsed: !state.isCollapsed })),
    }),
    { name: 'SidebarStore' }
  )
);
