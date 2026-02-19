/**
 * Calendar API Endpoints
 * CRUD for calendar events
 */

import { apiClient } from '../client';
import type {
  CalendarEvent,
  CalendarEventsResponse,
  EventCreateRequest,
  EventUpdateRequest,
} from '../types/calendar-types';

export const calendarApi = {
  list: async (start: string, end: string): Promise<CalendarEvent[]> => {
    const response = await apiClient.get<CalendarEventsResponse>('/calendar', {
      params: { start, end },
    });
    return response.data.events;
  },

  upcoming: async (days = 7, limit = 10): Promise<CalendarEvent[]> => {
    const response = await apiClient.get<CalendarEventsResponse>('/calendar/upcoming', {
      params: { days, limit },
    });
    return response.data.events;
  },

  create: async (data: EventCreateRequest): Promise<CalendarEvent> => {
    const response = await apiClient.post('/calendar', data);
    return response.data.event;
  },

  update: async (eventId: string, data: EventUpdateRequest): Promise<CalendarEvent> => {
    const response = await apiClient.patch(`/calendar/${eventId}`, data);
    return response.data.event;
  },

  remove: async (eventId: string): Promise<void> => {
    await apiClient.delete(`/calendar/${eventId}`);
  },
};
