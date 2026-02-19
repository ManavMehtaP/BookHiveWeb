-- Add end_time column to events table
ALTER TABLE events ADD COLUMN event_end_time TIME AFTER event_time;
